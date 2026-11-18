# POTIGUAR-LIVE-CLOUD-WS-DIAGNOSTICS-001 — diagnóstico do navegador remoto e gate HTTPS

**Status:** diagnóstico client-only implementado; fallback HTTPS de IA **NÃO IMPLEMENTADO**.
**Autoridade final:** LEANDRO. **Orquestrador:** MESTRE.
**Origem:** Issue #54, reteste Gemini modo Tarefas, demo sintética promovida com o
SHA do PR #58 `6e37e5adc8118025188e294dee3c2e6c8ad4a41e`.
**Base da branch:** commit exato do PR #58 (não altera esse PR, develop, deployment, banco, cofre ou backend).

## Evidência e hipótese

O navegador real independente de MESTRE conectou ambos modelos Live e produziu
respostas do provedor. O navegador remoto Gemini, em **nova** sessão, recebeu
`[LIVE_WS_ERROR]` na primeira tentativa com 3.8 Live e na tentativa Extended
após mais de 20 s, sem HTTP 429. A demo e as etapas 1–8 passaram.

`/meta=200`, `/csrf-token=200` e `/session-token=200` são evidências do
backend até a emissão do token; **não** demonstram que o navegador pode abrir
`wss://generativelanguage.googleapis.com`. No código implantado, CSP
`connect-src` já inclui explicitamente o HTTPS e WSS do Google.
Causas plausíveis: egress/política de browser cloud, proxy que bloqueia upgrade
de WebSocket, CSP adicional injetada por intermediário, handshake recusado por
outro motivo, bloqueio de origem, ou falha transitória. **Causa definitiva
não comprovada.** Não atribuir a chave ausente nem ao cooldown, já refutados
pelas evidências.

O evento JavaScript `WebSocket.onerror` não divulga detalhe confiável.
`onclose` pode chegar depois; `CloseEvent.code` e `wasClean` informam
**sintomas**, não o motivo do bloqueio. A conexão pré-existente pode ser
encerrada antes/depois do `onopen`. Documentação:
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/error_event
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/connect-src
- https://ai.google.dev/api/live

## Mudança nesta branch: diagnóstico local sem mudança de tráfego

1. Manter somente uma tentativa e o único token efêmero do servidor.
2. Ao receber `onerror`, aguardar **até 220 ms apenas pelo evento de
   encerramento** antes de concluir classificação; não é reconnect/retry.
3. Registrar exclusivamente `opened` como antes/depois da abertura,
   `CloseEvent.code` inteiro validado e `wasClean` booleano conhecido,
   nunca `CloseEvent.reason`, URL, query, headers, token, erro cru ou texto.
4. Se não chegar `onclose`, exibir `LIVE_WS_ERROR` e
   `fechamento=DESCONHECIDO`, sem inferir causa.
5. Se houve 1006 e `abertura=ANTES_ABERTURA`, suspeitar de falha de
   handshake/egress, **sem afirmar** proxy como causa.
6. Se o SDK rejeitar por outro motivo, preservar a categoria genérica, sem
   revelar exceção potencialmente sensível.
7. Se a sessão já estiver conectada, aguardar brevemente por `onclose`
   após `onerror` para entregar o código final em vez do erro genérico.

O `wasClean` desconhecido nunca é transformado em `true`.
Os códigos e flags ajudam o MESTRE a orientar o reteste Gemini sem mudar
CSP, quota, autenticação ou tráfego da API.

## Opções de evolução — ordem e decisão

### A. Telemetria mínima do cliente (este PR) — autorizada

Implementação isolada, teste unitário + browser local, pronta para revisão.
Não torna navegadores cloud capazes de abrir WebSocket caso o ambiente bloqueie.
Não enviar automaticamente telemetria de sessões a servidores novos.

### B. Diagnóstico de WebSocket sem credenciais — **HUMAN_GATE requerido**

Um probe controlado com origem/endpoint de WS sem token pode distinguir
proibição geral de WebSockets da falha **específica** no endpoint Google.
Uma resposta positiva em um domínio de teste não garante que o Google será
alcançável. Evitar serviços de eco públicos arbitrários e envio de dados.
Se for adicionado um endpoint próprio, deve ser sem segredos, sem entrada
arbitrária, tempo limite curto, sem refletir dados, com CSP exata, rate limit,
RBAC da demo e sem execução em produção. Qualquer rota/infra nova exige
aprovação anterior de LEANDRO. **Nenhum endpoint foi criado nesta branch.**

Para comparação externa, capturar (apenas no ambiente de testes autorizado):
`opened`, `code`, `wasClean`, CSP efetiva e indicador de upgrade WS
sem registrar URL completa com query, token ou payload. Uma política do
navegador gerenciado pode não ser inspecionável.

### C. Fallback do Copiloto **texto por HTTPS** — **HUMAN_GATE requerido**

**Recomendação MVP para permitir agente de texto no navegador cloud que
aceita HTTPS mas bloqueia WebSocket.** É um **outro modo**, com um modelo
de geração textual escolhido e confirmado pelo catálogo do provedor,
NÃO o 3.8 Live renomeado. Não oferece áudio bidirecional, transcrição de voz
nativa nem latência Live. Nunca ativar silenciosamente por falha do WS;
exigir opção consciente e consentimento por modo. Nenhuma implementação
nesta branch.

