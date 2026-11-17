'use strict';
const http=require('node:http'), fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const puppeteer=require(process.env.POTIGUAR_PUPPETEER_MODULE || 'puppeteer');
const ROOT=path.resolve(__dirname,'..');
const FIXTURE=process.env.POTIGUAR_E2E_HTML || '/tmp/potiguar-browser-e2e-20261113/index.html';
const saved=[];let version=0,conflict=false,completeCalls=0;
function respond(res,status,data){res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify(data));}
const iframe='<!doctype html><html lang="pt-BR"><meta charset="utf-8"><body><script>window.received=[];window.addEventListener("message",event=>{if(event.origin===location.origin)window.received.push(event.data)});window.parent.postMessage({type:"potiguar:onboarding:ready"},location.origin);</script></body></html>';
const srv=http.createServer((req,res)=>{
 const urlPath=new URL(req.url,'http://localhost').pathname;
 if(urlPath==='/'||/^\/admin\/onboarding\/[a-f0-9]{32}$/.test(urlPath)){res.writeHead(200,{'Content-Type':'text/html;charset=utf-8'});return res.end(fs.readFileSync(FIXTURE));}
 if(urlPath==='/admin/copilot/embed/onboarding'){res.writeHead(200,{'Content-Type':'text/html;charset=utf-8'});return res.end(iframe);}
 if(urlPath.startsWith('/static/')){
  const p=path.resolve(ROOT,urlPath.replace(/^\/+/,''));
  if(!p.startsWith(ROOT+path.sep))return respond(res,403,{error:'forbidden'});
  try{const data=fs.readFileSync(p);res.writeHead(200,{'Content-Type':p.endsWith('.js')?'application/javascript':p.endsWith('.css')?'text/css':'application/octet-stream'});return res.end(data);}
  catch{return respond(res,404,{error:'asset_not_found'});}
 }
 if(req.method==='POST'&&/\/save$/.test(urlPath)){
  let raw='';req.on('data',c=>raw+=c);
  return req.on('end',()=>{
   let body;try{body=JSON.parse(raw);}catch{return respond(res,400,{error:'bad_json'});}
   if(conflict||body.version!==version)return respond(res,409,{error:'conflito_de_versao'});
   if(!body.fields)return respond(res,422,{error:'bad_fields'});
   version++;saved.push({version,fields:body.fields});return respond(res,200,{saved:true,version});
  });
 }
 if(req.method==='POST'&&/\/complete$/.test(urlPath)){completeCalls++;return respond(res,403,{error:'never_create_in_test'});}
 if(urlPath==='/favicon.ico'){res.writeHead(204);return res.end();}
 return respond(res,404,{error:'not_found'});
});
const sleep=(ms)=>new Promise(resolve=>setTimeout(resolve,ms));
(async()=>{
 await new Promise(resolve=>srv.listen(0,'127.0.0.1',resolve));
 const errors=[],checks=[];let browser;
 try{
  browser=await puppeteer.launch({headless:true,executablePath:process.env.POTIGUAR_CHROME_BIN || '/usr/bin/google-chrome',args:['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking']});
  const page=await browser.newPage();
  await page.setViewport({width:412,height:896,deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',e=>errors.push(e.message));
  page.on('dialog',d=>d.dismiss());
  await page.goto('http://127.0.0.1:'+srv.address().port+'/',{waitUntil:'networkidle0',timeout:30000});
  assert.equal(await page.$eval('.step-panel:not([hidden])',el=>el.dataset.step),'0');
  checks.push('real_flask_html_eight_steps');
  await page.click('#copilot-open');
  await page.waitForFunction(()=>document.querySelector('#onboarding-copilot-frame')?.contentDocument?.readyState==='complete',{timeout:10000});
  const frame=page.frames().find(f=>f.url().includes('/admin/copilot/embed/onboarding'));
  assert(frame,'iframe_missing');
  await frame.evaluate(()=>parent.postMessage({type:'potiguar:onboarding:begin'},location.origin));
  await page.waitForFunction(()=>document.querySelector('#guided-field')?.textContent.includes('Tipo de relação'),{timeout:7000});
  checks.push('begin_one_question');
  // Recibos reais do orquestrador: a resposta deve vir da interface pai após executar.
  const operation=async(type,data={})=>{
    const requestId=await frame.evaluate(args=>{
      const id=crypto.randomUUID();
      parent.postMessage({...args,requestId:id},location.origin);
      return id;
    },{type,...data});
    await frame.waitForFunction(id=>window.received.some(m=>
      m.type==='potiguar:onboarding:result'&&m.requestId===id),{timeout:7000},requestId);
    return frame.evaluate(id=>window.received.find(m=>m.type==='potiguar:onboarding:result'&&m.requestId===id),requestId);
  };
  let receipt=await operation('potiguar:onboarding:execute',{action:'get_state'});
  assert.equal(receipt.status,'state');assert.equal(receipt.step,0);
  assert.equal(receipt.field,'relation_type');
  checks.push('agent_reads_step_without_field_values');
  receipt=await operation('potiguar:onboarding:execute',{action:'skip_optional'});
  assert.equal(receipt.status,'denied');
  receipt=await operation('potiguar:onboarding:execute',{action:'complete'});
  assert.equal(receipt.status,'denied');
  assert.equal(completeCalls,0);
  receipt=await operation('potiguar:onboarding:navigate',{kind:'open_step',step:5});
  assert.equal(receipt.status,'denied','future steps require prior validation');
  checks.push('agent_cannot_skip_required_or_complete_employee');
  checks.push('agent_cannot_jump_unvalidated_steps');
  receipt=await operation('potiguar:onboarding:execute',{action:'save_draft'});
  assert.equal(receipt.status,'saved');
  checks.push('agent_save_draft_receipt');
  receipt=await operation('potiguar:onboarding:execute',{action:'focus_current_field'});
  assert.equal(receipt.status,'focused');
  assert.equal(await page.$eval('#onboarding-copilot-drawer',el=>getComputedStyle(el).display),'none');
  await page.click('#copilot-open');
  checks.push('agent_focuses_form_field_and_minimizes_drawer');
  await page.evaluate(()=>window.postMessage({type:'potiguar:onboarding:proposal',step:0,suggestions:[{field:'relation_type',value:'CLT comum'}]},location.origin));
  await sleep(120);
  assert.equal(await page.$eval('#field-relation_type',el=>el.value),'');
  checks.push('ignore_wrong_window_source');
  receipt=await operation('potiguar:onboarding:proposal',{step:0,suggestions:[{field:'relation_type',value:'CLT comum'}]});
  assert.equal(receipt.status,'saved');
  await page.waitForFunction(()=>document.querySelector('#field-relation_type')?.value==='CLT comum'&&document.querySelector('#current-step-label')?.textContent.includes('Etapa 2'),{timeout:7000});
  assert.equal(saved.length,1);
  checks.push('auto_apply_persist_move_to_step_2');
  checks.push('agent_receives_save_confirmation_after_server_response');
  await page.waitForFunction(()=>document.querySelector('#guided-field')?.textContent.includes('Nome completo'),{timeout:7000});
  receipt=await operation('potiguar:onboarding:proposal',{step:1,suggestions:[{field:'cpf',value:'52998224725'}]});
  assert.equal(receipt.status,'validation_failed');
  checks.push('agent_rejects_confidential_field_proposal');
  await frame.evaluate(()=>parent.postMessage({type:'potiguar:onboarding:proposal',step:1,suggestions:[{field:'full_name',value:'Maria Oliveira de Teste'}]},location.origin));
  await page.waitForFunction(()=>document.querySelector('#field-full_name')?.value==='Maria Oliveira de Teste'&&document.querySelector('#guided-field')?.textContent.includes('CPF'),{timeout:7000});
  checks.push('one_safe_field_then_protected_field');
  await page.click('#copilot-minimize');
  assert.equal(await page.$eval('#onboarding-copilot-drawer',el=>getComputedStyle(el).display),'none');
  await page.focus('#field-cpf');
  await page.keyboard.type('52998224725');
  await page.$eval('#field-cpf',el=>el.blur());
  await page.waitForFunction(()=>document.querySelector('#guided-field')?.textContent.includes('Data de nascimento'),{timeout:7000});
  assert.equal(saved.at(-1).fields.cpf,'52998224725');
  checks.push('protected_field_local_save_mobile');
  await page.click('#copilot-open');
  await page.waitForFunction(()=>document.querySelector('#guided-field')?.textContent.includes('Data de nascimento'),{timeout:7000});
  const messages=await frame.evaluate(()=>window.received);
  assert(!JSON.stringify(messages).includes('52998224725'),'cpf_leaked_to_iframe');
  checks.push('no_secret_leak_to_iframe');
  // Percorrer todas as oito etapas, pulando somente opcionais.
  let traversed=0, agentSkipped=false;
  for(;traversed<150;traversed++){
    const stage=await page.$eval('#current-step-label',el=>el.textContent);
    if(stage.includes('Etapa 8'))break;
    const q=await frame.evaluate(()=>window.received.filter(x=>x.type==='potiguar:onboarding:question').at(-1)||null);
    assert(q,'missing question');
    const before=await frame.evaluate(()=>window.received.filter(x=>x.type==='potiguar:onboarding:question').length);
    if(!q.required){
      if(!agentSkipped){
        receipt=await operation('potiguar:onboarding:execute',{action:'skip_optional'});
        assert.equal(receipt.status,'skipped');agentSkipped=true;
      }else await frame.evaluate(data=>parent.postMessage({type:'potiguar:onboarding:skip',step:data.step,field:data.field},location.origin),q);
    }else if(q.safe){
      const values={country:'Brasil',address_type:'Urbano'};
      assert(values[q.field],'unexpected required safe field: '+q.field);
      await frame.evaluate(data=>parent.postMessage({type:'potiguar:onboarding:proposal',step:data.step,suggestions:[{field:data.field,value:data.value}]},location.origin),{...q,value:values[q.field]});
    }else{
      assert.equal(q.field,'biometric_timing','unexpected protected required field');
      await page.$eval('#field-biometric_timing',el=>{el.value='Depois';el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));});
    }
    await page.waitForFunction((count)=>
      document.querySelector('#current-step-label')?.textContent.includes('Etapa 8')
      || document.querySelector('#onboarding-copilot-frame')?.contentWindow?.received?.filter(x=>x.type==='potiguar:onboarding:question').length>count,
      {timeout:7000},before);
  }
  assert(traversed<150,'stage traversal stuck');
  assert(agentSkipped,'agent had to skip one optional field');
  checks.push('agent_skips_only_optional_fields');
  assert.equal(await page.$eval('#current-step-name',el=>el.textContent),'Revisão');
  const reviewText=await page.$eval('#review-details',el=>el.textContent);
  assert(reviewText.includes('Maria Oliveira de Teste'));
  assert.equal(completeCalls,0);
  receipt=await operation('potiguar:onboarding:execute',{action:'request_completion'});
  assert.equal(receipt.status,'awaiting_human_confirmation');
  assert.equal(completeCalls,0,'request_completion_must_not_create');
  checks.push('agent_requests_human_confirmation_without_creating_employee');
  await page.click('#complete-button');
  await sleep(100);
  assert.equal(completeCalls,0,'automatic completion was not permitted');
  checks.push('complete_eight_steps_with_conditional_skips');
  checks.push('review_only_human_gate_no_employee_creation');
  await page.screenshot({path:process.env.POTIGUAR_E2E_SCREENSHOT || '/tmp/potiguar-browser-e2e-20261113/onboarding-mobile-e2e.png'});
  await page.click('#copilot-open');
  receipt=await operation('potiguar:onboarding:navigate',{kind:'correct_field',step:0,field:'relation_type'});
  assert.equal(receipt.status,'navigated');
  await page.waitForFunction(()=>document.querySelector('#current-step-label')?.textContent.includes('Etapa 1'),{timeout:7000});
  await page.waitForFunction(()=>document.querySelector('#guided-field')?.textContent.includes('Tipo de relação'),{timeout:7000});
  checks.push('correction_navigates_previous_stage');
  conflict=true;
  await frame.evaluate(()=>parent.postMessage({type:'potiguar:onboarding:proposal',step:0,suggestions:[{field:'relation_type',value:'CLT intermitente'}]},location.origin));
  await page.waitForFunction(()=>document.querySelector('#form-errors')?.textContent.includes('Conflito de edição'),{timeout:7000});
  assert.equal(completeCalls,0);
  checks.push('409_blocks_stale_save_no_employee_created');
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({status:'PASS',checks,draft_saves:saved.length,latest_version:version,created_employees:completeCalls,viewport:'412x896',errors},null,2));
 }finally{if(browser)await browser.close();await new Promise(resolve=>srv.close(resolve));}
})().catch(e=>{console.error('E2E FAIL',e.stack||e);process.exitCode=1;});
