#!/usr/bin/env python3
"""Telemetria leve GPU/CPU/RAM durante baterias locais; sem coleta de PII."""
import argparse,csv,time,os
from pathlib import Path

def readint(path):
    try:return int(Path(path).read_text().strip())
    except (OSError,ValueError):return None
def cpustat():
    vals=Path('/proc/stat').read_text().splitlines()[0].split()[1:]
    nums=list(map(int, vals))
    return sum(nums), nums[3]+(nums[4] if len(nums)>4 else 0)
def mem():
    text=Path('/proc/meminfo').read_text()
    d={}
    for line in text.splitlines():
        key,_,value=line.partition(':')
        if key in ('MemTotal','MemAvailable'):
            d[key]=int(value.strip().split()[0])
    return d
def run():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seconds',type=float,default=28)
    ap.add_argument('--interval',type=float,default=.2)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    os.makedirs(os.path.dirname(args.output),exist_ok=True)
    g='/sys/class/drm/card1/device'
    prev=cpustat()
    start=time.monotonic()
    rows=0
    with open(args.output,'w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(('elapsed_seconds','cpu_percent','ram_used_mb','gpu_busy_percent','vram_used_mb','gpu_temp_c'))
        while time.monotonic()-start<args.seconds:
            now=cpustat()
            dt=now[0]-prev[0];di=now[1]-prev[1];prev=now
            ram=mem()
            values=(
                round(time.monotonic()-start,3),
                round(100*(dt-di)/dt,2) if dt else 0,
                round((ram.get('MemTotal',0)-ram.get('MemAvailable',0))/1024,1),
                readint(g+'/gpu_busy_percent'),
                round((readint(g+'/mem_info_vram_used') or 0)/(1024*1024),1),
                (lambda x:round(x/1000,1) if x is not None else None)(
                    readint(g+'/hwmon/hwmon1/temp1_input')),
            )
            writer.writerow(values);rows+=1;f.flush()
            time.sleep(max(.05,args.interval))
    print('TELEMETRY_ROWS',rows,'PATH',args.output)
if __name__=='__main__':run()
