# Relatório de execução — Fase 04

## Execução
1. Confirmada a PR #43 draft, head `ee093b90`, e inspecionado o repositório MCF.
2. Inspecionado fluxo V2 real de onboarding: `Employee` criado no `onboarding_complete`, ficha `EmployeeOnboarding` guarda payload criptografado. Acesso administrativo por `Permission` existente.
3. Criada branch/worktree isolada a partir da Fase 03.
4. Implementado `app/payment_v2_link.py` com relação simulada em memória entre nomes textuais do XLSX e registros de `Employee`/existência de `EmployeeOnboarding`.
5. Integrado modo de comparação à rota já autenticada de upload e aos templates; adicionado atalho protegido na lista de funcionários da V2.
6. Implementados testes de isolamento por empresa/obra, RBAC, CSRF, múltiplos homônimos, nomes repetidos, inativos, legados, fórmulas, privacidade e ausência de gravação.
7. Corrigida discrepância com arquivo real: cabeçalho de nomes `A3:B3` mesclado; valor textual na coluna B. Teste sintético específico acrescentado.
8. Suite selecionada incluindo testes reais de onboarding V2: **65 aprovados**, 252 avisos de depreciação legada (logs em `PHASE-04-VALIDATION-FULL.txt`).
9. Smoke com Ajudantes original (sem banco real) indicou 156 linhas candidatas; detalhes agregados no relatório de smoke, sem dados pessoais.

## Limites
Não foi acessado o banco de funcionários real da V2; resultados de coincidência reais não foram produzidos. O código está integrado aos modelos/rotas da aplicação em branch de desenvolvimento, **não** à V2 hospedada em produção.

Não houve importação/comprometimento de cadastro, leitura de payload criptografado, correção de planilhas, cálculo financeiro, autorização de transferência nem PIX.

Não houve atuação de agentes independentes LÉO/Emily nem decisão sobre merge/deploy. A GPU não foi utilizada para comparações de nomes/ZIP, porque são tarefas leves de CPU e I/O, sem ganho justificável por GPU.
