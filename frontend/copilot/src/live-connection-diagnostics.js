/** Diagnósticos públicos, com enumeração estrita. Nunca incluir token, URL, reason nem erro bruto do SDK. */
export function safeCloseCode(event) {
  const code = event?.code;
  return Number.isInteger(code) && code >= 1000 && code <= 4999 ? code : null;
}

export function classifyLiveFailure({opened=false, closed=false, errored=false, closeCode=null, wasClean=null}={}) {
  // Apenas indicadores enumerados. Não revelar URL, hostname, token, reason ou SDK Error.
  // Antes/depois da abertura é uma evidência, não diagnóstico definitivo de proxy.
  const phase = opened ? 'APOS_ABERTURA' : 'ANTES_ABERTURA';
  const clean = wasClean === true ? 'LIMPO' : wasClean === false ? 'ANORMAL' : 'DESCONHECIDO';
  const suffix = ` abertura=${phase}; fechamento=${clean}.`;
  if (closed) {
    if (closeCode === 1008)
      return 'O WebSocket foi encerrado com código 1008; investigar política ou configuração [LIVE_WS_CLOSE_1008].' + suffix;
    if (closeCode === 1006)
      return 'A conexão WebSocket terminou anormalmente, sem causa confirmada [LIVE_WS_CLOSE_1006].' + suffix;
    if (closeCode === 1011)
      return 'O WebSocket encerrou com código 1011 (erro interno informado) [LIVE_WS_CLOSE_1011].' + suffix;
    return `O WebSocket Live foi encerrado [LIVE_WS_CLOSE_${closeCode ?? 'UNKNOWN'}].` + suffix;
  }
  if (errored)
    return 'Falha no transporte WebSocket; causa não disponível ao navegador [LIVE_WS_ERROR].' + suffix;
  if (!opened)
    return 'WebSocket não abriu; verifique política, proxy, rede ou destino [LIVE_WS_OPEN_FAILED].' + suffix;
  return 'WebSocket abriu, mas o SDK não concluiu a negociação Live [LIVE_WS_SETUP_FAILED].' + suffix;
}

export function liveSessionClosedMessage(attempt) {
  return classifyLiveFailure({...attempt,closed:true}) + ' Inicie outra conversa manualmente, após o intervalo de segurança.';
}
