'use strict';
/**
 * E2E bundle Vite real, Chromium, HTTP mock. Não usa Google, cofre, dados reais nem DB.
 * POTIGUAR_PUPPETEER_MODULE=/path/puppeteer node scripts/potiguar_https_text_browser_e2e.cjs
 */
const assert=require('node:assert/strict');
const http=require('node:http');
const fs=require('node:fs');
const path=require('node:path');
const puppeteer=require(process.env.POTIGUAR_PUPPETEER_MODULE||'puppeteer');
const root=path.resolve(__dirname,'..');
const visits={token:0,csrf:0,text:0,proposals:[]};
const send=(res,code,data)=>{
  res.writeHead(code,{'Content-Type':'application/json','Cache-Control':'no-store'});
  res.end(JSON.stringify(data));
};
const server=http.createServer((req,res)=>{
  const url=new URL(req.url,'http://127.0.0.1');
  if(url.pathname==='/embed'){
    res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});
    return res.end('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/static/copilot/style.css"><div id="potiguar-copilot" data-embed="onboarding" data-csrf-token="TEST_ONLY"></div><script type="module" src="/static/copilot/app.js"></script></html>');
  }
  if(['/static/copilot/app.js','/static/copilot/style.css'].includes(url.pathname)){
    const file=path.resolve(root,url.pathname.slice(1));
    if(!file.startsWith(root+path.sep))return send(res,403,{error:'blocked'});
    res.writeHead(200,{'Content-Type':file.endsWith('.js')?'application/javascript':'text/css'});
    return res.end(fs.readFileSync(file));
  }
  if(url.pathname==='/admin/copilot/meta')return send(res,200,{
    enabled:true,configured:true,can_create_with_ai:true,text_enabled:true,
    models:['gemini-3.8-live','gemini-3.8-live-extended-thinking']});
  if(url.pathname==='/admin/copilot/csrf-token'){visits.csrf++;return send(res,200,{csrf_token:'CSRF_ONLY_SYNTHETIC'});}
  if(url.pathname==='/admin/copilot/session-token'){
    visits.token++;
    return send(res,200,{token:'auth_tokens/SYNTHETIC_NOT_VALID',model:'gemini-3.8-live'});
  }
  if(url.pathname==='/admin/copilot/text-turn'&&req.method==='POST'){
    visits.text++;
    assert.equal(req.headers['x-csrftoken'],'CSRF_ONLY_SYNTHETIC');
    let buffer='';req.on('data',part=>buffer+=part);
    return req.on('end',()=>{
      const body=JSON.parse(buffer);
      assert.deepEqual(Object.keys(body).sort(),['step','field','candidate','request_id','consent'].sort());
      assert.equal(body.consent,true);
      assert.equal(body.field,'relation_type');
      assert.equal(body.candidate,'CLT comum');
      assert.equal(body.step,0);
      assert(!buffer.includes('usuário real') && !buffer.includes('CPF'));
      return send(res,200,{
        mode:'https_text',model_type:'text_not_live',request_id:body.request_id,
        proposal:{step:0,field:'relation_type',value:'CLT comum',reply:'Sugestão validada para o campo atual.'},
      });
    });
  }
  if(url.pathname==='/favicon.ico'){res.writeHead(204);return res.end();}
  return send(res,404,{error:'not found'});
});
(async()=>{
  await new Promise(done=>server.listen(0,'127.0.0.1',done));
  const url='http://127.0.0.1:'+server.address().port+'/embed';
  let browser;
  const pageErrors=[];
  try{
    browser=await puppeteer.launch({headless:true,executablePath:process.env.POTIGUAR_CHROME_BIN||'/usr/bin/google-chrome',
      args:['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking']});
    const page=await browser.newPage();
    await page.setViewport({width:390,height:844,deviceScaleFactor:1,isMobile:true,hasTouch:true});
    page.on('pageerror',error=>pageErrors.push(error.name));
    await page.evaluateOnNewDocument(()=>{
      window.__wsCalls=0;
      window.WebSocket=class {
        constructor(){
          window.__wsCalls++;
          throw Error('SYNTHETIC_WS_BLOCKED');
        }
      };
      window.addEventListener('message',event=>{
        if(event.source!==window||event.origin!==location.origin)return;
        if(event.data?.type==='potiguar:onboarding:begin')
          setTimeout(()=>window.postMessage({
            type:'potiguar:onboarding:question',step:0,field:'relation_type',
            label:'Tipo de relação',safe:true,required:true,
            options:['CLT comum','CLT intermitente','Sem vínculo empregatício'],
          },location.origin),20);
        if(event.data?.type==='potiguar:onboarding:proposal'){
          window.__lastProposal=event.data;
          setTimeout(()=>window.postMessage({
            type:'potiguar:onboarding:result',requestId:event.data.requestId,
            status:'saved',step:0,field:'relation_type',
          },location.origin),20);
        }
      });
    });
    await page.goto(url,{waitUntil:'networkidle0'});
    await page.waitForSelector('#onb-text-mode');
    assert.equal(await page.$eval('#onb-text-mode',b=>b.disabled),true,
      'consentimento HTTPS deve ser obrigatório');
    await page.click('.config:not(.text-https) input[type=checkbox]');
    await page.waitForFunction(()=>document.querySelector('.config:not(.text-https) button')?.disabled===false);
    await page.click('.config:not(.text-https) button');
    await page.waitForFunction(()=>document.querySelector('.error')?.textContent?.includes('LIVE_WS_'),
      {timeout:7000});
    assert.equal(visits.token,1);
    assert.equal(await page.evaluate(()=>window.__wsCalls),1);
    assert.equal(await page.$eval('#onb-text-mode',b=>b.disabled),true);
    // Falha Live NÃO ativa automaticamente texto: consentimento independente.
    await page.click('.text-https input[type=checkbox]');
    await page.click('#onb-text-mode');
    await page.waitForFunction(()=>document.querySelector('header span')?.textContent?.includes('Texto HTTPS'));
    await page.waitForFunction(()=>document.querySelector('.field-prompt strong')?.textContent?.includes('Tipo de relação'));
    assert.equal(await page.$eval('.composer button[type=button]',b=>b.disabled),true,
      'microfone proibido no HTTPS texto');
    await page.type('#onb-text','CLT comum');
    await page.click('.composer button[type=submit]');
    await page.waitForFunction(()=>Array.from(document.querySelectorAll('.bubble')).some(
      b=>b.textContent.includes('Campo salvo no rascunho.')), {timeout:12000});
    const proposal=await page.evaluate(()=>window.__lastProposal);
    assert.deepEqual(proposal.suggestions,[{field:'relation_type',value:'CLT comum'}]);
    assert.equal(visits.text,1);
    assert.equal(visits.token,1,'HTTPS texto não requer outro token Live');
    assert.equal(await page.evaluate(()=>window.__wsCalls),1,'não houve novo WebSocket');
    assert.deepEqual(pageErrors,[]);
    console.log(JSON.stringify({
      result:'PASS',viewport:'390x844',checks:[
        'live_ws_blocked_no_silent_fallback','separate_https_consent',
        'one_safe_field_https_post','parent_controller_saved_receipt',
        'voice_disabled_text_mode','no_additional_ws_token','zero_page_errors',
      ],httpTextPosts:visits.text,liveTokenPosts:visits.token,googleRequests:0,
      realEmployees:0,pageErrors,
    },null,2));
  }finally{
    if(browser)await browser.close();
    await new Promise(done=>server.close(done));
  }
})().catch(e=>{console.error('HTTPS_TEXT_E2E_FAIL',e.stack||e);process.exitCode=1});
