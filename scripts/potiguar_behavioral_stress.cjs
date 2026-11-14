#!/usr/bin/env node
// Testes sintéticos de linguagem natural + execução de ferramentas, com verificação vetorizada via Vulkan/ANGLE.
// Não envia CPF, credenciais ou dados reais ao Gemini. O modelo remoto é testado em E2E separado.
const {createRequire}=require('node:module');
const {pathToFileURL}=require('node:url');
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const requireLocal=createRequire(__filename);
const puppeteer=requireLocal(process.env.POTIGUAR_PUPPETEER_MODULE||'puppeteer');
const ROOT=path.join(__dirname,'..');
const argv=process.argv.slice(2);
const scenarios=Number(argv[0]||40000);
if(!Number.isInteger(scenarios)||scenarios<1000||scenarios>200000)throw Error('scenario_count_out_of_bounds');
const variants={
  common:['CLT comum','clt normal','clt padrão','CLT tradicional','clt regular'],
  intermittent:['CLT intermitente','intermitente','contrato intermitente',
   'regime intermitente','trabalho por convocação','contrato por convocação'],
  autonomous:['sem vínculo','sem vínculo empregatício','prestador autônomo',
    'trabalhador autônomo','prestação de serviços sem vínculo'],
};
const sentences=['%v','sou %v','o regime é %v','o contrato é %v',
  'coloca %v','pode colocar %v','É %v.','quero %v','seleciona %v'];
