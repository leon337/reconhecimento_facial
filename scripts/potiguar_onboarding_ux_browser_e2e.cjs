'use strict';
/* Regressão visual isolada: HTML gerado pelo Flask + ativos locais, sem API Gemini nem banco real. */
const fs=require('node:fs'), path=require('node:path'), http=require('node:http');
const assert=require('node:assert/strict');
const puppeteer=require(process.env.POTIGUAR_PUPPETEER_MODULE || 'puppeteer');
const ROOT=path.resolve(__dirname,'..');
const FIXTURE=process.env.POTIGUAR_E2E_HTML || '/tmp/potiguar-browser-e2e-20261113/index.html';
if(!fs.existsSync(FIXTURE)) throw Error('Gere HTML Flask com scripts/potiguar_onboarding_e2e_fixture.py ou defina POTIGUAR_E2E_HTML');
const pageHtml=fs.readFileSync(FIXTURE);
let saves=0,completeCalls=0;const savedPayloads=[];
const response=(res,status,body)=>{res.writeHead(status,{'Content-Type':'application/json'});res.end(JSON.stringify(body));};
const server=http.createServer((req,res)=>{
 const pathname=new URL(req.url,'http://localhost').pathname;
 if(pathname==='/'||/^\/admin\/onboarding\/[a-f0-9]{32}$/.test(pathname)){
  res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});return res.end(pageHtml);
 }
 if(pathname==='/admin/onboarding/drafts'){
  res.writeHead(200,{'Content-Type':'text/html'});return res.end('<html><body id="drafts-success">Rascunhos salvos</body></html>');
 }
 if(pathname==='/admin/copilot/embed/onboarding'){
  res.writeHead(200,{'Content-Type':'text/html'});return res.end('<html><body>Copiloto sintético sem Gemini</body></html>');
 }
 if(pathname.startsWith('/static/')){
  const file=path.resolve(ROOT,pathname.slice(1));
  if(!file.startsWith(ROOT+path.sep))return response(res,403,{error:'forbidden'});
  try {
   const payload=fs.readFileSync(file);
   res.writeHead(200,{'Content-Type':file.endsWith('.css')?'text/css':'application/javascript'});
   return res.end(payload);
  }catch{return response(res,404,{error:'asset_missing'});}
 }
 if(req.method==='POST'&&/\/save$/.test(pathname)){
  let raw='';req.on('data',chunk=>raw+=chunk);
  return req.on('end',()=>{
   const data=JSON.parse(raw);
   if(data.fields?.has_system_access || data.fields?.payment_method)return response(res,422,{error:'bloqueio_sintetico_da_demo'});
   saves++;savedPayloads.push(data.fields);return response(res,200,{saved:true,version:saves});
  });
 }
 if(req.method==='POST'&&/\/complete$/.test(pathname)){completeCalls++;return response(res,403,{error:'forbidden'});}
 if(pathname==='/favicon.ico'){res.writeHead(204);return res.end();}
 return response(res,404,{error:'not_found'});
});
async function setField(page,name,value){
 await page.$eval('[name="'+name+'"]',(el,val)=>{
  if(el.tagName==='SELECT')el.value=val;
  else if(el.type==='checkbox')el.checked=!!val;
  else el.value=val;
  el.dispatchEvent(new Event('input',{bubbles:true}));
  el.dispatchEvent(new Event('change',{bubbles:true}));
 },value);
}
async function step(page,n){
 assert.equal(await page.$eval('.step-panel:not([hidden])',el=>Number(el.dataset.step)),n);
}
async function advance(page,n){
 await page.click('#next-button');
 await page.waitForFunction(i=>document.querySelector('.step-panel:not([hidden])')?.dataset.step===String(i+1),{timeout:10000},n);
}
async function fields(page,names){
 return page.evaluate(ns=>Object.fromEntries(ns.map(name=>{
  const control=document.querySelector('[name="'+name+'"]');
  return [name,{hidden:control?.closest('.field-item')?.hidden,disabled:control?.disabled,value:control?.value}];
 })),names);
}
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const url='http://127.0.0.1:'+server.address().port;
 let browser;const errors=[],checks=[];
 try {
  browser=await puppeteer.launch({headless:true,executablePath:process.env.POTIGUAR_CHROME_BIN || '/usr/bin/google-chrome',
   args:['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking']});
  const page=await browser.newPage();
  await page.setViewport({width:390,height:844,deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(url,{waitUntil:'networkidle0',timeout:15000});
  await step(page,0);
  await page.click('#next-button');
  assert.match(await page.$eval('#form-errors',el=>el.textContent),/Tipo de relação/);
  assert.equal(await page.$eval('#form-errors',el=>el.closest('.step-panel')?.dataset.step),'0');
  checks.push('required_error_visible_in_current_panel_step1');
  await setField(page,'relation_type','CLT comum');await advance(page,0);await step(page,1);
  await page.click('#next-button');
  assert.match(await page.$eval('#form-errors',el=>el.textContent),/Nome completo/);
  assert.equal(await page.$eval('#field-full_name',el=>el.getAttribute('aria-invalid')),'true');
  assert.equal(await page.$eval('#form-errors',el=>el.closest('.step-panel')?.dataset.step),'1');
  checks.push('required_error_visible_and_announced_step2');
  await setField(page,'full_name','Teste de UX');await advance(page,1);
  await setField(page,'country','Brasil');
  await setField(page,'address_type','Urbano');
  let f=await fields(page,['street','rural_road','foreign_street']);
  assert.equal(f.street.hidden,false);assert.equal(f.rural_road.hidden,true);assert.equal(f.foreign_street.disabled,true);
  await setField(page,'street','Avenida Teste');
  await setField(page,'address_type','Rural');
  f=await fields(page,['street','rural_road','foreign_street']);
  assert.equal(f.street.hidden,true);assert.equal(f.rural_road.hidden,false);assert.equal(f.foreign_street.hidden,true);
  await setField(page,'address_type','Exterior');
  f=await fields(page,['street','rural_road','foreign_street']);
  assert.equal(f.street.hidden,true);assert.equal(f.rural_road.hidden,true);assert.equal(f.foreign_street.hidden,false);
  await setField(page,'address_type','Urbano');
  f=await fields(page,['street']);
  assert.equal(f.street.value,'Avenida Teste','Campo oculto preservado na UI ao voltar');
  checks.push('address_urban_rural_exterior_visibility_and_value_restoration');
  await advance(page,2);
  f=await fields(page,['salary','intermittent_date','non_employee_type']);
  assert.equal(f.salary.hidden,false);assert.equal(f.intermittent_date.hidden,true);assert.equal(f.non_employee_type.hidden,true);
  checks.push('clt_normal_conditional_visibility');
  await advance(page,3);
  assert.match(await page.$eval('.step-panel:not([hidden]) .info-banner',el=>el.textContent),/financeir/);
  await setField(page,'payment_method','PIX');
  f=await fields(page,['pix_key','bank','salary_bank']);
  assert.equal(f.pix_key.hidden,false);assert.equal(f.bank.disabled,true);assert.equal(f.salary_bank.hidden,true);
  await setField(page,'payment_method','');
  await advance(page,4);
  assert.equal(await page.$eval('[name="has_system_access"]',el=>el.disabled),true);
  assert.equal((await fields(page,['access_login'])).access_login.hidden,true);
  assert.match(await page.$eval('.step-panel:not([hidden]) .info-banner',el=>el.textContent),/HTTP 422/);
  checks.push('payment_conditional_and_demo_access_warning_422_preserved');
  await advance(page,5);
  await page.click('#next-button');
  assert.match(await page.$eval('#form-errors',el=>el.textContent),/Momento da biometria/);
  assert.equal(await page.$eval('#form-errors',el=>el.closest('.step-panel')?.dataset.step),'6');
  await setField(page,'biometric_timing','Agora');
  assert.equal((await fields(page,['biometric_notice_ack'])).biometric_notice_ack.hidden,false);
  await setField(page,'biometric_timing','Depois');
  assert.equal((await fields(page,['biometric_notice_ack'])).biometric_notice_ack.hidden,true);
  checks.push('biometric_conditional_and_required_error_step7');
  await advance(page,6);await step(page,7);
  assert.match(await page.$eval('.step-panel:not([hidden])',el=>el.textContent),/HTTP 403/);
  await page.click('#copilot-open');
  assert.equal(await page.$eval('#copilot-close',el=>getComputedStyle(el).whiteSpace),'nowrap');
  await page.click('#copilot-close');
  checks.push('drawer_close_button_does_not_wrap');
  assert.equal(completeCalls,0);
  await page.click('#save-button');
  await page.waitForFunction(()=>location.pathname==='/admin/onboarding/drafts',{timeout:10000});
  assert.equal(completeCalls,0);assert(saves>=2);
  assert(savedPayloads.every(p=>!p.has_system_access&&!p.payment_method));
  checks.push('save_and_exit_redirects_without_employee_creation');
  const shell=await browser.newPage();await shell.setViewport({width:390,height:844,deviceScaleFactor:1,isMobile:true,hasTouch:true});
  await shell.goto(url+'/static/copilot/style.css').catch(()=>{});
  await shell.goto(url,{waitUntil:'domcontentloaded'});
  await shell.setContent('<link rel="stylesheet" href="'+url+'/static/copilot/style.css"><div class="shell persistent-shell"><main class="workspace persistent-workspace"><header class="topbar"><h1>Teste</h1></header><div class="persistent-columns"><section class="app-stage"></section><div class="persistent-copilot-grid"></div></div><div class="persistent-voice-dock"><button>Conectar</button><button>Chat</button></div></main></div>');
  await shell.waitForFunction(()=>Number.parseFloat(getComputedStyle(document.querySelector('.persistent-workspace')).paddingBottom)>60,{timeout:5000});
  const geometry=await shell.evaluate(()=>{
    const work=document.querySelector('.persistent-workspace');
    return {padding:getComputedStyle(work).paddingBottom,
      stageBottom:document.querySelector('.persistent-columns').getBoundingClientRect().bottom,
      dockTop:document.querySelector('.persistent-voice-dock').getBoundingClientRect().top};
  });
  assert(geometry.stageBottom<=geometry.dockTop,JSON.stringify(geometry));
  checks.push('390x844_dock_does_not_overlap_workspace');
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({status:'PASS',checks,viewport:'390x844',saves,completeCalls,pageErrors:errors},null,2));
 } finally {if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error('UX_E2E_FAIL',e.stack||e);process.exitCode=1});
