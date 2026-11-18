import { fold, resolveOnboardingAnswer } from './onboarding-natural-language.js';
import { isProtectedInput } from './protected-input.js';

// Contrato espelhado do backend; o servidor é a fonte de autorização definitiva.
const ALLOWED = Object.freeze({
  0: Object.freeze({relation_type: ['CLT comum','CLT intermitente','Sem vínculo empregatício']}),
  1: Object.freeze({full_name: ['Teste Funcionário de Teste','Teste Operador de Teste']}),
  2: Object.freeze({country: ['Brasil'],address_type:['Urbano','Rural','Exterior']}),
  3: Object.freeze({transport_benefit:['Sim','Não']}),
});

export function safeTextCandidate(step, field, raw) {
  if (!Number.isInteger(step) || typeof field !== 'string' || typeof raw !== 'string') return null;
  const choices = ALLOWED[step]?.[field];
  if (!choices || !raw.trim() || raw.length > 90 || isProtectedInput(raw)) return null;
  // Instruções livres, telefones, dígitos, URLs, e-mails e múltiplos campos são proibidos.
  if (/[\d@\/:<>={}\[\]#\n\r]/.test(raw)) return null;
  const normalized = fold(raw);
  const exact = choices.find(choice => fold(choice) === normalized);
  if (exact) return exact;
  if (field === 'full_name' || field === 'country') return null;
  const prefix = /^(?:quero |escolho |selecionar |selecione |coloque |marque )/;
  const candidate = prefix.test(normalized) ? normalized.replace(prefix,'') : normalized;
  // Só aliases curtos reconhecidos, nunca enviar a frase original ao servidor.
  if (candidate.split(' ').length > 6) return null;
  const resolved = resolveOnboardingAnswer(field, candidate, choices);
  return choices.includes(resolved) ? resolved : null;
}

export async function requestTextTurn({step,field,candidate,requestId,consent}, fetchFn=fetch) {
  if (consent !== true || !candidate || !requestId) throw new Error('Confirme o consentimento do modo texto.');
  const csrfResponse = await fetchFn('/admin/copilot/csrf-token', {
    credentials:'same-origin',cache:'no-store',headers:{Accept:'application/json'},
  }).catch(()=>{throw new Error('Falha de rede na validação CSRF [TEXT_CSRF_NETWORK].');});
  if (!csrfResponse.ok) throw new Error('Sessão não validada [TEXT_CSRF_HTTP].');
  const csrf = await csrfResponse.json().catch(()=>({}));
  if (!csrf?.csrf_token) throw new Error('Sessão sem CSRF [TEXT_CSRF_INVALID].');
  const response = await fetchFn('/admin/copilot/text-turn', {
    method:'POST',credentials:'same-origin',cache:'no-store',
    headers:{'Content-Type':'application/json','X-CSRFToken':csrf.csrf_token},
    body:JSON.stringify({step,field,candidate,request_id:requestId,consent:true}),
  }).catch(()=>{throw new Error('Falha de rede na sugestão HTTPS [TEXT_NETWORK].');});
  const payload = await response.json().catch(()=>({}));
  if (!response.ok) {
    if (response.status === 429) throw new Error('Limite ou intervalo de mensagens atingido. Aguarde antes de tentar [TEXT_429].');
    if (response.status === 409) throw new Error('Solicitação duplicada. Não foi reenviada à IA [TEXT_409].');
    if (response.status === 401 || response.status === 403) throw new Error('Sessão sem permissão [TEXT_AUTH].');
    if (response.status === 422) throw new Error('Campo não permitido para modo texto [TEXT_422].');
    throw new Error('Serviço textual indisponível [TEXT_HTTP_ERROR].');
  }
  const proposal=payload?.proposal;
  if (payload?.mode !== 'https_text' || payload.model_type !== 'text_not_live'
      || payload.request_id !== requestId || proposal?.step !== step
      || proposal?.field !== field || proposal?.value !== candidate) {
    throw new Error('Resposta textual não corresponde ao campo atual [TEXT_BAD_RECEIPT].');
  }
  return {proposal,mode:payload.mode};
}
