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
