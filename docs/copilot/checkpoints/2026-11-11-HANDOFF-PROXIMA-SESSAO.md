# HANDOFF — próxima sessão do MESTRE no Potiguar

**Mission ID:** `POTIGUAR-COPILOT-ACTIONS-VAD-20261111`
**Phase:** `HML_VERIFIED_CHECKPOINT_PR41_OPEN`
**Autoridade:** LEANDRO é o humano final; MESTRE coordena; LÉO é agente distinto.

## Prompt pronto para abrir outro chat

> MESTRE, continue o projeto Potiguar pelo checkpoint `POTIGUAR-COPILOT-ACTIONS-VAD-20261111` no repositório `leon337/reconhecimento_facial`, em `docs/copilot/checkpoints/2026-11-11-CHECKPOINT-COPILOTO-VAD-ACOES.md`, e pelo checkpoint cruzado do MCF. Consulte `AGENTS.md` e GitHub ao vivo; não recomece a implementação. O PR #41 contém cadastro assistido por Gemini com confirmação humana e VAD modular. O ambiente no notebook é HML sintética e não produção oficial. Verifique CI/HEAD, teste Android real, encontre o módulo VAD do assistente R, preserve segredos, backups e NF-01. Traga o status, bloqueios e próxima ação segura.

## Sequência de retomada (sem recriar o que já foi feito)

1. Consultar `leon337/multiagent-collaboration-framework/AGENTS.md`, `docs/MCF-CURRENT-STATE.md`, `docs/operations/MCF-MESTRE-HANDBOOK.md`, `docs/operations/MCF-LOCAL-WORKSPACE-CANONICALIZATION.md`.
2. Conferir **GitHub ao vivo** do produto: HEAD de `main`, PR #41 e checks do SHA mais recente; PRs paralelos #32, #34, #35 e #38. No checkpoint pré-documental, #41 estava aberto com 4 workflows verdes no SHA `94469e4`.
3. Notebook `leo-N43SM`: `git -C /home/leo/reconhecimento_facial worktree list`, `git -C /tmp/potiguar-actions-vad-20261111 status --short`. O worktree tinha só um symlink de `frontend/copilot/node_modules` não rastreado. Não versioná-lo, não alterar o checkout NF-01 principal.
4. HML: confirmar `docker ps --filter name=potiguar-copilot-hml`, saúde `curl -f http://127.0.0.1:18951/health`, acesso HTTPS anonimizado 401 no túnel `trycloudflare.com`. Se túnel expirar, recriar só gateway **com autenticação**, nunca expor backend sem proteção.
5. Sem revelar segredos, confirmar `POTIGUAR_COPILOT_ENABLED`, `POTIGUAR_COPILOT_ACTIONS_ENABLED`, e cofre montado em leitura. Não exibir chaves Gemini, senhas de demonstração, token efêmero ou material Fernet.
6. Testar com dados **somente fictícios**, usando novo username e matrícula `TEST-...`: pedir ao `gemini-3.8-live` rascunho, revisar na UI, clicar confirmação **uma vez**, conferir novo funcionário e auditoria. `e2e.teste` já foi criado em teste e não deve ser reutilizado.
7. Fazer teste no Android de ruídos, interrupções e qualidade de fala; aferir false positives e latency. Testar modo manual. Localizar VAD do assistente R e comparar contratos antes de substituição.
8. Revisar idempotência por `request_id`, limites de HML, permissão/RBAC, custeio Google, LGPD e experiência de senha inicial. Planejar CI/merge conforme estado real e gates; **não promover automaticamente à produção oficial**.

## Evidências ancoradas

- Python: **174 passed**, JS: **12 passed**, Vite build PASS.
- Tool call real do Gemini 3.8 Live com dados fictícios: **PASS**; Extended Thinking: conectou, **sem tool call** no teste.
- Endpoint de cadastro HML: **201** criação sintética, **409** repetição, auditoria presente.
- Workflows GitHub de PR #41 no SHA `94469e4`: CI, Production Validation, Vue Build and Tests e Portal Credentials = SUCCESS; um novo commit cria novo HEAD e precisa de nova leitura.
- Documento técnico: `docs/copilot/ADR-002-ACOES-ASSISTIDAS-VAD.md`. Evidências: `docs/copilot/2026-11-11_ACTIONS_VAD_TESTS.md`.

## O que NÃO fazer

Não perder ou limpar checkout NF-01, worktrees, volumes de backup, cofre privado ou contêiner de rollback. Não declarar VAD humano aprovado nem operação trabalhista em produção. Não publicar credenciais em Git, logs ou nesta conversa. Não confundir CI verde com deploy oficial. Não deletar serviços Render para abrir vaga sem autorização.

**Conclusão do handoff:** o usuário pediu checkpoint local/remoto e continuidade. Este documento não autoriza por si só merge, implantação paga ou operação com funcionários reais.
