#!/usr/bin/env python3
"""Teste de estresse do contrato de campos do Potiguar em GPU Vulkan, sem dados pessoais.
Executar com Python que contenha numpy, wgpu e psutil; nao chama provedores externos.
"""
import importlib.util
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np
import psutil
import wgpu

ROOT = Path(__file__).resolve().parents[1]
N = int(os.environ.get("POTIGUAR_GPU_CASES", "1048576"))
ROUNDS = int(os.environ.get("POTIGUAR_GPU_ROUNDS", "48"))
SEED = 20261113

def get_contract():
    js = "console.log(JSON.stringify(require('./static/admin-onboarding-controller.js').SAFE))"
    allowed = json.loads(subprocess.check_output(["node", "-e", js], cwd=ROOT, text=True))
    spec = importlib.util.spec_from_file_location("potiguar_onboarding_fields_bench", ROOT / "app" / "onboarding_fields.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    names = list(module.FIELD_MAP.keys()) + ["unknown_or_injected_field"]
    matrix = np.zeros((8, len(names)), dtype=np.uint32)
    for step, step_names in allowed.items():
        for name in step_names:
            matrix[int(step), names.index(name)] = 1
    return names, matrix

def read_gpu():
    base = Path("/sys/class/drm/card1/device")
    hwmon = sorted((base / "hwmon").glob("hwmon*/temp1_input")) if (base / "hwmon").exists() else []
    values = {}
    for label, file in {
        "gpu_busy_percent": base / "gpu_busy_percent",
        "vram_used_bytes": base / "mem_info_vram_used",
        "vram_total_bytes": base / "mem_info_vram_total",
        "temperature_millicelsius": hwmon[0] if hwmon else Path("/nonexistent"),
    }.items():
        try:
            values[label] = int(file.read_text().strip())
        except (OSError, ValueError):
            pass
    return values

def main():
    if N < 1024 or N > 4194304 or ROUNDS < 1 or ROUNDS > 200:
        raise ValueError("Limites de carga incorretos")
    names, allow = get_contract()
    name_id = names.index("full_name")
    rng = np.random.default_rng(SEED)
    # step, field, comprimento sintetico, flags: bit 0=checkbox, 1=disabled,
    # 2=HTML/controle, 3=opcao de select invalida. Zero representa controle valido.
    cases = np.empty((N, 4), dtype=np.uint32)
    cases[:, 0] = rng.integers(0, 8, N, dtype=np.uint32)
    cases[:, 1] = rng.integers(0, len(names), N, dtype=np.uint32)
    cases[:, 2] = rng.integers(0, 145, N, dtype=np.uint32)
    cases[:, 3] = rng.choice(np.array([0, 0, 0, 0, 1, 2, 4, 8, 15], dtype=np.uint32), size=N)
    # Positivos e negativos exercitados explicitamente, nao somente amostragem aleatoria.
    positives = 0
    for step in range(8):
        for idx, allowed in enumerate(allow[step]):
            if not allowed:
                continue
            cases[positives] = (step, idx, 18, 0)
            positives += 1
    expected = (allow[cases[:, 0], cases[:, 1]] != 0) & (cases[:, 2] > 0) & (cases[:, 2] <= 120) & (cases[:, 3] == 0)
    expected &= (cases[:, 1] != name_id) | (cases[:, 2] >= 3)
    adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
    if adapter is None or adapter.info["backend_type"] != "Vulkan" or "RX 580" not in adapter.info["device"]:
        raise RuntimeError("GPU fisica RX 580 via Vulkan indisponivel; nao usar CPU silenciosamente")
    device = adapter.request_device_sync()
    nfields = len(names)
    shader = device.create_shader_module(code=f"""
struct Buffer {{ data: array<u32> }};
@group(0) @binding(0) var<storage, read> scenarios: Buffer;
@group(0) @binding(1) var<storage, read> allowed: Buffer;
@group(0) @binding(2) var<storage, read_write> verdicts: Buffer;
@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) id: vec3<u32>) {{
  let index = id.x;
  if (index >= {N}u) {{ return; }}
  let offset = index * 4u;
  let step = scenarios.data[offset];
  let field = scenarios.data[offset + 1u];
  let length = scenarios.data[offset + 2u];
  let flags = scenarios.data[offset + 3u];
  let on_allowlist = allowed.data[step * {nfields}u + field] == 1u;
  let valid = on_allowlist && length > 0u && length <= 120u
    && flags == 0u && (field != {name_id}u || length >= 3u);
  verdicts.data[index] = select(0u, 1u, valid);
}}""")
    src = device.create_buffer_with_data(data=cases.tobytes(), usage=wgpu.BufferUsage.STORAGE)
    mask = device.create_buffer_with_data(data=allow.tobytes(), usage=wgpu.BufferUsage.STORAGE)
    dst = device.create_buffer(size=N * 4, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_SRC)
    pipeline = device.create_compute_pipeline(layout="auto", compute={"module": shader, "entry_point": "main"})
    bind = device.create_bind_group(layout=pipeline.get_bind_group_layout(0), entries=[
        {"binding": 0, "resource": {"buffer": src}},
        {"binding": 1, "resource": {"buffer": mask}},
        {"binding": 2, "resource": {"buffer": dst}},
    ])
    telemetry = []
    running = threading.Event()
    running.set()
    def watch():
        while running.is_set():
            telemetry.append({"t": time.time(), **read_gpu(),
                "cpu_percent": psutil.cpu_percent(interval=None),
                "ram_used_bytes": psutil.virtual_memory().used})
            time.sleep(0.1)
    watcher = threading.Thread(target=watch, daemon=True)
    watcher.start()
    baseline = read_gpu()
    t0 = time.monotonic()
    encoder = device.create_command_encoder()
    work = encoder.begin_compute_pass()
    work.set_pipeline(pipeline)
    work.set_bind_group(0, bind, [], 0, 0)
    for _ in range(ROUNDS):
        work.dispatch_workgroups((N + 255) // 256)
    work.end()
    device.queue.submit([encoder.finish()])
    result = np.frombuffer(device.queue.read_buffer(dst).tobytes(), dtype=np.uint32)
    duration = time.monotonic() - t0
    running.clear()
    watcher.join(timeout=1)
    mismatches = int(np.count_nonzero(result != expected.astype(np.uint32)))
    safe_count = int(np.count_nonzero(result))
    output = {
        "status": "PASS" if mismatches == 0 else "FAIL",
        "device": adapter.info["device"],
        "backend": adapter.info["backend_type"],
        "driver": adapter.info["description"],
        "seed": SEED, "fields": len(names), "steps": 8,
        "scenario_samples": N, "distinct_input_patterns": int(np.unique((cases[:, 0].astype(np.uint64) << 32) | (cases[:, 1].astype(np.uint64) << 24) | (cases[:, 2].astype(np.uint64) << 16) | cases[:, 3].astype(np.uint64)).size),
        "gpu_dispatches": ROUNDS,
        "gpu_rule_evaluations": N * ROUNDS, "explicit_safe_cases": positives,
        "approved_cases": safe_count, "denied_cases": N - safe_count,
        "cpu_gpu_mismatches": mismatches, "elapsed_s": round(duration, 3),
        "samples": len(telemetry),
        "max_gpu_busy_percent": max((s.get("gpu_busy_percent", 0) for s in telemetry), default=None),
        "max_vram_used_mib": round(max((s.get("vram_used_bytes", 0) for s in telemetry), default=0) / 1048576, 1),
        "max_cpu_percent": max((s.get("cpu_percent", 0) for s in telemetry), default=None),
        "max_ram_used_gib": round(max((s.get("ram_used_bytes", 0) for s in telemetry), default=0) / 1073741824, 2),
        "max_gpu_temperature_c": (max([s["temperature_millicelsius"] for s in telemetry if "temperature_millicelsius" in s]) / 1000
            if any("temperature_millicelsius" in s for s in telemetry) else None),
        "baseline": baseline, "final": read_gpu(),
        "scope": "Synthetic numeric contract-gate stress test; does NOT test Gemini inference or microphone",
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    report = Path(os.environ.get("POTIGUAR_GPU_REPORT", "/tmp/potiguar-gpu-stress-20261113.json"))
    report.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    if mismatches:
        raise AssertionError(f"GPU x CPU divergiram em {mismatches} decisoes")

if __name__ == "__main__":
    main()
