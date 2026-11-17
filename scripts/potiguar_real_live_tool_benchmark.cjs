#!/usr/bin/env node
// Avaliação real do modelo 3.8 Live com tool calling em linguagem natural (somente dados fictícios).
// Os tokens efêmeros são provisionados pelo cofre local e nunca vão aos relatórios.
const cp=require('node:child_process');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..');
let GoogleGenAI,Modality;
try {
  ({GoogleGenAI,Modality}=require(require.resolve('@google/genai',{
    paths:[path.join(root,'frontend/copilot')]
  })));
} catch(error) {
  console.error('Dependência @google/genai não instalada no checkout ativo. Execute: npm ci --prefix frontend/copilot');
  process.exit(2);
}
const cases=[
 {id:'nav_dashboard',mode:'nav',text:'Por favor, abre o painel principal agora.',tool:'navigate_potiguar',destination:'dashboard'},
 {id:'nav_employees',mode:'nav',text:'Quero ir para a lista de funcionários.',tool:'navigate_potiguar',destination:'employees'},
 {id:'clt_intermitente',mode:'form',text:'Eu sou CLT intermitente.',tool:'suggest_onboarding_fields',value:'CLT intermitente'},
 {id:'contrato_convocacao',mode:'form',text:'Meu contrato de trabalho é por convocação.',tool:'suggest_onboarding_fields',value:'CLT intermitente'},
 {id:'clt_normal',mode:'form',text:'Pode colocar CLT normal.',tool:'suggest_onboarding_fields',value:'CLT comum'},
 {id:'autonomo',mode:'form',text:'Sou trabalhador autônomo, sem vínculo empregatício.',tool:'suggest_onboarding_fields',value:'Sem vínculo empregatício'},
 {id:'question',mode:'form',text:'Qual é a diferença entre CLT comum e intermitente?',tool:null},
 {id:'negation',mode:'form',text:'Não é intermitente. Ainda não escolhi a modalidade.',tool:null},
 {id:'save_draft',mode:'form',text:'Salve o rascunho agora.',tool:'operate_onboarding',action:'save_draft'},
];
function shortToken(){
 const command=[
  'import os,sys',
  'from services.credential_portal.vault import load_gemini_api_key',
  'from app.copilot.live import provision_live_token',
  'k=load_gemini_api_key(os.environ["POTIGUAR_COPILOT_VAULT_DIR"])',
  'sys.stdout.write(provision_live_token(k,"gemini-3.8-live"))',
 ].join(';');
 return cp.execFileSync('docker',['exec','potiguar-copilot-mobile-hml-20261113',
    'python','-c',command],{encoding:'utf8',timeout:15000,stdio:['ignore','pipe','pipe']}).trim();
}
(async()=>{
 const {onboardingSuggestionTool}=await import(pathToFileURL(path.join(root,'frontend/copilot/src/onboarding-suggestions.js')).href);
 const {appNavigationTool}=await import(pathToFileURL(path.join(root,'frontend/copilot/src/app-navigation.js')).href);
 const output=[],begin=Date.now();
 for(const sample of cases){
   let session,settle;
   const state={id:sample.id,expected:sample.tool,received:[],latencyMs:null,toolResult:'no_call'};
   let isDone=false,timer;
   const done=new Promise(resolve=>settle=resolve);
   const finish=(reason)=>{
      if(isDone)return;isDone=true;clearTimeout(timer);state.reason=reason;settle();
   };
   try{
     const ephemeral=shortToken();
     const ai=new GoogleGenAI({apiKey:ephemeral,httpOptions:{apiVersion:'v1alpha'}});
     const tools=sample.mode==='form' ?
       {functionDeclarations:[...onboardingSuggestionTool.functionDeclarations,...appNavigationTool.functionDeclarations]} :
       appNavigationTool;
     const instruction=sample.mode==='form' ?
       ['Você é o Copiloto Potiguar e está no formulário V2 na etapa 0, campo relation_type.',
        'Apenas o campo relation_type está ativo e é seguro. Opções exatas: CLT comum, CLT intermitente, Sem vínculo empregatício.',
        'Fale apenas português brasileiro. Se o usuário declarar seu vínculo de forma inequívoca, invoque suggest_onboarding_fields etapa 0 para relation_type, exatamente o valor correto.',
        'Se pedir para salvar, use operate_onboarding action save_draft.',
        'Se fizer uma pergunta conceitual ou disser uma negação sem informar opção positiva, não preencha e não chame ferramentas. Nunca invente dados.',
        'Aguarde recibo de ferramenta antes de confirmar salvamento.']
       .join(' ') :
       'Você é o Copiloto Potiguar pt-BR. Se o usuário pedir abertura de tela, use navigate_potiguar com o destino permitido. Não invente sucesso.';
     const start=Date.now();
     session=await ai.live.connect({
       model:'gemini-3.8-live',
       config:{responseModalities:[Modality.AUDIO],tools:[tools],systemInstruction:instruction},
       callbacks:{
         onopen:()=>{},
         onmessage:(msg)=>{
           for(const call of msg.toolCall?.functionCalls||[]){
             let args;try{args=typeof call.args==='string'?JSON.parse(call.args):call.args;}catch{args=null}
             state.received.push({name:call.name,
               destination:args?.destination??null,action:args?.action??null,
               step:args?.step??null,field:args?.suggestions?.[0]?.field??null,
               value:args?.suggestions?.[0]?.value??null});
             try{session?.sendToolResponse({functionResponses:[{id:call.id,name:call.name,
               response:{status:sample.tool===call.name?'saved':'denied',created:false}}]});}catch{}
             state.latencyMs=Date.now()-start;
             finish('tool_call');
           }
           if(msg.serverContent?.turnComplete)finish('turn_complete');
         },
         onerror:()=>finish('provider_error'),
         onclose:()=>finish('connection_closed'),
       }
     });
     timer=setTimeout(()=>finish('timeout'),9000);
     session.sendClientContent({turns:[{role:'user',parts:[{text:sample.text}]}],turnComplete:true});
     await done;
     const first=state.received[0];
     const correct=sample.tool===null?!first:
       !!first && first.name===sample.tool &&
       (sample.destination===undefined||first.destination===sample.destination)&&
       (sample.action===undefined||first.action===sample.action)&&
       (sample.value===undefined||first.value===sample.value);
     state.toolResult=sample.tool===null && !first && state.reason==='timeout'
       ? 'inconclusive' : correct?'pass':'fail';
   }catch(error){
     state.reason='sdk_or_quota_error';state.toolResult='error';state.errorType=error.name;
     // Quota/token errors should stop early rather than retry aggressively.
     if(output.length>=2){output.push(state);break}
   }finally{
     clearTimeout(timer);
     try{session?.close()}catch{}
   }
   output.push(state);
 }
 const summary={model:'gemini-3.8-live',apiVersion:'v1alpha',cases:output.length,
   success:output.filter(c=>c.toolResult==='pass').length,
   incorrect:output.filter(c=>c.toolResult==='fail').length,
   inconclusive:output.filter(c=>c.toolResult==='inconclusive').length,
   errors:output.filter(c=>c.toolResult==='error').length,
   durationMs:Date.now()-begin,
   results:output,
   note:'Cada cenário utiliza nova sessão real Gemini Live e somente dados sintéticos. Sem escrita em banco.'};
 console.log(JSON.stringify(summary,null,2));
 process.exitCode=summary.incorrect||summary.errors?1:0;
})().catch(e=>{console.log(JSON.stringify({status:'ERROR',errorType:e.name}));process.exitCode=2});
