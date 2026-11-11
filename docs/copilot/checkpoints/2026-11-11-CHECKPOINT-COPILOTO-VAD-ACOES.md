# CHECKPOINT — Copiloto Potiguar: cadastro assistido e VAD

**Mission ID:** `POTIGUAR-COPILOT-ACTIONS-VAD-20261111`
**Reconciliado:** 11/11/2026, ~16h35 America/Recife
**Estado:** `HML_ACTIVE / PR41_OPEN_GREEN / OFFICIAL_PRODUCTION_BLOCKED`
**Responsáveis:** LEANDRO é humano e autoridade final; MESTRE orquestra; LÉO é agente distinto.
**Checkpoint não equivale a autorização de merge ou deploy novo.**

## Fonte da verdade

- Produto: [leon337/reconhecimento_facial](https://github.com/leon337/reconhecimento_facial), e não o antigo `sistema-ponto-facial`.
- Governança: [leon337/multiagent-collaboration-framework](https://github.com/leon337/multiagent-collaboration-framework); ler `AGENTS.md`, `docs/MCF-CURRENT-STATE.md`, `docs/operations/MCF-MESTRE-HANDBOOK.md` e estado atual do GitHub.
- Principal: [PR #41](https://github.com/leon337/reconhecimento_facial/pull/41), aberto/não mesclado, branch `feat/copilot-actions-vad-20261111`. SHA **antes do commit deste checkpoint**: `94469e42b0a26d2ab306530744955c6c5d639ba8`.
- `main` em 11/11: `d64326789092992c2357dc6f945546bb192bebbf`.
- Os workflows no SHA `94469e4` estavam **SUCCESS**: CI (#43083622379, inclui build Docker), Production Validation (#43083622383), Copiloto Vue — Build and Tests (#43083622322) e Copiloto — Portal de Credenciais (#43083622411).
- Qualquer novo commit documental muda o HEAD e exige **consultar novamente as verificações do HEAD novo** antes de alegar que estão verdes.

## Produto e arquitetura implementada

LEANDRO quer que o Copiloto **cadastre funcionários**, não apenas indique páginas; também quer que o microfone **não trate ruídos como diálogos**.

**Cadastro:** Gemini `gemini-3.8-live` chama somente `prepare_employee_registration`, que devolve um rascunho sem escrita no banco. O Vue mostra campos editáveis e exige clique em **Confirmar e cadastrar**. O backend `POST /admin/copilot/employee-create` exige login, CSRF, `Permission.USERS_CREATE`, validadores e escopo empresa/obra, trata duplicidade, registra auditoria e grava `Employee` + `User` com papel `operator`. A senha inicial é aleatória, gerada no servidor e devolvida apenas após confirmação. Nenhuma ferramenta pode registrar ponto, alterar biometria, folha, admin ou credenciais.

**VAD:** `frontend/copilot/src/vad.js` implementa gate local com nível RMS adaptativo, cruzamentos por zero, periodicidade/autocorrelação, duração mínima, pré-fala, histerese e silêncio de fechamento. O áudio passa ainda por `getUserMedia` com supressão de ruído e parâmetros conservadores do Google Live. Há modo manual para ambientes difíceis. **Não garante eliminação de todo ruído**; música e vozes distantes podem ativar a detecção.

**Flags:** `POTIGUAR_COPILOT_ENABLED` e `POTIGUAR_COPILOT_ACTIONS_ENABLED`. Ações desligadas **por padrão** no código; ligadas apenas na HML sintética. Nome, usuário e matrícula precisam ser fictícios na HML; as cotas são 12 sessões Live/dia e 5 **tentativas** de cadastro/dia UTC.

Arquivos-chave: `app/copilot/actions.py`, `app/copilot/routes.py`, `app/copilot/demo_quota.py`, `main.py`, `frontend/copilot/src/{App.vue,live.js,registration.js,vad.js,audio.js}`, `tests/test_copilot_employee_actions.py`. Detalhes em `docs/copilot/ADR-002-ACOES-ASSISTIDAS-VAD.md` e `docs/copilot/2026-11-11_ACTIONS_VAD_TESTS.md`.

## Evidências verificadas

- **174 testes Python aprovados** (suíte completa); **12 testes JS aprovados**; Vite build PASS.
- **Gemini real** com dados fictícios: `gemini-3.8-live` conectou, emitiu a ferramenta `prepare_employee_registration` e devolveu rascunho; nenhuma gravação foi executada pela chamada ao modelo.
- `gemini-3.8-live-extended-thinking` conectou, mas **não emitiu** chamada da ferramenta no teste; cadastro por conversa limitado ao Live padrão.
- VAD: silêncio, ruído baixo/alto e pulsos curtos rejeitados nos testes; áudio sintético com 34 blocos teve 1 abertura e 1 fechamento, 32 blocos transmitidos. **Falta teste de ruído real no Android**.
- **HML sintética:** endpoint autenticado de confirmação criou conta `e2e.teste`, respondeu **HTTP 201**, gerou senha inicial e evento de auditoria; duplicação respondeu **HTTP 409**. Não repetir essa criação sem consultar o banco.
- Não há comprovação de cadastros reais nem de operação oficial de ponto.

## Homologação, acesso e isolamento

- Notebook autorizado: `leo-N43SM`; worktree de feature: `/tmp/potiguar-actions-vad-20261111`. Checkout principal `/home/leo/reconhecimento_facial` pertence à NF-01: preservar.
- Imagem atual: `potiguar-copilot:hml-actions-vad-20261111`, contêiner `potiguar-copilot-hml-20261111`, app em `127.0.0.1:18951`. Proxy Caddy autenticado em `127.0.0.1:18952`.
- Link **temporário e sujeito a expiração**: `https://converter-head-job-hall.trycloudflare.com/admin/copilot`. Sem credenciais retorna **HTTP 401**; saúde local `/health` retorna **HTTP 200**.
- Chave Google em cofre criptografado **privado**, montado **somente leitura**, nunca copiado para Git/Render; não imprimir senhas/tokens/valores de variáveis de segredo.
- Banco SQLite da HML é fictício. Backup antes das ações preservado no volume privado como `staging.before-actions-20261111.sqlite3`. Imagens/contêineres anteriores preservados para rollback.
- Render workspace chegou a **25/25 serviços grátis**, e a criação permanente foi recusada. [PR #38](https://github.com/leon337/reconhecimento_facial/pull/38) é apenas preparação de deploy **draft**. Não excluir serviços ou contratar plano pago sem autorização.
- Disco do notebook estava em **98%**: evitar builds pesados/destrutivos sem planejamento.

## Outras frentes, preservadas

- PRs já integrados: [#36](https://github.com/leon337/reconhecimento_facial/pull/36) Vue/Gemini Live, [#37](https://github.com/leon337/reconhecimento_facial/pull/37) cofre, [#39](https://github.com/leon337/reconhecimento_facial/pull/39) rota inicial, [#40](https://github.com/leon337/reconhecimento_facial/pull/40) interface móvel.
- NF-01/design system permanece separado, com [PR #32](https://github.com/leon337/reconhecimento_facial/pull/32) e [#35](https://github.com/leon337/reconhecimento_facial/pull/35). [#34](https://github.com/leon337/reconhecimento_facial/pull/34) trata runner PostgreSQL; não misturar branches nem afirmar Orca humano a partir de ensaio assistido.
- Registro MCF `context/projects/controle-ponto-frontend.yaml` refere-se à missão NF-01, **não** a este Copiloto.

## Pendências que mudam a próxima decisão

1. Revalidar GitHub PR #41, HEAD e todos os checks **após os commits deste checkpoint**. Revisar/decidir merge pelos gates do MCF. Este pedido atual não pediu merge.
2. Testar microfone e VAD em **Android real**, especialmente TV, ventilador, música e rua, e medir falsos positivos, falsos negativos e latência. O modo manual é fallback.
3. Localizar o módulo de VAD/“modulizing” do assistente **R** citado por LEANDRO; **não foi identificado com segurança** no GitHub ou notebook. Não afirmar reaproveitamento ainda.
4. Validar a UI de revisão e confirmação real no Chrome Android; CI/back-end não substituem esse teste humano.
5. Hardening: idempotência durável por `request_id` ainda não implementada; unicidade do username evita alguns duplicados, mas não cobre todo retry.
6. Produção oficial bloqueada: infraestrutura/dominio permanentes, PostgreSQL persistente, migrações, backup e restore, observabilidade, LGPD/trabalhista, segurança e homologação humana.

**Próximo arquivo obrigatório:** `docs/copilot/checkpoints/2026-11-11-HANDOFF-PROXIMA-SESSAO.md`. Estado deste documento é histórico e deve ser reconciliado com GitHub/host ao iniciar nova sessão.
