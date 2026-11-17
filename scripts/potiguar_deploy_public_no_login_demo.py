#!/usr/bin/env python3
"""Implanta somente a demonstração descartável em porta loopback própria.
Publicação externa é feita por tunnel Cloudflare separado.
Credenciais de serviço jamais são incluídas em logs nem argumentos processuais.
"""
import json
import os
import secrets
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path('/home/leo/mcf-worktrees/potiguar-conversational-controller-20261113')
STATE = Path('/home/leo/.local/state/potiguar-public-demo-20261114')
NAME = 'potiguar-copilot-public-demo-20261114'
TUNNEL = 'potiguar-copilot-public-demo-tunnel-20261114'
SRC_IMAGE = 'potiguar-copilot-hml-embedded:20261112-ready'
PORT = 18955


def run(*args):
    return subprocess.check_output(list(args), text=True, stderr=subprocess.STDOUT).strip()


def exists(name):
    return subprocess.run(['docker','container','inspect',name],
                          stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0


def build():
    if exists(NAME) or exists(TUNNEL):
        raise RuntimeError('Demo container already exists. Stop and reconcile instead.')
    STATE.mkdir(mode=0o700,parents=True,exist_ok=True)
    os.chmod(STATE,0o700)
    instance=STATE/'instance'
    instance.mkdir(mode=0o700,exist_ok=True)
    bundle=STATE/'bundle'
    if bundle.exists():
        raise RuntimeError('Snapshot already exists; refusing to overwrite')
    bundle.mkdir(mode=0o700)
    paths={
        'copilot/app.js':'static/copilot/app.js',
        'copilot/style.css':'static/copilot/style.css',
        'copilot/pcm-worklet.js':'static/copilot/pcm-worklet.js',
        'admin-onboarding-v2.js':'static/admin-onboarding-v2.js',
        'admin-onboarding-controller.js':'static/admin-onboarding-controller.js',
        'admin-onboarding-v2.css':'static/admin-onboarding-v2.css',
        'users_new_v2.html':'templates/admin/users_new_v2.html',
        'routes.py':'app/copilot/routes.py',
        'auth.py':'app/admin/auth.py',
        'observability.py':'app/observability.py',
        'public_demo.py':'app/public_demo.py',
        'demo_entry.py':'scripts/potiguar_public_demo_entry.py',
    }
    mounts=[]
    destinations={
        'copilot':'/app/static/copilot',
        'admin-onboarding-v2.js':'/app/static/admin-onboarding-v2.js',
        'admin-onboarding-controller.js':'/app/static/admin-onboarding-controller.js',
        'admin-onboarding-v2.css':'/app/static/admin-onboarding-v2.css',
        'users_new_v2.html':'/app/templates/admin/users_new_v2.html',
        'routes.py':'/app/app/copilot/routes.py',
        'auth.py':'/app/app/admin/auth.py',
        'observability.py':'/app/app/observability.py',
        'public_demo.py':'/app/app/public_demo.py',
        'demo_entry.py':'/app/demo_entry.py',
    }
    for target,source in paths.items():
        copy_to=bundle/target
        copy_to.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/source,copy_to)
        if not target.startswith('copilot/'):
            mounts += ['--volume',str(copy_to)+':'+destinations[target]+':ro']
    mounts += ['--volume',str(bundle/'copilot')+':'+destinations['copilot']+':ro']
    mounts += ['--volume',str(instance)+':/app/instance']
    # Ler somente a montagem de cofre existente, sem repetir chaves em comandos.
    source_container=json.loads(run('docker','inspect','potiguar-copilot-mobile-hml-20261113'))[0]
    old_vault=next((m['Source'] for m in source_container['Mounts']
                    if m['Destination']=='/run/potiguar-vault' and not m['RW']),None)
    if not old_vault or not Path(old_vault).is_dir():
        raise RuntimeError('No authorized read-only vault is available')
    mounts += ['--volume',old_vault+':/run/potiguar-vault:ro']
    env={x.partition('=')[0]:x.partition('=')[2] for x in source_container['Config']['Env']}
    env.update({
        'APP_ENV':'development',
        'POTIGUAR_PUBLIC_DEMO':'1',
        'POTIGUAR_ENV_LABEL':'DEMO_PUBLICA_SINTETICA_SEM_LOGIN',
        'SECRET_KEY':secrets.token_urlsafe(48),
        'DATABASE_URL':'sqlite:////app/instance/ponto.db',
        'POTIGUAR_ONBOARDING_FERNET_KEY': __import__('cryptography.fernet',fromlist=['Fernet']).Fernet.generate_key().decode('ascii'),
        'POTIGUAR_HML_PUBLIC_HTTPS':'1',
        'POTIGUAR_COPILOT_ENABLED':'1',
        'POTIGUAR_COPILOT_ACTIONS_ENABLED':'1',
        'POTIGUAR_COPILOT_DEMO_DAILY_LIMIT':'60',
        'POTIGUAR_COPILOT_VAULT_DIR':'/run/potiguar-vault',
        'WEB_CONCURRENCY':'1',
        'PORT':'8000',
    })
    for key in ('GEMINI_API_KEY','POTIGUAR_HML_AUTH_USERNAME','POTIGUAR_HML_AUTH_PASSWORD',
                'POTIGUAR_COPILOT_DEMO_RESET_TOKEN'):
        env.pop(key,None)
    env_file=STATE/'demo.env'
    with open(env_file,'x',encoding='utf8') as f:
        os.fchmod(f.fileno(),0o600)
        for k,v in env.items():
            if '\n' in v or '\r' in v:
                raise RuntimeError('Environment value with illegal newline')
            f.write(k+'='+v+'\n')

    # Nenhum proxy HTTP Basic nesta rota: autenticação é a identidade sintética,
    # única por cookie, emitida pelo próprio backend de demonstração.
    cmd=['docker','create','--name',NAME,'--restart','unless-stopped',
         '--publish','127.0.0.1:'+str(PORT)+':8000',
         '--env-file',str(env_file), *mounts,
         '--entrypoint','sh',SRC_IMAGE,
         '-c','gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 120 demo_entry:app']
    run(*cmd)
    run('docker','start',NAME)
    for attempt in range(25):
        try:
            with urllib.request.urlopen('http://127.0.0.1:'+str(PORT)+'/admin/copilot',timeout=3) as response:
                if response.status==200 and response.headers.get('X-Potiguar-Demo')=='synthetic-no-login':
                    break
        except Exception:
            pass
        time.sleep(1)
    else:
        print('APP_LOG_LAST_LINES',run('docker','logs','--tail','35',NAME)[:1800])
        raise RuntimeError('Public demo did not become healthy')
    run('docker','run','-d','--name',TUNNEL,'--network','host',
        '--restart','unless-stopped','cloudflare/cloudflared:latest',
        'tunnel','--no-autoupdate','--url',
        'http://127.0.0.1:'+str(PORT),'--loglevel','info')
    print(json.dumps({'status':'LOCAL_READY','demo_container':NAME,
         'tunnel_container':TUNNEL,'port':PORT,'auth_form':False,
         'db':'new_isolated_sqlite','max_live_sessions_per_day':60,
         'destructive_operations':False,'existing_hml_modified':False}))
if __name__=='__main__':
    build()