const cases=[],failExamples=[];
let rng=0x4cf337;
const next=()=>{rng=(Math.imul(rng,1664525)+1013904223)>>>0;return rng};
function push(field,utterance,expected,options){cases.push({field,utterance,expected,options});}
for(let i=0;i<scenarios;i++){
  const category=i%8,seed=next();
  if(category<5){
    const names=Object.keys(variants),name=names[(seed>>>5)%names.length];
    const base=variants[name][(seed>>>11)%variants[name].length];
    const sent=sentences[(seed>>>19)%sentences.length].replace('%v',base);
    push('relation_type',sent,({common:'CLT comum',intermittent:'CLT intermitente',
      autonomous:'Sem vínculo empregatício'})[name],
      ['CLT comum','CLT intermitente','Sem vínculo empregatício']);
  }else if(category===5){
    const bad=['qual a diferença entre CLT comum e intermitente?',
      'é CLT comum ou intermitente?','não é intermitente',
      'me explica o contrato intermitente','qual é o tipo de relação?',
      'terceirizado','não, nunca fui CLT comum',
      'quero ver as opções CLT comum e intermitente'];
    push('relation_type',bad[seed%bad.length],null,
      ['CLT comum','CLT intermitente','Sem vínculo empregatício']);
  }else if(category===6){
    const opts=['Urbano','Rural','Exterior'],names=['zona urbana','área rural','no exterior'];
    const idx=seed%3;
    push('address_type',names[idx],opts[idx],opts);
  }else{
    const opts=['Não','Sim'];const positive=['sim','quero vale transporte','recebo vale transporte'];
    const negative=['não','não preciso de vale transporte','dispenso vale transporte'];
    const kind=seed%2;
    push('transport_benefit',(kind?positive:negative)[(seed>>>8)%3],kind?'Sim':'Não',opts);
  }
}
(async()=>{
  const {resolveNaturalSelect}=await import(pathToFileURL(path.join(ROOT,'frontend/copilot/src/onboarding-natural-language.js')).href);
  const {sanitizeOnboardingSuggestions}=await import(pathToFileURL(path.join(ROOT,'frontend/copilot/src/onboarding-suggestions.js')).href);
  const {PotiguarLive}=await import(pathToFileURL(path.join(ROOT,'frontend/copilot/src/live.js')).href);
  const start=process.hrtime.bigint();
  let falsePositive=0,falseNegative=0,wrongValue=0,passtotal=0,toolDenied=0,toolExecuted=0,toolFailed=0;
  const codes=new Uint8Array(cases.length*4);
  const codeOf={null:0,'CLT comum':1,'CLT intermitente':2,'Sem vínculo empregatício':3,
    Urbano:4,Rural:5,Exterior:6,Não:7,Sim:8};
  cases.forEach((row,i)=>{
    const got=resolveNaturalSelect(row.field,row.utterance,row.options);
    if(got===row.expected)passtotal++;
    else {
      if(got===null)falseNegative++;else if(row.expected===null)falsePositive++;else wrongValue++;
      if(failExamples.length<12)failExamples.push({field:row.field,utterance:row.utterance,
        expected:row.expected,actual:got});
    }
    codes[i*4]=codeOf[String(row.expected)]||0;
    codes[i*4+1]=codeOf[String(got)]||0;
    codes[i*4+3]=255;
  });
  // Exercitar ferramentas reais do executor, ainda sem rede.
  const packets=[];
  const live=new PotiguarLive({
    onOnboardingSuggestions:async()=>({status:'saved',step:0}),
    onOnboardingAction:async()=>({status:'saved',step:0}),
    onAppNavigation:async()=>({status:'navigated'}),
  });
  live.allowAppNavigation=true;live.allowOnboardingSuggestions=true;live.allowEmployeeActions=true;
  live.session={sendToolResponse(r){packets.push(r)}};
  for(let i=0;i<1200;i++){
    live.setOnboardingMode(true);live.setOnboardingStep(0);live.setOnboardingField('relation_type');
    const word=variants.intermittent[i%variants.intermittent.length];
    await live.handleToolCalls([{id:String(i),name:'suggest_onboarding_fields',
      args:{step:0,suggestions:[{field:'relation_type',value:word}]}}]);
    const status=packets.at(-1).functionResponses[0].response.status;
    if(status==='saved')toolExecuted++;
    else if(failExamples.length<12)failExamples.push({tool:'valid',status});
    await live.handleToolCalls([{id:'forbidden'+i,name:'operate_onboarding',args:{action:'complete'}}]);
    if(packets.at(-1).functionResponses[0].response.status==='denied')toolDenied++;
    live.handlers.onOnboardingSuggestions=async()=>{throw Error('simulated_backend_failure')};
    await live.handleToolCalls([{id:'fail'+i,name:'suggest_onboarding_fields',
      args:{step:0,suggestions:[{field:'relation_type',value:word}]}}]);
    if(packets.at(-1).functionResponses[0].response.status==='execution_failed')toolFailed++;
    live.handlers.onOnboardingSuggestions=async()=>({status:'saved',step:0});
  }
  const elapsedMs=Number(process.hrtime.bigint()-start)/1e6;
  // Checagem massiva dos pares esperados/reais em pipeline WebGL2, com ANGLE/Vulkan RADV.
  let browser,gpu=null;
  try {
    browser=await puppeteer.launch({headless:true,executablePath:'/usr/bin/google-chrome',
      args:['--no-sandbox','--disable-dev-shm-usage','--enable-features=Vulkan',
        '--use-angle=vulkan','--disable-software-rasterizer']});
    const page=await browser.newPage();
    const session=await browser.target().createCDPSession();
    const info=await session.send('SystemInfo.getInfo');
    const adapter=(info.gpu?.devices||[])[0]||{};
    const hardware=adapter.deviceString||'';
    const width=512,height=Math.ceil(cases.length/width);
    if(height>4096)throw Error('gpu_texture_bounds');
    const gpuData=Array.from(codes);
    const t=Date.now();
    gpu=await page.evaluate(({width,height,gpuData,n})=>{
      const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
      const gl=canvas.getContext('webgl2',{preserveDrawingBuffer:true,antialias:false,
        powerPreference:'high-performance'});
      if(!gl)return {supported:false};
      const source=(type,code)=>{
        const shader=gl.createShader(type);gl.shaderSource(shader,code);gl.compileShader(shader);
        if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(shader));
        return shader;
      };
      const vert=source(gl.VERTEX_SHADER,`#version 300 es
      void main(){vec2 v[3]=vec2[3](vec2(-1.,-1.),vec2(3.,-1.),vec2(-1.,3.));
      gl_Position=vec4(v[gl_VertexID],0.,1.);}`);
      const frag=source(gl.FRAGMENT_SHADER,`#version 300 es
      precision highp float;uniform sampler2D inputValues;out vec4 fragColor;
      void main(){ivec2 p=ivec2(gl_FragCoord.xy);vec4 entry=texelFetch(inputValues,p,0);
      float valid=abs(entry.r-entry.g)<0.001?1.0:0.0;fragColor=vec4(valid,0.,0.,1.);}`);
      const program=gl.createProgram();gl.attachShader(program,vert);gl.attachShader(program,frag);
      gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))
        throw Error(gl.getProgramInfoLog(program));
      gl.useProgram(program);
      const values=new Uint8Array(width*height*4);values.set(gpuData);
      for(let i=n;i<width*height;i++){values[4*i]=0;values[4*i+1]=0;values[4*i+3]=255}
      const input=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,input);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA8,width,height,0,gl.RGBA,gl.UNSIGNED_BYTE,values);
      gl.uniform1i(gl.getUniformLocation(program,'inputValues'),0);
      const output=new Uint8Array(width*height*4);
      gl.viewport(0,0,width,height);gl.drawArrays(gl.TRIANGLES,0,3);
      gl.finish();gl.readPixels(0,0,width,height,gl.RGBA,gl.UNSIGNED_BYTE,output);
      const error=gl.getError();let pass=0;
      for(let i=0;i<n;i++)if(output[i*4]===255)pass++;
      return {supported:true,pass,fail:n-pass,glError:error,
        renderer:gl.getParameter(gl.RENDERER),maxTexture:gl.getParameter(gl.MAX_TEXTURE_SIZE)};
    },{width,height,gpuData,n:cases.length});
    gpu.chromeDevice=hardware;gpu.wallMs=Date.now()-t;
    gpu.hardwareAccelerated=/AMD.*Radeon.*RADV/i.test(hardware);
  }catch(e){gpu={supported:false,errorType:e.name,errorMessage:String(e.message).slice(0,160)}}
  finally{await browser?.close();}
  const report={scenarioCount:cases.length,pass:passtotal,falsePositive,falseNegative,wrongValue,
    passRate:+(passtotal/cases.length*100).toFixed(3),cpuElapsedMs:+elapsedMs.toFixed(2),
    toolCalls:3600,toolExecuted,toolDenied,toolFailed,gpu,failExamples,
    note:'Casos sintéticos e execução simulada de ferramentas; não equivalem a 40 mil chamadas ao Gemini.'};
  console.log(JSON.stringify(report,null,2));
  if(falsePositive||wrongValue||falseNegative||toolExecuted!==1200||toolDenied!==1200||toolFailed!==1200||
     (gpu?.supported && gpu.fail>0))process.exitCode=1;
})().catch(err=>{console.error('FATAL',err.stack);process.exitCode=2});
