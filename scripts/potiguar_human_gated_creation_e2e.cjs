'use strict';
// Testa navegador + Flask REAL com funcionário explicitamente sintético,
// sem usar Gemini remoto nem dados pessoais verdadeiros.
// A ferramenta só solicita confirmação; o humano simulado autoriza a UI.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const puppeteer=require(process.env.POTIGUAR_PUPPETEER_MODULE||'puppeteer');
const BASE=process.env.POTIGUAR_E2E_BASE||'http://127.0.0.1:18953';
const CREDS=process.env.POTIGUAR_E2E_CREDENTIALS;
if(!CREDS||!/^(http:\/\/127\.0\.0\.1|https:\/\/)/.test(BASE))
  throw Error('Base de desenvolvimento privada e credenciais sintéticas obrigatórias.');
const credential=JSON.parse(fs.readFileSync(CREDS,'utf8'));
if(credential.database_scope!=='isolated_synthetic')
  throw Error('Testes de criação proibidos fora do banco exclusivamente sintético.');
const userName='Teste Copiloto Integracao '+Date.now();
(async()=>{
 const checks=[],errors=[];
 const browser=await puppeteer.launch({
   headless:true,executablePath:'/usr/bin/google-chrome',
   args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
   const page=await browser.newPage();
   await page.setViewport({width:412,height:896,deviceScaleFactor:1,isMobile:true,hasTouch:true});
   page.on('pageerror',e=>errors.push(e.message));
   await page.authenticate({username:credential.username,password:credential.password});
   await page.goto(BASE+'/admin/login',{waitUntil:'domcontentloaded'});
   await page.type('#username',credential.username);
   await page.type('#password',credential.password);
   await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded'}),
     page.click('form button[type=submit]')]);
   assert(page.url().includes('/admin/users'));
   const userListBefore=await page.content();
   assert(!userListBefore.includes(userName));
   checks.push('private_login_required_and_new_test_user_absent');
   await page.goto(BASE+'/admin/onboarding/new',{waitUntil:'domcontentloaded'});
   await page.waitForSelector('#onboarding-v2');
   assert.equal(await page.$eval('#onboarding-v2',el=>el.dataset.demo),'0');
   checks.push('private_real_backend_v2_eight_steps');

   for(let step=0;step<7;step++){
     const current=await page.$eval('.step-panel:not([hidden])',el=>Number(el.dataset.step));
     assert.equal(current,step,'unexpected step '+step);
     if(step===0){
       await page.$eval('#field-relation_type',el=>{
         el.value='CLT comum';el.dispatchEvent(new Event('input',{bubbles:true}));
       });
     }
     if(step===1){
       await page.$eval('#field-full_name',(el,name)=>{
         el.value=name;el.dispatchEvent(new Event('input',{bubbles:true}));
       },userName);
     }
     if(step===2){
       await page.$eval('#field-country',el=>{
         el.value='Brasil';el.dispatchEvent(new Event('input',{bubbles:true}));
       });
       await page.$eval('#field-address_type',el=>{
         el.value='Urbano';el.dispatchEvent(new Event('input',{bubbles:true}));
       });
     }
     if(step===6){
       await page.$eval('#field-biometric_timing',el=>{
         el.value='Depois';el.dispatchEvent(new Event('input',{bubbles:true}));
       });
     }
     await page.click('#next-button');
     await page.waitForFunction(expected=>Number(
       document.querySelector('.step-panel:not([hidden])')?.dataset.step)===expected,
       {timeout:13000},step+1);
   }
   assert.equal(await page.$eval('#current-step-name',el=>el.textContent),'Revisão');
   assert((await page.$eval('#review-details',el=>el.textContent)).includes(userName));
   checks.push('all_eight_steps_validated_and_reviewed');
   await page.click('#copilot-open');
   await page.waitForSelector('#onboarding-copilot-frame');
   await page.waitForFunction(()=>document.querySelector('#onboarding-copilot-frame')
     ?.contentWindow?.location?.pathname==='/admin/copilot/embed/onboarding'
     &&document.querySelector('#onboarding-copilot-frame')?.contentDocument
       ?.readyState==='complete',{timeout:12000});
   const frame=page.frames().find(f=>f.url().includes('/admin/copilot/embed/onboarding'));
   assert(frame);
   await frame.evaluate(()=>{window.receipts=[];window.addEventListener('message',event=>{
     if(event.origin===location.origin&&event.data?.type==='potiguar:onboarding:result')
       window.receipts.push(event.data);
   });parent.postMessage({type:'potiguar:onboarding:begin'},location.origin);});
   const id=await frame.evaluate(()=>{
     const requestId=crypto.randomUUID();
     parent.postMessage({type:'potiguar:onboarding:execute',requestId,
       action:'request_completion'},location.origin);
     return requestId;
   });
   await frame.waitForFunction(id=>window.receipts.some(x=>x.requestId===id),{timeout:10000},id);
   const receipt=await frame.evaluate(id=>window.receipts.find(x=>x.requestId===id),id);
   assert.equal(receipt.status,'awaiting_human_confirmation');
   assert.equal(receipt.step,7);
   checks.push('agent_requests_confirmation_without_persisting');
   const preReviewList=await page.evaluate(async()=>{
     const r=await fetch('/admin/users',{credentials:'same-origin'});
     return r.text();
   });
   assert(!preReviewList.includes(userName),'employee_created_before_human_confirmation');
   checks.push('no_employee_created_before_human_click');
   let confirmation=false;
   page.on('dialog',async dialog=>{
     assert.equal(dialog.type(),'confirm');
     assert(dialog.message().includes(userName),'dialog_must_identify_employee');
     confirmation=true;await dialog.accept();
   });
   await page.click('#complete-button');
   await page.waitForFunction(()=>location.pathname==='/admin/users',{timeout:18000});
   assert(confirmation,'explicit_human_confirmation_missing');
   const list=await page.content();
   assert(list.includes(userName),'created_employee_not_in_registry');
   checks.push('human_confirmed_atomic_flask_creation_verified_in_list');
   assert.deepEqual(errors,[]);
   console.log(JSON.stringify({status:'PASS',checks,syntheticEmployee:true,
     employeeName:userName,createdAfterHumanGate:true,pageErrors:errors},null,2));
 }finally{await browser.close();}
})().catch(err=>{console.error('E2E_FAIL',err.message);process.exitCode=1});
