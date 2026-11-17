/** Smoke Google Live com funcionário 100% fictício; nunca grava cadastros. */
import {GoogleGenAI,Modality,StartSensitivity,EndSensitivity} from '@google/genai';
import {registrationTool, REGISTRATION_FUNCTION_NAME} from './src/registration.js';

let input='';
process.stdin.setEncoding('utf8');
for await(const chunk of process.stdin) input+=chunk;
const {token,model}=JSON.parse(input);
if (!token||!['gemini-3.8-live','gemini-3.8-live-extended-thinking'].includes(model)) {
  throw new Error('Invalid synthetic test input');
}
const state={model,connected:false,tool_called:false,tool_name_ok:false,returned_draft:false,denied_automatic_creation:true,turn_complete:false};
const ai=new GoogleGenAI({apiKey:token,httpOptions:{apiVersion:'v1beta'}});
let session=null,done=false;
let resolver;
const result=new Promise(r=>{resolver=r;});
const finish=(reason)=>{if(!done){done=true;resolver(reason);}};
const timer=setTimeout(()=>finish('TIMEOUT'),30000);
try{
  session=await ai.live.connect({
    model,
    config:{
      responseModalities:[Modality.AUDIO],
      systemInstruction:'Você é Copiloto Potiguar. Quando o usuário pedir o cadastro, você deve chamar a ferramenta prepare_employee_registration apenas para preparar RASCUNHO; a ferramenta NUNCA cadastra. Não diga que cadastrou.',
      tools:[registrationTool],
      ...(model.endsWith('extended-thinking') ? {thinkingConfig:{thinkingLevel:'low'}} : {}),
      realtimeInputConfig:{automaticActivityDetection:{
        disabled:false,
        startOfSpeechSensitivity:StartSensitivity.START_SENSITIVITY_LOW,
        endOfSpeechSensitivity:EndSensitivity.END_SENSITIVITY_LOW,
        prefixPaddingMs:220,
        silenceDurationMs:750,
      }},
    },
    callbacks:{
      onopen(){state.connected=true;},
      onmessage(msg){
        if(msg.toolCall?.functionCalls?.length){
          state.tool_called=true;
          for(const c of msg.toolCall.functionCalls){
            state.tool_name_ok ||= c.name===REGISTRATION_FUNCTION_NAME;
            const args= typeof c.args==='string'?JSON.parse(c.args):c.args;
            if(args?.name && String(args.name).toLowerCase().includes('maria'))state.returned_draft=true;
            session?.sendToolResponse({functionResponses:[{
              id:c.id,name:c.name,response:{status:'awaiting_human_review',created:false},
            }]});
          }
          finish('TOOL_CALL_RECEIVED');
        }
        if(msg.serverContent?.turnComplete)state.turn_complete=true;
      },
      onerror(){finish('GOOGLE_LIVE_ERROR');},
      onclose(){finish('CLOSED');},
    },
  });
  session.sendClientContent({turns:[{role:'user',parts:[{text:'Por favor, cadastre a funcionária fictícia Maria de Teste, usuário maria.teste, matrícula TEST-101 e função atendente. Prepare o rascunho para minha revisão.'}]}],turnComplete:true});
  const outcome=await result;
  console.log(JSON.stringify({...state,outcome}));
  if(!state.connected||!state.tool_called||!state.tool_name_ok||!state.returned_draft)process.exitCode=5;
}catch(e){
  console.log(JSON.stringify({model,outcome:'CONNECT_EXCEPTION',error_type:e?.name || 'Error'}));
  process.exitCode=4;
}finally{
  clearTimeout(timer);
  try{session?.close();}catch{}
}
