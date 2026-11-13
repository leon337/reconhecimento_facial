#!/usr/bin/env python3
"""Deploy atômico e reversível do Copiloto V2 HML, sem expor segredos."""
import json
import os
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path
from http.client import HTTPConnection

OLD='potiguar-copilot-hml-20261111'
ROLLBACK='potiguar-copilot-hml-before-copilot-form-20261112'
CANDIDATE='potiguar-copilot-hml-copilot-form-preflight-20261112'
IMAGE='potiguar-copilot-hml-embedded:20261112-ready'
DB=Path('/home/leo/.local/share/potiguar-copilot-hml-20261111/instance/staging.sqlite3')

def docker(*args,input=None):
    p=subprocess.run(['docker',*args],input=input,capture_output=True,text=True,timeout=90)
    if p.returncode:
        raise RuntimeError('docker_failed:'+str(args[:2])+':'+p.stderr[-350:])
    return p.stdout.strip()

def exists(name):
    return subprocess.run(['docker','inspect',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0

def check_http(port,path,status):
    connection=HTTPConnection('127.0.0.1',port,timeout=4)
    try:
        connection.request('GET',path,headers={'Accept':'text/html'})
        response=connection.getresponse()
        got=response.status
        response.read(256)
        return got==status
    finally:
        connection.close()

def wait_http(port,path='/admin/login',status=200,attempts=24):
    for _ in range(attempts):
        try:
            if check_http(port,path,status):return True
        except Exception:pass
        time.sleep(.7)
    return False

def create(name,port,inspection,*,restart=False):
    env_items=inspection['Config']['Env']
    mounts=inspection['Mounts']
    cmd=['create','--name',name,'--network','bridge',
         '--env-file','/dev/stdin','-p',f'127.0.0.1:{port}:8000']
    if restart:cmd.extend(['--restart','unless-stopped'])
    for item in mounts:
        if item['Type']!='bind':raise RuntimeError('unsupported_mount_type')
        volume=f"{item['Source']}:{item['Destination']}"
        if not item['RW']:volume+=':ro'
        cmd.extend(['-v',volume])
    cmd.append(IMAGE)
    env='\n'.join(env_items)+'\n'
    return docker(*cmd,input=env)

def check_auth_container(name):
    script=r'''from main import create_app
from app.models import User,Employee,Ponto
from app.rbac import Permission
from app.onboarding_models import OnboardingDraft
app=create_app({'AUTO_CREATE_SCHEMA':False,'WTF_CSRF_ENABLED':False})
with app.app_context():
 u=User.query.filter_by(username='potiguar-demo').one()
 assert u.can(Permission.USERS_CREATE)
 before=(Employee.query.count(),Ponto.query.count(),OnboardingDraft.query.count())
 with app.test_client() as client:
  with client.session_transaction() as s:
   s['admin_user_id']=u.id;s['admin_company_id']=u.company_id;s['admin_worksite_id']=u.worksite_id
  copilot=client.get('/admin/copilot/embed/onboarding')
  assert copilot.status_code==200
  assert copilot.headers['X-Frame-Options']=='SAMEORIGIN'
  assert "frame-ancestors 'self'" in copilot.headers['Content-Security-Policy']
  assert 'microphone=(self)' in copilot.headers['Permissions-Policy']
  draft=client.get('/admin/onboarding/new')
  assert draft.status_code==302
  form=client.get(draft.location)
  assert form.status_code==200
  body=form.get_data(as_text=True)
  assert 'onboarding-copilot-drawer' in body
  assert all(f'ETAPA {i} DE 8' in body for i in range(1,9))
  with_id=draft.location.rsplit('/',1)[-1]
  disposed=client.post(draft.location+'/discard')
  assert disposed.status_code==200
 after=(Employee.query.count(),Ponto.query.count(),OnboardingDraft.query.count())
 assert before==after
 print('AUTH_COPILOT=200 AUTH_FORM=200 STEPS=8 DATA_PRESERVED=YES')'''
    result=docker('exec','-i',name,'python','-c',script)
    if 'DATA_PRESERVED=YES' not in result:raise RuntimeError('authenticated_preflight_failed')
    print(result.splitlines()[-1],flush=True)

def main():
    if exists(ROLLBACK) or exists(CANDIDATE):
        raise RuntimeError('container_name_conflict')
    if not exists(OLD):raise RuntimeError('current_container_missing')
    data=json.loads(docker('inspect',OLD))[0]
    if data['Config']['Image']!='potiguar-copilot-hml-onboarding:20261112-final':
        raise RuntimeError('unexpected_current_image')
    if not DB.exists():raise RuntimeError('live_db_missing')
    backup=DB.with_name('staging.before-copilot-embedded-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.sqlite3')
    with sqlite3.connect('file:'+str(DB)+'?mode=ro',uri=True) as src:
        with sqlite3.connect(str(backup)) as dst:src.backup(dst)
    backup.chmod(0o600)
    with sqlite3.connect(str(backup)) as conn:
        if conn.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('sqlite_backup_invalid')
    print('SQLITE_BACKUP_VALID',backup.name,flush=True)
    create(CANDIDATE,18957,data)
    print('PREFLIGHT_CREATED',flush=True)
    try:
        docker('start',CANDIDATE)
        if not wait_http(18957):raise RuntimeError('preflight_http_unavailable')
        for path,status in [('/admin/onboarding/drafts',302),('/admin/copilot/embed/onboarding',302),('/static/copilot/app.js',200),('/static/admin-onboarding-v2.js',200)]:
            if not check_http(18957,path,status):raise RuntimeError('preflight_failed:'+path)
        check_auth_container(CANDIDATE)
    finally:
        docker('rm','-f',CANDIDATE)
    print('PREFLIGHT_PASSED',flush=True)
    # Troca com rollback automático caso o novo contêiner falhe.
    docker('stop','-t','10',OLD)
    docker('rename',OLD,ROLLBACK)
    try:
        create(OLD,18951,data,restart=True)
        docker('start',OLD)
        if not wait_http(18951):raise RuntimeError('live_http_unavailable')
        for path,status in [('/admin/onboarding/drafts',302),('/admin/copilot/embed/onboarding',302),('/static/copilot/app.js',200),('/static/admin-onboarding-v2.js',200)]:
            if not check_http(18951,path,status):raise RuntimeError('live_failed:'+path)
        check_auth_container(OLD)
        print('DEPLOY_OK_ROLLBACK_CONTAINER_RETAINED',flush=True)
    except Exception:
        try:
            if exists(OLD):docker('rm','-f',OLD)
            docker('rename',ROLLBACK,OLD)
            docker('start',OLD)
            print('ROLLBACK_RESTORED',flush=True)
        except Exception as rollback_error:
            print('ROLLBACK_ERROR',str(rollback_error)[:250],flush=True)
        raise

if __name__=='__main__':main()
