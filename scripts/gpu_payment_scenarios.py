"""QA opcional em GPU AMD/OpenGL: valida cenários temporais sintéticos em lote.

Executar fora da aplicação, em desenvolvimento, com numpy + moderngl.
Sem dados pessoais, modelos de IA, conexão bancária ou alteração do banco.
"""
from __future__ import annotations
import argparse
import time
import numpy as np
import moderngl

SHADER = """
#version 430
layout(local_size_x = 256) in;
layout(std430, binding = 0) readonly buffer InputTimes { ivec4 events[]; };
layout(std430, binding = 1) writeonly buffer Results { int minutes[]; };
uniform int count;
void main() {
    uint i = gl_GlobalInvocationID.x;
    if (i >= uint(count)) return;
    ivec4 t = events[i];
    bool ordered = (t.x < t.y && t.y < t.z && t.z < t.w);
    bool bounded = (t.x >= 0 && t.w <= 1439);
    minutes[i] = ordered && bounded ? (t.y - t.x) + (t.w - t.z) : -1;
}
"""


def run(n: int, seed: int = 337) -> dict:
    if not 1 <= n <= 1_000_000:
        raise ValueError("Escolha entre 1 e 1000000 cenários.")
    ctx = moderngl.create_standalone_context(require=430, backend="egl")
    renderer = ctx.info.get("GL_RENDERER", "")
    if "llvmpipe" in renderer.lower() or "softpipe" in renderer.lower():
        raise RuntimeError("Renderização de software não é teste de GPU.")
    rng = np.random.default_rng(seed)
    values = rng.integers(0, 1440, (n, 4), dtype=np.int32)
    # Metade é válida (ordenação crescente) e o restante contém casos inválidos.
    values[: n // 2].sort(axis=1)
    begin_cpu = time.perf_counter()
    a, b, c, d = values.T
    expected = np.where(
        (a < b) & (b < c) & (c < d),
        (b - a) + (d - c),
        -1,
    ).astype("i4")
    cpu_ms = (time.perf_counter() - begin_cpu) * 1000

    shader = ctx.compute_shader(SHADER)
    in_buf = ctx.buffer(values.tobytes())
    out_buf = ctx.buffer(reserve=n * 4)
    in_buf.bind_to_storage_buffer(0)
    out_buf.bind_to_storage_buffer(1)
    shader["count"].value = n
    begin_gpu = time.perf_counter()
    shader.run(group_x=(n + 255) // 256)
    ctx.finish()
    actual = np.frombuffer(out_buf.read(), dtype=np.int32)
    gpu_ms = (time.perf_counter() - begin_gpu) * 1000
    mismatches = int(np.count_nonzero(actual != expected))
    if mismatches:
        raise AssertionError(f"Divergências GPU vs referência NumPy: {mismatches}")
    # Referência sequencial Python: aprox. o custo da validação escalar usada
    # pelo servidor, mantendo o resultado vetorial 100% independente.
    scalar_start = time.perf_counter()
    scalar = [
        (b - a) + (d - c) if 0 <= a < b < c < d <= 1439 else -1
        for a, b, c, d in values.tolist()
    ]
    scalar_ms = (time.perf_counter() - scalar_start) * 1000
    if not np.array_equal(actual, np.asarray(scalar, dtype=np.int32)):
        raise AssertionError("Divergência GPU vs referência Python escalar.")
    in_buf.release()
    out_buf.release()
    ctx.release()
    return {
        "gpu": renderer,
        "scenarios": n,
        "mismatches": mismatches,
        "cpu_numpy_ms": round(cpu_ms, 2),
        "cpu_scalar_python_ms": round(scalar_ms, 2),
        "gpu_dispatch_read_ms": round(gpu_ms, 2),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=int, default=262144)
    args = parser.parse_args()
    print(run(args.scenarios))
