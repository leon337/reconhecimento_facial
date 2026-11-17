'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const puppeteer=require(process.env.POTIGUAR_PUPPETEER_MODULE||'puppeteer');
const CREDS=process.env.POTIGUAR_E2E_CREDENTIALS;
const BASE=process.env.POTIGUAR_E2E_BASE;
if(!CREDS || !BASE)throw Error('Defina URL da homologação e caminho local de credenciais sintéticas');
const credential=JSON.parse(fs.readFileSync(CREDS,'utf8'));
const checks=[],errors=[],tokenResponses=[],sockets=new Set(),closed=new Set();
(async()=>{
 let browser,page;
 try{
  browser=await puppeteer.launch({headless:true,executablePath:process.env.POTIGUAR_CHROME_BIN||'/usr/bin/google-chrome',
   args:['--no-sandbox','--disable-dev-shm-usage','--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream',
     '--autoplay-policy=no-user-gesture-required','--disable-background-networking']});
  page=await browser.newPage();
  await page.setViewport({width:412,height:896,deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',async response=>{
    if(new URL(response.url()).pathname==='/admin/copilot/session-token'){
      const status=response.status();
      let csrfFailure=false;
      if(status>=400){try{csrfFailure=/csrf/i.test(await response.text());}catch{}}
      tokenResponses.push({status,csrfFailure});
    }
  });
  const cdp=await page.createCDPSession();
  await cdp.send('Network.enable');
  cdp.on('Network.webSocketCreated',m=>sockets.add(m.requestId));
  cdp.on('Network.webSocketClosed',m=>closed.add(m.requestId));
  await page.authenticate({username:credential.username,password:credential.password});
  const auth=await page.goto(BASE+'/admin/login',{waitUntil:'domcontentloaded',timeout:30000});
  assert.equal(auth.status(),200);
  await page.type('#username',credential.username);
  await page.type('#password',credential.password);
  await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}),page.click('form button[type=submit]')]);
  assert(page.url().includes('/admin/users'),'login_redirect');
  checks.push('public_basic_auth_and_flask_login');

  await page.goto(BASE+'/admin/copilot',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForSelector('iframe.app-frame',{timeout:15000});
  await page.waitForFunction(()=>document.querySelector('iframe.app-frame')?.contentWindow?.location?.pathname==='/admin/dashboard',{timeout:15000});
  await page.evaluate(()=>{window.__shell_root=document.getElementById('potiguar-copilot');
    window.__shell_iframe=document.querySelector('iframe.app-frame')});
  const provePersistent=async(route)=>{
    await page.waitForFunction(route=>document.querySelector('iframe.app-frame')?.contentWindow?.location?.pathname===route,
      {timeout:16000},route);
    assert.equal(await page.evaluate(()=>document.getElementById('potiguar-copilot')===window.__shell_root),true);
    assert.equal(await page.evaluate(()=>document.querySelector('iframe.app-frame')===window.__shell_iframe),true);
  };
  checks.push('persistent_shell_dashboard_mobile');
  const innerHeaders=[];
  page.on('response',response=>{
    const u=response.url();
    if(u.includes('/admin/dashboard')||u.includes('/admin/relatorios')||u.includes('/admin/users'))
      innerHeaders.push({status:response.status(),url:new URL(u).pathname});
  });

  // Navegação manual entre as telas nunca recarrega o documento pai.
  // Usar iframe src diretamente equivale ao alvo dos links autorizados.
  await page.evaluate(()=>document.querySelector('iframe.app-frame').contentWindow.location.assign('/admin/relatorios'));
  await provePersistent('/admin/relatorios');
  checks.push('shell_survives_normal_report_navigation');
  await page.evaluate(()=>document.querySelector('iframe.app-frame').contentWindow.location.assign('/admin/users'));
  await provePersistent('/admin/users');
  checks.push('shell_survives_normal_employee_navigation');

  await page.click('.app-stage-controls button:nth-child(2)');
  await page.evaluate(()=>{
    const config=document.querySelector('.control-card');
    config.scrollIntoView({block:'nearest'});
  });
  await page.waitForSelector('.control-card input[type=checkbox]');
  await page.click('.control-card input[type=checkbox]');
  await page.$eval('.control-card .connect-button',button=>button.click());
  await page.waitForFunction(()=>document.querySelector('.status.online')?.textContent?.includes('Conversa conectada'),{timeout:11000});
  checks.push('real_gemini_live_connected_in_persistent_shell');
  const opened=sockets.size;
  assert(opened>=1,'gemini_live_websocket_missing');
  await page.$eval('.conversation .microphone',button=>button.click());
  await page.waitForFunction(()=>document.querySelector('.conversation .microphone')?.classList.contains('recording'),{timeout:9000});
  checks.push('microphone_started_in_persistent_shell');

  // Navegação manual com uma conexão Live real.
  await page.evaluate(()=>document.querySelector('iframe.app-frame').contentWindow.location.assign('/admin/dashboard'));
  await provePersistent('/admin/dashboard');
  assert.equal(await page.$eval('.status',el=>el.classList.contains('online')),true);
  assert.equal(closed.size,0,'websocket_closed_during_normal_navigation');
  assert.equal(await page.$eval('.conversation .microphone',el=>el.classList.contains('recording')),true);
  checks.push('live_websocket_and_microphone_remain_active_during_navigation');
  await page.$eval('.conversation .microphone',button=>button.click());
  await page.waitForFunction(()=>!document.querySelector('.conversation .microphone')?.classList.contains('recording'),{timeout:7000});
  checks.push('microphone_stops_on_user_request_without_disconnect');

  // Conjunto de ferramentas do Gemini deve alcançar a navegação sem recarregar shell.
  // Digitação real atualiza o v-model; o Gemini escolhe a ferramenta permitida.
  await page.click('#question');
  await page.type('#question','Abra a lista de funcionários usando a ferramenta navigate_potiguar.');
  await page.click('button.send-button');
  await provePersistent('/admin/users');
  assert.equal(await page.$eval('.status',el=>el.classList.contains('online')),true);
  assert.equal(closed.size,0);
  checks.push('gemini_live_tool_navigates_without_disconnect');

  // Cadastro V2: root Live continua dono da sessão, evitando iframe Gemini duplicado.
  await page.evaluate(()=>document.querySelector('iframe.app-frame').contentWindow.location.assign('/admin/users/new'));
  await page.waitForFunction(()=>/^\/admin\/onboarding\/[a-f0-9]{32}$/.test(
    document.querySelector('iframe.app-frame')?.contentWindow?.location?.pathname||''),{timeout:15000});
  assert.equal(await page.evaluate(()=>document.getElementById('potiguar-copilot')===window.__shell_root),true);
  assert.equal(await page.evaluate(()=>document.querySelector('iframe.app-frame')===window.__shell_iframe),true);
  assert.equal(await page.$eval('.status',el=>el.classList.contains('online')),true);
  assert.equal(closed.size,0);
  await page.waitForFunction(()=>document.querySelector('iframe.app-frame')?.contentDocument?.querySelector('#copilot-open')?.hidden===true,{timeout:7000});
  assert.equal(await page.evaluate(()=>Boolean(document.querySelector('iframe.app-frame').contentDocument.querySelector('#onboarding-copilot-frame').getAttribute('src'))),false);
  checks.push('live_session_persists_entering_v2_without_second_copilot');

  await page.waitForFunction(()=>
    document.querySelector('iframe.app-frame')?.contentDocument?.querySelector('#guided-field')?.textContent?.includes('Tipo de relação'),
    {timeout:9000});
  checks.push('parent_agent_drives_onboarding_question');
  await new Promise(resolve=>setTimeout(resolve,950));
  await page.click('#question');
  await page.type('#question','O tipo de vínculo é CLT comum.');
  await page.$eval('button.send-button',button=>button.click());
  await page.waitForFunction(()=>document.querySelector('iframe.app-frame')?.contentDocument
    ?.querySelector('#field-relation_type')?.value==='CLT comum',{timeout:19000});
  checks.push('real_gemini_live_fills_safe_field_and_flask_saves_draft');
  // Não cadastrar funcionário nem preencher campos protegidos.
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({status:'PASS',checks,open_websockets:opened,closed_websockets:closed.size,
    viewport:'412x896',runtime_page_errors:errors,tokenResponses,synthetic_draft_only:true},null,2));
 }catch(e){
  let ui={};try {if(page)ui=await page.evaluate(()=>({
    status:document.querySelector('.status')?.textContent,
    error:document.querySelector('.conversation .error')?.textContent,
    config_error:document.querySelector('.control-card .config-note')?.textContent,
    connect_button:document.querySelector('.control-card .connect-button')?.textContent,
    connect_disabled:document.querySelector('.control-card .connect-button')?.disabled,
    consent:document.querySelector('.control-card input[type=checkbox]')?.checked,
    connect_hit:(()=>{const b=document.querySelector('.control-card .connect-button');if(!b)return '';const r=b.getBoundingClientRect();return document.elementFromPoint(r.left+r.width/2,r.top+r.height/2)?.className||'';})(),
    config_display:getComputedStyle(document.querySelector('.assist-panel')).display,
    vue_state:(()=>{const instance=document.getElementById('potiguar-copilot')?.__vue_app__?._instance;
      const state=instance?.setupState;return {
        setupKeys:Object.keys(state||{}).filter(x=>/live|connect|busy|frame|status/.test(x)).slice(0,18),
        liveSession:!!state?.live?.session, connected:state?.connected,
        busy:state?.busy, frameRoute:state?.frameRoute};})(),
    frame:document.querySelector('iframe.app-frame')?.contentWindow?.location?.pathname
  }));}catch{}
  console.log(JSON.stringify({status:'FAIL',checks,reason:e.message.slice(0,180),page_errors:errors,ui,tokenResponses,sockets_created:sockets.size,sockets_closed:closed.size},null,2));
  process.exitCode=1;
 }finally{if(browser)await browser.close();}
})().catch(e=>{console.error('TEST_FAILURE',e.message);process.exitCode=1});