```text
Navegador Gemini gerenciado
  | fetch HTTPS same-origin + CSRF + cookie + consentimento texto
  v
Flask /admin/copilot/text-turn (NOVA ROTA: gate pendente)
  | RBAC, demo-no-login sintética, quotas independentes,
  | rate limiting, input MAX_BYTES, allowlist por etapa e applicable()
  | bloqueio de CPF, documentos, pagamentos, acessos, biometria, saúde,
  | prompt limitado, log de código/status sem conteúdo
  v
Gemini API /models/{modelo_texto_verificado}:generateContent
  | HTTPS backend, chave existente só do servidor/cofre
  v
Proposta estruturada {step, field, safe_value, text}
  | verificar contrato NO SERVIDOR antes de devolver
  v
UI via postMessage same-origin para controlador existente
  | validação de step, field, allowlist, consentimento e versão
  v
salvamento do rascunho sintético pelo fluxo existente (422/403 preservados)
```

**Contrato mínimo:** somente intenção textual de campo seguro da etapa
corrente, opção selecionada ou frase curta sintética. Sem histórico de
formulário, CPF/RG, endereço detalhado, dados financeiros, dados biométricos,
senhas, áudio, navegador/cookies, tokens ou conteúdo de campos protegidos.
Em vez de aceitar `messages[]` livre, receber
`{step, field, intent, candidate_safe_value, request_id}`, todos
validados no backend com tamanhos fixos e valores permitidos; ou rejeitar
qualquer payload que não possa ser classificado como estritamente seguro.
Segurança por regex em texto livre **não é suficiente** para garantir
ausência de dados pessoais: usar allowlist positiva e rejeitar ambiguidades.
O backend **não confia** nas flags `safe` enviadas pelo frontend.

**Proteções obrigatórias:** consentimento independente; CSRF de sessão;
RBAC `USERS_CREATE` + isolamento do principal demo; replay/idempotência;
rate limit por usuário/sessão/IP; cota por dia/tokens, sem permitir bypass
das quotas Live existentes; model ID permitido no servidor; cache
`no-store`; segredos apenas em processo servidor; auditoria com
`request_id`, categoria e status (nunca prompt/resposta com valores);
verificação JSON/schema e rejeição de `functionCalls` fora de allowlist;
nenhuma ferramenta de cadastro definitivo; preservar bloqueios 422/403
e a confirmação humana; limites de custo e falhas do fornecedor (timeout/
502/503) com mensagem neutra.

**Ações de IA:** o modelo apenas **propõe** campo seguro. A UI existente
executa `potiguar:onboarding:proposal` com validação do controlador e
recibo; nunca permitir que uma resposta do modelo escreva no banco direto.
Um modo determinístico local de preenchimento já existente não deve ser
rotulado como IA do backend.

**Risco de abuso:** como a demo é pública e sem login, verificações
de principal sintético/quotas/rate limiting devem ser testadas antes de
expor a rota; caso contrário pode virar um proxy pago público para a
API Gemini. Não reutilizar indiscriminadamente `session-token` da Live,
pois a unidade de custo e o controle de uso diferem.

### D. Proxy WS server-to-server — não recomendado para este MVP

Pode contornar **somente** a restrição de conexão direta ao Google se o
navegador conseguir abrir WSS com o domínio próprio; caso o navegador bloqueie
todos os WebSockets, não resolve. Introduz infraestrutura persistente, risco
de streaming de áudio, custos, autenticação e limites de conexão. Exigiria
outra autorização e não está no escopo.

## Critérios de QA antes e depois de futura autorização

**Este PR (sem backend):** testes unitários para `onerror → onclose`
tardio, 1006, 1008, `wasClean`, `opened`, ausência de `close`,
limpeza de timers em `disconnect`, callbacks antigos, ausência de token
nos erros, um pedido de token por tentativa, preservação 429. Navegador
Chromium com WS simulado, 390×844, Live e Extended.

**Caso o HTTPS texto seja autorizado depois:** testes backend com 401/403,
CSRF faltante, 422 para dados sensíveis mesmo sintéticos, 429 por limite,
tamanho excessivo, payload fora de allowlist, tool calling malicioso,
replay, sessão demo, modelo indisponível, fornecedor timeout, logs sem
conteúdo e zero criação real; E2E Gemini remoto sem WSS, com IA textual
real respondendo a **um campo seguro fictício** via HTTPS e recibo de
`saved`; E2E voz mantém mensagem de indisponibilidade e não finge Live.

## HUMAN_GATE pendente — exclusivo para LEANDRO

**Escopo solicitado para nova missão separada:**
autorizar desenho e implementação em *outra branch/PR draft* de um
**Copiloto texto HTTPS** usando modelo textual permitido, rota Flask
protegida, limites/rate/auditoria sintéticos e teste controlado sem dados
reais. Autorizar de forma separada o probe WS sem credenciais se necessário.
**Não há autorização nesta rodada para criar essas rotas, deployar,
reconfigurar proxy/CSP, modificar segredo, cota, banco, Render, Vercel,
container ou PR #58.**

**Decisão solicitada:** LEANDRO autoriza ou rejeita este novo escopo.
**Gate:** `HUMAN_GATE_PENDING_BACKEND_HTTPS_TEXT`.
