/** Diagnósticos públicos, com enumeração estrita. Nunca incluir token, URL, reason nem erro bruto do SDK. */
export function safeCloseCode(event) {
  const code = event?.code;
  return Number.isInteger(code) && code >= 1000 && code <= 4999 ? code : null;
}

export function classifyLiveFailure({opened=false, closed=false, errored=false, closeCode=null}={}) {
  if (closed) {
    if (closeCode === 1008)
      return 'O provedor recusou a configuração ou a política da sessão Live [LIVE_WS_CLOSE_1008].';
    if (closeCode === 1006)
      return 'A conexão WebSocket foi interrompida pela rede ou navegador [LIVE_WS_CLOSE_1006].';
    if (closeCode === 1011)
      return 'O serviço de voz encerrou a sessão por falha interna [LIVE_WS_CLOSE_1011].';
    return `O WebSocket Live foi encerrado antes da inicialização [LIVE_WS_CLOSE_${closeCode ?? 'UNKNOWN'}].`;
  }
  if (errored)
    return 'Falha de transporte na conexão Live. Verifique permissões de rede/WebSocket [LIVE_WS_ERROR].';
  if (!opened)
    return 'O navegador não conseguiu abrir o WebSocket do modelo [LIVE_WS_OPEN_FAILED].';
  return 'O WebSocket abriu, mas a negociação do modelo não foi concluída [LIVE_WS_SETUP_FAILED].';
}

export function liveSessionClosedMessage(attempt) {
  return classifyLiveFailure({...attempt,closed:true}) + ' Inicie outra conversa manualmente, após o intervalo de segurança.';
}
