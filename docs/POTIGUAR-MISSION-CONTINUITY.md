# Ecossistema Potiguar — referência única de continuidade

**Reconciliação-base:** 2026-11-17; sempre consultar o estado live antes de agir.

## Fonte de verdade

- Aplicação: https://github.com/leon337/reconhecimento_facial
- Método MCF: https://github.com/leon337/multiagent-collaboration-framework (AGENTS.md e normas vigentes).
- Baselines verificados antes desta consolidação: develop ab4ab92a37a5e0da7bb15aaac601a6ab459081ca; main d64326789092992c2357dc6f945546bb192bebbf.
- Desenvolvimento = develop; produção de funcionários reais = main. Demonstração Vercel não é produção real.
- Rodar bash scripts/potiguar_reconcile_state.sh antes de nova missão; conferir PRs/Issues em aberto.

## Fluxo único

Desenvolver uma missão por vez em branch curta derivada de develop; não duplicar PRs. Testar, abrir PR, obter CI, integrar à develop e sincronizar local por fast-forward. Não promover main sem aceite humano. Preservar segredos, dados de funcionários, biometria e bancos privados.

## Inventário

- Copiloto antigo feat/potiguar-copilot-onboarding-20261112@0b93e25 é ancestral de develop; worktree limpo pode ser eliminado. O benchmark de Gemini passa a resolver seu SDK em frontend/copilot/node_modules (instalar via npm ci --prefix frontend/copilot).
- PRs de pagamentos: #42 fase 02 (base fase 01), #43 fase 03 (base fase 02), #44 fase 04 (base fase 03). Todos drafts, branches e commits remotos preservados. Checkouts locais redundantes podem ser removidos após verificar que estão limpos, sincronizados e sem serviços dependentes.
- NF-01: PRs #32 e #35; checkout raiz possui arquivos não rastreados e branch atrás de upstream. Não remover sem recuperar/registrar dados únicos.
- PRs #13 (hardening), #33 (checkpoint), #34 (restore) são independentes; não integrar nem fechar apenas para limpar contagem.
- Não confundir branches locais de trabalho com branches permanentes: as únicas referências permanentes de produto são develop e main.

## Ambientes e verificação

- Privado autenticado: http://127.0.0.1:18953/admin/copilot
- Demo pública sintética, sem cadastro definitivo: https://potiguar-v2-demo.vercel.app/admin/copilot
- Projeto Vercel predix-ai-br/potiguar-v2-demo; gateway versionado em deploy/vercel-demo. Backend Flask e SQLite NÃO foram migrados; origem Cloudflare Quick Tunnel efêmera exige substituição durável.
- Evidência anterior: navegador 13/13 navegação + Live e 17/17 recuperação de HTTP 503 + linguagem natural, dados fictícios. Gemini Web verificou parcialmente etapas 1 a 3.
- Ainda pendentes: etapas 4 a 8 com agente real, voz do operador, continuação de campo protegido e aceite humano de cadastro.
- Para configurar Git -> Vercel, exigir rootDirectory deploy/vercel-demo e branch de produção da demo develop; nunca publicar main real como demo. Validar site ao vivo antes/depois.

## Ordem de continuidade

1. Origem HTTPS sintética estável e integração Git/Vercel segura.
2. Testes ponta a ponta das etapas 4 a 8, Copiloto Live, preencher/salvar/continuar, sem dados reais.
3. Reconciliar NF-01 sem perdas.
4. Retomar pagamentos somente via cadeia #42 -> #43 -> #44.
5. Limpar apenas caches regeneráveis; preservar modelos, perfis, containers/volumes Docker e dados exclusivos.

## Regra de conclusão

Registrar SHA local/remoto, status PR/CI, resultado do deploy, evidências PASS/FAIL e pendências. Não afirmar que um teste não executado passou, nem declarar sincronização total enquanto houver outras árvores sujas.

## Recibo de consolidação executada em 2026-11-17

- PR #50 integrado: develop@8e10ec5c3ca690ce59fc328b42741fe7c78385b9; CI 3/3 PASS; main real permanece d64326789092992c2357dc6f945546bb192bebbf.
- Worktrees locais redundantes removidos após preflight de alterações, SHA remoto exato, Docker mounts e processos: Copiloto legado e três fases de pagamentos. Filiais de pagamentos permanecem no GitHub nos PRs #42, #43 e #44.
- Dois worktrees físicos restantes: desenvolvimento (develop) e checkout legado NF-01. NF-01 não é produção e contém dados não rastreados; manter até reconciliação documental própria.
- Frontend reinstalado no checkout único de desenvolvimento; 41/41 testes JavaScript PASS, check de fontes PASS. Formulário de oito etapas sintético 24/24 PASS (incluindo bloqueios de CPF/consentimento e ação manual de continuar); esses testes não substituem voz física ou aceite de dados reais.
- Limpeza de artefatos regeneráveis: npm/pip cache e imagens Docker antigas sem containers dependentes; disco passou de 99% / 1,7 GB livres para 94% / 8,3 GB livres. Perfis, dados, modelos, Docker volumes e demais worktrees com dados únicos preservados.
- Vercel potiguar-v2-demo possui rootDirectory deploy/vercel-demo configurado e URL sintética respondendo HTTP 200 com cabeçalho esperado. **Ainda não há Git conectado nem origem HTTPS backend permanente**: a ligação automática deve ser feita somente após configurar branch de produção da demo em develop e validar que não será adotada main inadvertidamente.
- Recibos locais sem segredos: /home/leo/.local/state/potiguar-consolidation-20261117. Não versionar dumps privados.
- Continuidades ainda abertas e deliberadamente não tratadas como concluídas: infraestrutura durável da demo, integração Git/Vercel, sessão longa/etapas 4–8 com Gemini Web, NF-01 não rastreado, cadeia de pagamentos em draft. Não criar implementação concorrente para elas.

## Preparação de Render gratuito (2026-11-17, não publicada)

- Workspace Render autorizado: Leandro's workspace, ID `tea-d2u2msje5dus73eb6ehg`; inventário ao vivo: **25 serviços**, nenhum do repositório `leon337/reconhecimento_facial`.
- Criação de serviço web `potiguar-v2-demo-backend` com plano `free` rejeitada: **Hobby Tier is limited to 25 services**. Nenhum plano pago nem serviço novo criado.
- Blueprint `exs-dbue7m8jo6nc739qvtb0` criado com `autoSync=false`, `existingResources=create_new` e branch de trabalho isolada; planejamento com status `failed` pela mesma restrição de 25 serviços. **Não aprovado/aplicado**.
- Arquivos canônicos: `render.yaml`, `scripts/potiguar_render_demo_environment.py`, `scripts/potiguar_render_demo_entry.py`, `tests/test_render_demo_environment_unittest.py`, `scripts/potiguar_render_demo_smoke.py`; guia `docs/POTIGUAR-RENDER-DEMO-READINESS.md`.
- Não reutilizar serviços de outros repositórios nem apagar recursos apenas para contornar limite sem decisão humana específica. Serviço `potiguar-intermitente-app` preservado: é outro repositório.
- Render Free hiberna e perde SQLite local: domínio HTTPS pode ser estável, **rascunhos não são persistentes**. A demo Render ficará sem Gemini Live até controle durável de quota/credenciais e novo aceite; não injetar chaves da homologação.
- A Vercel **continua apontando ao Quick Tunnel existente**. Não alterar `deploy/vercel-demo/vercel.json` até Render passar verificações de segurança externas e haver vaga livre, sem custos.
