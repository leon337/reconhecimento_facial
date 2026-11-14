#!/usr/bin/env python3
"""Recriar apenas a homologação sintética Potiguar. Recria mounts para o inode atual do bundle Vite.
A configuração de produção e a homologação anterior não são tocadas.
As variáveis sensíveis passam somente em memória, nunca são impressas.
"""
import os,subprocess,json,time,sys,urllib.request
from datetime import datetime,timezone
from tempfile import NamedTemporaryFile
from pathlib import Path
NAME='potiguar-copilot-mobile-hml-20261113'
BACKUP='potiguar-copilot-mobile-hml-20261113-backup-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
ROOT=Path('/home/leo/mcf-worktrees/potiguar-conversational-controller-20261113')
def run(*args):
    return subprocess.check_output(list(args),stderr=subprocess.STDOUT,text=True)
def status():
    try:
        return urllib.request.urlopen('http://127.0.0.1:18953/admin/login',timeout=2).status
    except Exception:
        return None
def main():
    config=json.loads(run('docker','inspect',NAME))[0]
    if config['Config']['Image']!='potiguar-copilot-hml-embedded:20261112-ready':
        raise RuntimeError('unexpected_image')
    mounts=config['Mounts']
    if not any(m['Source']==str(ROOT/'static/copilot/app.js') and m['Destination']=='/app/static/copilot/app.js'
               for m in mounts):raise RuntimeError('unexpected_bundle_mount')
    if not any(m['Destination']=='/app/instance' and m['RW'] for m in mounts):
        raise RuntimeError('missing_sqlite_volume')
    if config['HostConfig']['NetworkMode']!='bridge':raise RuntimeError('unexpected_network')
    if status()!=200:raise RuntimeError('original_container_not_healthy')
    try: run('docker','inspect',BACKUP)
    except subprocess.CalledProcessError:pass
    else: raise RuntimeError('preexisting_backup_container')
    # Nunca exponha SECRET_KEY e chaves da aplicação nos argumentos de processo do Docker.
    with NamedTemporaryFile('w',prefix='hml-rebind-',suffix='.env',
            dir='/home/leo/.local/state/potiguar-onboarding-mobile-hml-20261113',
            delete=False) as env_file:
        os.fchmod(env_file.fileno(),0o600)
        env_file.write(chr(10).join(config['Config']['Env'])+chr(10))
        env_path=env_file.name
    args=['docker','create','--name',NAME,
          '--restart',config['HostConfig']['RestartPolicy']['Name'],
          '--workdir',config['Config']['WorkingDir'] or '/app',
          '--env-file',env_path]
    for m in mounts:
        if m['Type']!='bind':raise RuntimeError('unexpected_mount_type')
        args+=['--volume',m['Source']+':'+m['Destination']+('' if m['RW'] else ':ro')]
    for port,bindings in config['HostConfig']['PortBindings'].items():
        for item in bindings:
            args+=['--publish',(item.get('HostIp') or '127.0.0.1')+':'+item['HostPort']+':'+port.split('/')[0]]
    entry=config['Config']['Entrypoint']
    if len(entry)!=1:raise RuntimeError('unexpected_entrypoint')
    args+=['--entrypoint',entry[0],config['Config']['Image'],*config['Config']['Cmd']]
    backup_renamed=False
    try:
        run('docker','stop','--time','8',NAME)
        run('docker','rename',NAME,BACKUP)
        backup_renamed=True
        run(*args)
        # These Python files live in the writable layer rather than an image bind mount.
        for file in ('app/admin/auth.py','app/observability.py'):
            run('docker','cp',str(ROOT/file),NAME+':/app/'+file)
        run('docker','start',NAME)
        for i in range(18):
            if status()==200:break
            time.sleep(1)
        else:raise RuntimeError('recreated_container_not_healthy')
        local=run('sha256sum',str(ROOT/'static/copilot/app.js')).split()[0]
        mounted=run('docker','exec',NAME,'sha256sum','/app/static/copilot/app.js').split()[0]
        if local!=mounted:raise RuntimeError('stale_bundle_still_mounted')
        print(json.dumps({'status':'REBOUND','healthy':True,
           'bundle_matches':True,'bundle_hash_prefix':local[:12],
           'old_container_backup':BACKUP,'production_touched':False}))
    except Exception:
        try:run('docker','stop','--time','3',NAME)
        except Exception:pass
        try:run('docker','rm',NAME)
        except Exception:pass
        if backup_renamed:
            run('docker','rename',BACKUP,NAME)
            run('docker','start',NAME)
        print(json.dumps({'status':'ROLLED_BACK'}))
        raise
    finally:
        Path(env_path).unlink(missing_ok=True)
if __name__=='__main__':main()
