'use strict';
const http=require('node:http');
const fs=require('node:fs'),path=require('node:path');
const puppeteer=require(process.env.POTIGUAR_PUPPETEER_MODULE || 'puppeteer');
const root=path.resolve(__dirname,'..');
const server=http.createServer((req,res)=>{
 const routes={'/src/audio.js':'frontend/copilot/src/audio.js','/src/vad.js':'frontend/copilot/src/vad.js','/static/copilot/pcm-worklet.js':'static/copilot/pcm-worklet.js'};
 let body,typ;
 if(req.url==='/'){body=Buffer.from('<!DOCTYPE html><html lang="pt-BR"><body><h1>Teste de microfone</h1><script type="module">import {Microphone} from "/src/audio.js";window.PotiguarMicrophone=Microphone;</script></body></html>');typ='text/html';}
 else if(routes[req.url]){body=fs.readFileSync(path.resolve(root,routes[req.url]));typ='application/javascript';}
 else {res.writeHead(404);return res.end('not found')}
 res.writeHead(200,{'Content-Type':typ,'Cache-Control':'no-store'});res.end(body);
});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));let browser;
 try{
  browser=await puppeteer.launch({headless:true,executablePath:process.env.POTIGUAR_CHROME_BIN || '/usr/bin/google-chrome',args:['--no-sandbox','--disable-dev-shm-usage','--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream','--autoplay-policy=no-user-gesture-required']});
  const page=await browser.newPage();
  await page.setViewport({width:412,height:896,isMobile:true,hasTouch:true});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:'+server.address().port+'/',{waitUntil:'networkidle0'});
  await page.waitForFunction(()=>!!window.PotiguarMicrophone,{timeout:7000});
  const metrics=await page.evaluate(async()=>{
   let frames=0,bytes=0,lastMime='',speechEvents=[];
   const mic=new window.PotiguarMicrophone(pcm=>{frames++;bytes+=pcm.data.length;lastMime=pcm.mimeType},{mode:'manual',onSpeechState:e=>speechEvents.push(e)});
   await mic.start();
   await new Promise(resolve=>setTimeout(resolve,1400));
   const before=frames;
   await mic.stop();
   await new Promise(resolve=>setTimeout(resolve,150));
   return {secure_context:window.isSecureContext,device_api:!!navigator.mediaDevices?.getUserMedia,
    frames,frames_before_stop:before,base64_chars:bytes,pcm_mime:lastMime,
    context_closed:mic.context===null,stream_closed:mic.stream===null,speech_events:speechEvents};
  });
  metrics.viewport='412x896';metrics.js_errors=errors;
  metrics.status=metrics.secure_context&&metrics.frames>0&&metrics.frames_before_stop===metrics.frames&&metrics.pcm_mime==='audio/pcm;rate=16000'&&metrics.context_closed&&!errors.length?'PASS':'FAIL';
  console.log(JSON.stringify(metrics,null,2));if(metrics.status!=='PASS')process.exitCode=2;
 }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(e=>{console.log(JSON.stringify({status:'FAIL',error_type:e.name,error_message:String(e.message).slice(0,130)}));process.exitCode=3});
