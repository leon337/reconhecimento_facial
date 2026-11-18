import test from 'node:test';
import assert from 'node:assert/strict';
import { PotiguarLive } from '../src/live.js';
import { safeCloseCode, classifyLiveFailure } from '../src/live-connection-diagnostics.js';

const MODELS=['gemini-3.8-live','gemini-3.8-live-extended-thinking'];
const fakeResponse=(status,body)=>({ok:status>=200 && status<300,status,json:async()=>body});

function scenario({model=MODELS[0],tokenStatus=200,tokenBody,transport='success'}={}) {
  const events=[],requests=[],callbacks=[],created=[];
  const fetchFn=async(url,params)=>{
    requests.push({path:url,method:params?.method||'GET'});
    if(url.endsWith('/csrf-token'))return fakeResponse(200,{csrf_token:'TEST-CSRf'});
    if(url.endsWith('/session-token'))return fakeResponse(tokenStatus,tokenBody ?? (
      tokenStatus===200 ? {token:'EPHEMERAL_SECRET_NOT_FOR_LOGS',model} : {error:'Aguarde antes de iniciar outra sessão.'}
    ));
    throw Error('Unexpected endpoint');
  };
  const createClient=(token)=>{
    created.push(token.length);
    return {live:{connect:async({callbacks:cb})=>{
      callbacks.push(cb);
      if(transport==='reject')throw Error('SECRET_RAW_VENDOR_ERROR_SHOULD_NOT_LEAK');
      cb.onopen();
      if(transport==='close-1008'){
        cb.onclose({code:1008,reason:'SECRET_REASON_SHOULD_NOT_LEAK'});
        throw Error('SECRET_RAW_CLOSE_ERROR_SHOULD_NOT_LEAK');
      }
      if(transport==='error-before-ready'){
        cb.onerror({message:'SECRET_ERROR_EVENT_SHOULD_NOT_LEAK'});
        return {close(){}};
      }
      cb.onmessage({setupComplete:{}});
      return {close(){events.push('session.close')}};
    }}};
  };
  const live = new PotiguarLive({
    onStatus:status=>events.push(status),
    onStatusDetail:detail=>events.push(detail),
    onError:error=>events.push(error),
  },{fetchFn,createClient});
  return {live,events,requests,callbacks,created};
}
const connect=(s,model=MODELS[0])=>s.live.connect(model,'unused',{
  allowOnboardingSuggestions:true,persistentShell:false
});

test('Live e Extended conectam uma vez com token efêmero e configuração autorizada',async()=>{
  for(const model of MODELS){
    const s=scenario({model});
    await connect(s,model);
    assert.equal(s.requests.filter(r=>r.path.endsWith('/session-token')).length,1);
    assert.equal(s.created.length,1);
    assert(s.events.includes('websocket_aberto'));
    assert(s.events.includes('setup_live_confirmado'));
    assert(s.events.includes('connected'));
    assert.equal(s.live.session!==null,true);
    await s.live.disconnect();
  }
});

test('erro de transporte pré-handshake não expõe mensagens, chaves, URLs ou tokens do SDK',async()=>{
  const s=scenario({transport:'reject'});
  await assert.rejects(connect(s),error=>{
    assert.match(error.message,/LIVE_WS_OPEN_FAILED/);
    assert.doesNotMatch(error.message,/SECRET|EPHEMERAL/);
    return true;
  });
  assert.equal(s.requests.filter(r=>r.path.endsWith('/session-token')).length,1,
    'não repetir requisição automaticamente');
  assert.equal(s.live.session,null);
});

test('fechamento 1008 identifica negociação recusada, sem expor reason',async()=>{
  const s=scenario({transport:'close-1008'});
  await assert.rejects(connect(s),error=>{
    assert.match(error.message,/LIVE_WS_CLOSE_1008/);
    assert.doesNotMatch(error.message,/SECRET/);
    return true;
  });
  assert.equal(s.live.session,null);
});

test('onerror durante negociação não exibe erro bruto e não sinaliza connected',async()=>{
  const s=scenario({transport:'error-before-ready'});
  await assert.rejects(connect(s),/LIVE_WS_ERROR/);
  assert(!s.events.includes('connected'));
  assert.equal(s.live.session,null);
});

test('HTTP 429 continua política do servidor; sem fallback ou repetição de token',async()=>{
  const s=scenario({tokenStatus:429});
  await assert.rejects(connect(s),/LIVE_TOKEN_HTTP_429/);
  assert.equal(s.requests.filter(r=>r.path.endsWith('/session-token')).length,1);
  assert.equal(s.created.length,0);
});

test('token de modelo divergente é negado antes de abrir WebSocket',async()=>{
  const s=scenario({tokenBody:{model:MODELS[1],token:'EPHEMERAL_SECRET_NOT_FOR_LOGS'}});
  await assert.rejects(connect(s),/LIVE_TOKEN_INVALID/);
  assert.equal(s.created.length,0);
});

test('código WebSocket 1006 gera mensagem útil, apenas com enumeração segura',async()=>{
  const s=scenario();
  await connect(s);
  s.callbacks[0].onclose({code:1006,reason:'DO_NOT_EXPOSE_PRIVATE_DATA'});
  assert.equal(s.live.session,null);
  assert(s.events.some(e=>String(e).includes('LIVE_WS_CLOSE_1006')));
  assert(!JSON.stringify(s.events).includes('DO_NOT_EXPOSE_PRIVATE_DATA'));
  assert(s.events.includes('disconnected'));
});

test('callback atrasado de conexão antiga não derruba a nova sessão',async()=>{
  const s=scenario();
  await connect(s);
  const stale=s.callbacks[0];
  await s.live.disconnect();
  await connect(s);
  const newSession=s.live.session;
  stale.onclose({code:1006,reason:'OLD_CLOSE_SHOULD_NOT_AFFECT_NEW'});
  assert.strictEqual(s.live.session,newSession);
  assert.equal(s.events.at(-1),'connected');
});

test('código de fechamento só admite inteiros conhecidos pelo protocolo',()=>{
  assert.equal(safeCloseCode({code:1006,reason:'secret'}),1006);
  assert.equal(safeCloseCode({code:'1006'}),null);
  assert.equal(safeCloseCode(null),null);
  assert.match(classifyLiveFailure({opened:true,closed:true,closeCode:1008}),/1008/);
  assert.doesNotMatch(classifyLiveFailure({opened:true,closed:true,closeCode:1008}),/secret/);
});

test('falha no inicializador do SDK nunca revela token nem exceção interna',async()=>{
  const s=scenario();
  s.live.createClient=()=>{throw Error('EPHEMERAL_SECRET_NOT_FOR_LOGS');};
  await assert.rejects(connect(s),error=>{
    assert.match(error.message,/LIVE_SDK_INIT/);
    assert.doesNotMatch(error.message,/EPHEMERAL|SECRET/);
    return true;
  });
});
test('payload nulo não provoca TypeError e não abre conexão',async()=>{
  const s=scenario({tokenBody:null});
  // A fixture padrão usa coalescência; substituir fetch no teste.
  s.live.fetchFn=async url=>url.endsWith('/csrf-token')
    ? fakeResponse(200,{csrf_token:'CSRF_TEST'}) : fakeResponse(200,null);
  await assert.rejects(connect(s),/LIVE_TOKEN_INVALID/);
});
