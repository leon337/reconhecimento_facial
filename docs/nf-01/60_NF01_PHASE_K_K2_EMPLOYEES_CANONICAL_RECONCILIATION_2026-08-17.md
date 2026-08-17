# NF-01 — Fase K — K2 — Reconciliação canônica de Funcionários

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
K2_EMPLOYEES_CANONICAL_RECONCILIATION=APPROVED_BY_LEANDRO
K2_STATUS=IN_PROGRESS
PHASE_K_EMPLOYEES_RECONCILIATION=IN_PROGRESS
IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY
PRODUCTION_CHANGE=NO
PHASE_L=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate foi consumida somente para K2.

---

## Plano de implementação

**Goal:** reconciliar a superfície Funcionários do Design Lab com os gaps comprovados por K1, sem ampliar o escopo funcional.

**Architecture:** `03.01-funcionarios.html` continua como contrato de conteúdo; `employees-v1.css` continua responsável apenas pela apresentação local; `employees-v1.js` continua responsável apenas pela demonstração local de filtros, estado e affordances. O AppShell permanece em `app-shell.css/js` e o backend continua sendo a autoridade real de RBAC.

**Tech Stack:** HTML semântico + CSS + JavaScript vanilla do Design Lab.

### Restrições globais

```text
DO_NOT_CHANGE_PRODUCTION=YES
DO_NOT_CHANGE_BACKEND=YES
DO_NOT_REWRITE_COMPONENTS_CSS=YES
DO_NOT_START_PHASE_L=YES
DO_NOT_START_PHASE_M=YES
DO_NOT_START_PHASE_N=YES
DO_NOT_START_NF02=YES
DO_NOT_MERGE_PR=YES
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
```

### Task 1 — Verdade dos dados e estados

- separar total da coleção de contagem filtrada;
- calcular métricas demonstrativas a partir das próprias fixtures;
- remover pseudo-KPI `Admin`;
- declarar `READY` como estado da fixture;
- materializar contratos distintos para `LOADING`, `EMPTY_DATASET`, `ERROR`, `OFFLINE`, `NO_PERMISSION` e `FILTER_NO_RESULTS`;
- manter ausência de dado diferente de zero inventado.

### Task 2 — Hierarquia da lista

- priorizar `Nome/Matrícula | Unidade | Biometria | Status | Ações`;
- rebaixar username/função para metadado secundário da pessoa;
- manter busca por nome/matrícula e filtro de função;
- não adicionar sorting fictício.

### Task 3 — RBAC demonstrativo

- explicitar papel/permissões da fixture no `body`;
- `Novo funcionário` exige `users:create` e aponta para `03.04-novo-funcionario-v2.html` somente quando permitido;
- ações biométricas exigem `biometrics:manage`;
- usuário sem ação mutável recebe estado textual de leitura, não botão proibido desabilitado;
- `users:view` ausente leva ao contrato `NO_PERMISSION` da coleção;
- nenhum comportamento do Design Lab substitui autorização backend.

### Task 4 — Paginação e responsividade

- remover paginação viva fictícia;
- preservar apenas resumo real de resultados filtrados;
- migrar dimensionamento local tocado para `rem/fr/minmax`;
- usar container query para tabela → cards antes da faixa de overflow problemática;
- preservar ordem DOM e nomes acessíveis.

### Task 5 — Verificação e continuidade

- verificar os sete gaps HIGH de K1 source-level;
- confirmar que `components.css`, produção e backend não foram tocados por K2;
- manter testes automáticos/manuais completos diferidos para Fase N;
- atualizar este checkpoint, roadmap, README do Design Lab e body do PR somente após verificação.

---

## Critério de conclusão

```text
K1_HIGH_GAPS_RECONCILED_SOURCE_LEVEL=7/7
FAKE_PAGINATION=REMOVED
RBAC_AFFORDANCE_CONTRACT=SOURCE_LEVEL
EMPLOYEE_COLLECTION_STATE_CONTRACT=SOURCE_LEVEL
EMPLOYEE_TABLE_CANONICAL_PRIORITY=SOURCE_LEVEL
LOCAL_EMPLOYEES_DIMENSIONING=rem/fr/minmax/container-query
PRODUCTION_CHANGE=NO
```
