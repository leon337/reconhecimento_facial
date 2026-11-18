'use strict';
/**
 * Testa o bundle real em Chromium usando backend HTTP e WebSocket 100% simulados.
 * NÃO chama Google, não lê cofre e não consome quota; sem dados pessoais.
 *
 * Requer: npm ci && npm run build em frontend/copilot.
 * POTIGUAR_PUPPETEER_MODULE=/caminho/puppeteer node scripts/potiguar_live_connect_browser_e2e.cjs
 */
const http=require('node:http');
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const puppeteer=require(process.env.POTIGUAR_PUPPETEER_MODULE || 'puppeteer');
const root=path.resolve(__dirname,'..');
const visited=new Map();
const issued=new Map();
const rejected=new Map();
const json=(res,status,obj)=>{
 res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});
 res.end(JSON.stringify(obj));
};
const server=http.createServer((req,res)=>{
 const pathname=new URL(req.url,'http://localhost').pathname;
 const referer=new URL(req.headers.referer||'http://localhost/embed?scenario=unknown');
 const scenario=referer.searchParams.get('scenario') || 'unknown';
 if(pathname==='/embed'){
   res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});
   return res.end('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Copiloto sintético</title><link rel="stylesheet" href="/static/copilot/style.css"><div id="potiguar-copilot" data-embed="onboarding" data-csrf-token="TEST_ONLY"></div><script type="module" src="/static/copilot/app.js"></script></html>');
 }
 if(pathname==='/static/copilot/app.js'||pathname==='/static/copilot/style.css'){
   const file=path.resolve(root,pathname.slice(1));
   if(!file.startsWith(root+path.sep))return json(res,403,{error:'forbidden'});
   const payload=fs.readFileSync(file);
   res.writeHead(200,{'Content-Type':file.endsWith('.js')?'application/javascript':'text/css'});
   return res.end(payload);
 }
 if(pathname==='/admin/copilot/meta')
   return json(res,200,{enabled:true,configured:true,can_create_with_ai:true,models:['gemini-3.8-live','gemini-3.8-live-extended-thinking']});
 if(pathname==='/admin/copilot/csrf-token')return json(res,200,{csrf_token:'SYNTHETIC_CSRF'});
 if(pathname==='/admin/copilot/session-token'&&req.method==='POST'){
   visited.set(scenario,(visited.get(scenario)||0)+1);
   const previous=issued.get(scenario)||0;
   if(previous && Date.now()-previous<15000){
     rejected.set(scenario,(rejected.get(scenario)||0)+1);
     return json(res,429,{error:'Aguarde antes de iniciar outra sessão.'});
   }
   issued.set(scenario,Date.now());
   let raw='';req.on('data',c=>raw+=c);
   return req.on('end',()=>{
     const data=JSON.parse(raw);
     assert(['gemini-3.8-live','gemini-3.8-live-extended-thinking'].includes(data.model));
     return json(res,200,{token:'auth_tokens/SYNTHETIC_NOT_GOOGLE',model:data.model});
   });
 }
 if(pathname==='/favicon.ico'){res.writeHead(204);return res.end();}
 return json(res,404,{error:'not_found'});
});

const installFakeWebSocket=(mode)=>{
  window.__mockWsCount=0;
  const OriginalWebSocket=window.WebSocket;
  class MockWebSocket{
    static CONNECTING=0;static OPEN=1;static CLOSING=2;static CLOSED=3;
    constructor(url){
      const target=new URL(url);
      if(target.hostname!=='generativelanguage.googleapis.com')
        throw Error('Somente domínio público do provedor esperado');
      window.__mockWsCount++;
      this.readyState=0;
      this.onopen=null;this.onmessage=null;this.onerror=null;this.onclose=null;
      setTimeout(()=>{
        if(this.readyState!==0)return;
        if(mode==='fail') {
          this.readyState=3;
          this.onerror?.({type:'error',message:'SECRET_ERROR_NOT_PUBLIC'});
          this.onclose?.({code:1006,reason:'SECRET_CLOSE_REASON_NOT_PUBLIC'});
          return;
        }
        this.readyState=1;this.onopen?.({type:'open'});
      },25);
    }
    send(data){
      if(this.readyState!==1)throw Error('Socket fechado');
      // A API retorna setupComplete antes do primeiro turno. Nunca registrar data.
      setTimeout(()=>this.onmessage?.({data:JSON.stringify({setupComplete:{}})}),30);
    }
    close(){
      if(this.readyState===3)return;
      this.readyState=3;setTimeout(()=>this.onclose?.({code:1000,reason:''}),1);
    }
  }
  window.WebSocket=MockWebSocket;
  window.__restoreWebSocket=()=>{window.WebSocket=OriginalWebSocket;};
};

(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const host='http://127.0.0.1:'+server.address().port;
  const cases=[],pageErrors=[];let browser;
  try {
    browser=await puppeteer.launch({headless:true,executablePath:process.env.POTIGUAR_CHROME_BIN||'/usr/bin/google-chrome',
      args:['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking']});
    for(const item of [
      {scenario:'failed-first',mode:'fail',model:'gemini-3.8-live'},
      {scenario:'live-success',mode:'success',model:'gemini-3.8-live'},
      {scenario:'extended-success',mode:'success',model:'gemini-3.8-live-extended-thinking'},
    ]) {
      const page=await browser.newPage();
      await page.setViewport({width:390,height:844,deviceScaleFactor:1,isMobile:true,hasTouch:true});
      page.on('pageerror',e=>pageErrors.push('PAGE_ERROR:'+e.name));
      await page.evaluateOnNewDocument(installFakeWebSocket,item.mode);
      await page.goto(host+'/embed?scenario='+item.scenario,{waitUntil:'networkidle0'});
      await page.waitForSelector('.config button');
      await page.select('#onb-model',item.model);
      await page.click('.config input[type=checkbox]');
      await page.waitForFunction(()=>document.querySelector('.config button')?.disabled===false,{timeout:5000});
      await page.click('.config button');
      if(item.mode==='fail'){
        await page.waitForFunction(()=>document.querySelector('.error')?.textContent?.includes('LIVE_WS_'),{timeout:10000});
        const first=await page.$eval('.error',e=>e.textContent);
        assert.match(first,/LIVE_WS_/);
        assert.doesNotMatch(first,/SECRET|SYNTHETIC|auth_tokens/);
        assert.equal(await page.$eval('.composer textarea',e=>e.disabled),true);
        // Sem retry automático; segunda solicitação explícita recebe 429 do mock.
        await page.click('.config button');
        await page.waitForFunction(()=>document.querySelector('.error')?.textContent?.includes('LIVE_TOKEN_HTTP_429'),{timeout:8000});
        assert.equal(rejected.get(item.scenario),1);
        assert.equal(visited.get(item.scenario),2);
        cases.push('first_ws_failure_classified_and_second_click_429_no_automatic_retry');
      }else{
        await page.waitForFunction(()=>document.querySelector('header span')?.textContent==='Conectado',{timeout:12000});
        assert.equal(await page.$eval('.composer textarea',e=>e.disabled),false);
        assert.equal(await page.evaluate(()=>window.__mockWsCount),1);
        assert.equal(visited.get(item.scenario),1);
        cases.push(item.model+'_connected_with_one_ephemeral_token');
      }
      await page.close();
    }
    assert.deepEqual(pageErrors,[]);
    console.log(JSON.stringify({status:'PASS',checks:cases,viewport:'390x844',
      synthetic_only:true,google_calls:0,pageErrors},null,2));
  }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error('LIVE_BROWSER_E2E_FAIL',e.stack||e);process.exitCode=1});
