# POTIGUAR-HTTPS-TEXT-001 — Copiloto textual HTTPS, sem voz

Missão executada em branch de correção isolada após HUMAN_GATE aprovado por LEANDRO
na Issue #60. MESTRE permanece responsável por QA independente e eventual promoção.

## Baseline e isolamento

- Base desta branch: PR #59, SHA a7f7690a51212860e212da34ef49acffd99a5cd2
- Origem: PR integrado #58, SHA 6e37e5adc8118025188e294dee3c2e6c8ad4a41e
- Nenhum merge em develop, main ou alteração da demo/container neste trabalho
- Nenhum dado real de Pessoa Real foi utilizado

## Interface e fluxo

- Na interface do onboarding aparece a opção explícita Copiloto texto (HTTPS), sem voz.
- A opção aparece somente quando metadata.text_enabled estiver true.
- Consentimento independente do Live; falha WebSocket não faz downgrade automático.
- O modo HTTPS nunca liga microfone; botão Falar permanece desabilitado.
- Para um campo permitido, o usuário informa valor sintético da allowlist.
- O navegador consulta CSRF e chama POST same-origin /admin/copilot/text-turn.
- A API retorna uma proposta, não altera banco nem usa tools de registro.
- A UI envia somente a proposta ao controlador V2 existente por postMessage
  same-origin. Declara salvo apenas após recibo explícito status=saved.
- Não há histórico, documentos, dados preenchidos, CPF ou texto livre no prompt.

## Contrato positivo do MVP

Etapa 0: relation_type — CLT comum, CLT intermitente, Sem vínculo empregatício.
Etapa 1: full_name — Teste Funcionário de Teste, Teste Operador de Teste.
Etapa 2: country — Brasil; address_type — Urbano, Rural, Exterior.
Etapa 3: transport_benefit — Sim, Não.
Nenhum outro campo, opção ou par etapa/campo é aceito neste MVP.
A interface executa validação preventiva, mas o servidor é a autoridade final.

## Backend, segurança e quota

- Rota Flask exigindo sessão autenticada, RBAC USERS_CREATE, CSRF global,
  consentimento booleano true, JSON de schema exato, limite 512 bytes.
- No ambiente DEMO exige papel manager, username demo.*, usuário sintético
  vinculado ao cookie, empresa e obra coerentes com a sessão.
- PUBLIC_DEMO mantém listas fechadas de endpoints e de campos sintéticos.
- Feature flag: POTIGUAR_COPILOT_TEXT_ENABLED=1 (desabilitado por padrão).
- Modelo padrão textual: gemini-3.8-flash no endpoint REST generateContent
  da API Gemini v1beta; IDs dos modelos Live/Extended não são permitidos.
- Allowlist de modelo: gemini-3.8-flash, gemini-3.6-flash, gemini-3.5-flash-lite.
- Chave obtida somente pelo servidor a partir da configuração/cofre existente.
  Nenhuma chave nova, token Live ou credencial no JS, HTML ou repositório.
- Biblioteca padrão urllib sem nova dependência Python, timeout 12 segundos,
  máximo de 220 tokens de resposta e schema JSON de saída com field, value, reply.
- O servidor rejeita qualquer proposta do fornecedor que altere campo/valor.
  A frase final de confirmação é neutra, definida pelo próprio servidor.
- Em armazenamento sidecar separado, copilot-text-quota.sqlite3, cada tentativa
  reserva atomicamente um request_id via SHA-256 e transação BEGIN IMMEDIATE.
- Quotas padrão: 25 requisições/dia global, 8 por principal/dia, 20 por
  origem de rede/dia e 2 segundos mínimos entre turnos do mesmo principal.
  IP, principal e request_id entram no sidecar apenas como hashes.
- Replay 409, limite/rate 429, sem reenvio automático nem reembolso ao falhar.
- Log de categorias e status, nunca prompt, nome, valor, documento ou segredo.
- As guardas existentes 422/403, Live cooldown 15s e quotas de voz permanecem.

## Teste e QA

Executar em virtualenv com Flask, Flask-WTF, Flask-SQLAlchemy e pytest:
python -m pytest tests/test_copilot_text_https.py tests/test_copilot_live.py tests/test_copilot_demo_quota.py -q

Na máquina QA sem dlib/face_recognition, o carregamento dos testes Flask foi
executado com stub biométrico SOMENTE no runner externo temporário. Não usar
essa simulação para testar recursos faciais; a implementação real de HTTP,
CSRF, Flask, RBAC e transações SQLite foi executada com suas dependências.

Frontend:
cd frontend/copilot
npm ci
npm test
npm run check
npm run build

Navegador sintético:
POTIGUAR_PUPPETEER_MODULE=/path/to/puppeteer node scripts/potiguar_https_text_browser_e2e.cjs

O navegador Chromium bloqueia WebSocket intencionalmente, verifica consentimento
independente, uma sugestão de campo seguro, recibo saved, áudio desabilitado,
ausência de novas tentativas Live, zero chamadas reais Google e zero empregados
criados. O Google real NÃO foi chamado nesta entrega.

## Gates restantes

O novo modo NÃO está implantado nem ativado em nenhuma demo.
MESTRE deve revisar PR/CI, quotas e permissões do sidecar antes de promover.
A promoção à demo exige nova autorização e smoke real com um campo sintético
para validar disponibilidade efetiva do modelo via HTTPS; o primeiro smoke
deve confirmar CSRF, identidade demo, quota, modelo REST e recibo salvo.
Não habilitar em sistema real de RH nem mover dados reais de usuário real ao Gemini
da demo. Cadastro real pertence a outra missão e ambiente privado.
