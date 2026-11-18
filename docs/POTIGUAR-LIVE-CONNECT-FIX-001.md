# POTIGUAR-LIVE-CONNECT-FIX-001 — Tratamento seguro de falhas Gemini Live

**Branch de referência:** `develop` em `401cdc9d0653883ceb971a048c7b5f64c7ba27a0`.
**Orquestrador:** MESTRE. **Autoridade final:** LEANDRO.
**Escopo:** cliente Copiloto Gemini Live 3.8 / Extended do onboarding V2.
**Limites:** sem mudança de token, segredo, cofre, quota, cooldown, backend, banco, autenticação, 422/403, Vercel ou Render.

## Reprodução independente antes da correção

Em 18/11/2026, no Chromium do host `mcf-gpu-x99`, uma conexão pela demo pública no fluxo
`/admin/users/new → Abrir Copiloto → consentir → Conectar Gemini 3.8 Live` obteve:

| Fase | Evidência sanitizada |
| --- | --- |
| Página V2 | HTTP 200 |
| `/admin/copilot/meta` | HTTP 200 |
| `/admin/copilot/csrf-token` | HTTP 200 |
| `/admin/copilot/session-token` | HTTP 200 |
| WebSocket `generativelanguage.googleapis.com` | Handshake 101 |
| UI | Conectado, sem erro |

Não foi necessário abrir chave ou cofre e não foram usados dados de funcionário. A falha
intermitente descrita na Issue #54 **não foi reproduzida nesse navegador**. Não atribuir causa
definitiva ao Gemini, ao provedor ou ao navegador remoto a partir deste teste.

## Defeito confirmado no cliente

O cliente anterior descartava integralmente a causa de toda exceção após
`ai.live.connect()` e apresentava sempre a mesma mensagem. Além disso, um evento
`onclose` atrasado de uma tentativa anterior podia modificar `session` e estado de
uma tentativa mais recente. A proteção de concorrência só verificava `session` pronta,
não uma negociação já em andamento.

Correções: distinguir emissão de CSRF e token de erro WebSocket; diagnosticar fases sem
mostrar mensagens brutas do SDK; serializar tentativas em andamento; ignorar callbacks
de tentativas invalidadas; recusar uma sessão que tenha fechado durante a negociação;
preservar token único e **não executar retry automático**.

### Códigos exibidos

| Código | Significado operacional |
| --- | --- |
| `LIVE_CSRF_HTTP_N` | Falha HTTP na validação CSRF |
| `LIVE_TOKEN_HTTP_429` | Cooldown/limite protegido pelo servidor |
| `LIVE_TOKEN_HTTP_N` | Falha na emissão, não no WebSocket |
| `LIVE_TOKEN_INVALID` | Resposta inconsistente ou modelo divergente |
| `LIVE_WS_OPEN_FAILED` | Não abriu WebSocket |
| `LIVE_WS_ERROR` | Evento de erro de transporte |
| `LIVE_WS_CLOSE_1006` | Encerramento anormal de conexão |
| `LIVE_WS_CLOSE_1008` | Encerramento por política/configuração |
| `LIVE_WS_SETUP_FAILED` | Abriu transporte mas o SDK não concluiu a negociação |
| `LIVE_SDK_INIT` | Falha de inicialização local do cliente |

Não registrar URL completa do WebSocket, query, token, headers, event.reason,
`ErrorEvent.message`, exceção bruta do provedor ou mensagens de usuários.

## Testes e reprodutibilidade

Executar em um workspace isolado com Node.js e Chromium:

```bash
cd frontend/copilot
npm ci
npm test
npm run build
cd ../..
POTIGUAR_PUPPETEER_MODULE=/caminho/para/puppeteer node scripts/potiguar_live_connect_browser_e2e.cjs
```

O E2E sobe servidor local e substitui o WebSocket por uma implementação **sintética**.
Cobre falha da primeira conexão com erro específico, segundo clique com HTTP 429,
conexão Live e Extended e ausência de novas tentativas automáticas. Não utiliza
API Gemini real, credenciais, dados reais ou banco. O teste com WebSocket real foi
feito **antes** do patch; nenhuma implantação posterior foi autorizada.

## Critérios para MESTRE e Gemini retestarem

Após promoção em gate separado:
1. Confirmar SHA de implantação e se o JS compilado publicado corresponde ao commit.
2. Abrir sessão inédita de navegador; documentar hora, modelo, etapa V2 e **somente** status HTTP/códigos diagnósticos.
3. Na primeira tentativa, registrar HTTP de CSRF/token e se houve WebSocket 101, fechamento ou erro (sem URL e payload).
4. Em erro `LIVE_WS_*`, capturar a mensagem sanitizada e verificar políticas do navegador.
5. Não tentar Extended imediatamente após falha: aguardar o cooldown de 15 segundos.
6. Testar conexão Live e Extended separadamente; validar texto em PT-BR e controles de voz sob permissões.
7. Confirmar que 422/403, quotas e ausência de persistência real permanecem intactos.

**Risco residual:** um bloqueio de WebSocket aplicado pelo navegador remoto do Gemini
ou uma indisponibilidade do fornecedor não pode ser resolvido apenas no cliente.
Nenhuma mudança de arquitetura de rede, quota ou servidor foi autorizada nesta PR.
