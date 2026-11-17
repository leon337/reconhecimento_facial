'use strict';
const http=require('node:http'), fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const puppeteer=require(process.env.POTIGUAR_PUPPETEER_MODULE||'puppeteer');
const root=path.resolve(__dirname,'..');
const fixtureDir=process.env.POTIGUAR_E2E_DIR||'/tmp/potiguar-browser-e2e-20261113';
const headers=JSON.parse(fs.readFileSync(path.join(fixtureDir,'embed-headers.json'),'utf8'));
assert(headers.csp && !headers.csp.includes("'unsafe-inline'"),'CSP deve proibir unsafe-inline');
assert.equal(headers.x_frame_options,'SAMEORIGIN');
assert(headers.permissions.includes('microphone=(self)'));
const server=http.createServer((req,res)=>{
 const p=new URL(req.url,'http://localhost').pathname;
 if(p==='/favicon.ico'){res.writeHead(204);return res.end();}
 if(p==='/'){
  res.writeHead(200,{'Content-Type':'text/html','Content-Security-Policy':"default-src 'self'; frame-src 'self'; script-src 'self'; frame-ancestors 'none'"});
  return res.end('<!doctype html><html lang="pt-BR"><body><iframe title="Copiloto" src="/admin/copilot/embed/onboarding" allow="microphone"></iframe></body></html>');
 }
 if(p==='/admin/copilot/embed/onboarding'){
  res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Content-Security-Policy':headers.csp,'Permissions-Policy':headers.permissions,'X-Frame-Options':headers.x_frame_options});
  return res.end(fs.readFileSync(path.join(fixtureDir,'embed.html')));
 }
 if(p==='/admin/copilot/meta'){
  res.writeHead(200,{'Content-Type':'application/json'});
  return res.end(JSON.stringify({enabled:false,configured:false,can_create_with_ai:false}));
 }
 if(p.startsWith('/static/')){
  const absolute=path.resolve(root,p.replace(/^\/+/,''));
  if(!absolute.startsWith(root+path.sep)){res.writeHead(403);return res.end();}
  try{
   const data=fs.readFileSync(absolute);
   res.writeHead(200,{'Content-Type':p.endsWith('.js')?'application/javascript':p.endsWith('.css')?'text/css':'application/octet-stream'});
   return res.end(data);
  }catch{res.writeHead(404);return res.end();}
 }
 res.writeHead(404);res.end('not found');
});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 let browser;
 try{
  browser=await puppeteer.launch({headless:true,executablePath:process.env.POTIGUAR_CHROME_BIN||'/usr/bin/google-chrome',args:['--no-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage();
  await page.setViewport({width:412,height:896,isMobile:true,hasTouch:true});
  const errors=[];const externals=[];
  page.on('pageerror',err=>errors.push(err.message));
  page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text().slice(0,200))});
  page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:')&&!r.url().startsWith('data:'))externals.push(r.url().split('/').slice(0,3).join('/'))});
  await page.goto('http://127.0.0.1:'+server.address().port+'/',{waitUntil:'networkidle0',timeout:30000});
  const frame=page.frames().find(f=>f.url().includes('/admin/copilot/embed/onboarding'));
  assert(frame,'iframe_missing');
  await frame.waitForSelector('#potiguar-copilot .embedded',{timeout:10000});
  const state=await frame.evaluate(()=>({
   header:document.querySelector('header strong')?.textContent,
   language:document.documentElement.lang,
   model:document.querySelector('#onb-model')?.value,
   connect_disabled:Array.from(document.querySelectorAll('button')).find(el=>el.textContent.includes('Conectar Copiloto'))?.disabled,
   can_access_mic:document.permissionsPolicy?.allowsFeature?.('microphone')??document.featurePolicy?.allowsFeature?.('microphone')??null,
   privacy_notice:document.querySelector('.privacy')?.textContent.includes('Não dite documentos'),
  }));
  assert.equal(state.header,'✦ Copiloto Potiguar');
  assert.equal(state.model,'gemini-3.8-live');
  assert.equal(state.language,'pt-BR');
  assert.equal(state.connect_disabled,true);
  assert.equal(state.privacy_notice,true);
  assert.deepEqual(errors,[]);
  assert.deepEqual(externals,[]);
  console.log(JSON.stringify({status:'PASS',checks:['flask_real_embed_html','real_csp_no_inline','safely_mounted_vue_in_iframe','ptbr_default','live_model_selected','cannot_connect_without_access','privacy_notice_visible','no_external_requests_without_consent','no_js_or_csp_errors'],viewport:'412x896',permissions_policy:headers.permissions,...state},null,2));
 }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error('STRICT_CSP_FAIL',e.name,String(e.message).slice(0,280));process.exitCode=2});
