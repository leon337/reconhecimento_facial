# NF-01 — Fase K — K2 — Reconciliação canônica de Funcionários

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
K2_EMPLOYEES_CANONICAL_RECONCILIATION=APPROVED_BY_LEANDRO
K2_STATUS=COMPLETE
PHASE_K_EMPLOYEES_RECONCILIATION=IN_PROGRESS
IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY
K2_ACCEPTANCE=PASS_SOURCE_LEVEL
K1_HIGH_GAPS_RECONCILED_SOURCE_LEVEL=7/7

PRODUCTION_CHANGE=NO
PHASE_L=NOT_STARTED
PHASE_M=NOT_STARTED
PHASE_N=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate foi consumida somente para K2. Nenhuma autorização de K3, Fase L, NF-02, produção, deploy ou merge foi inferida.

---

## Plano executado

**Goal:** reconciliar a superfície Funcionários do Design Lab com os gaps comprovados por K1, sem ampliar o escopo funcional.

**Architecture:** `03.01-funcionarios.html` permanece como contrato de conteúdo; `employees-v1.css` permanece responsável apenas pela apresentação local; `employees-v1.js` permanece responsável apenas pela demonstração local de filtros, estados e affordances. O AppShell continua em `app-shell.css/js` e o backend continua sendo a autoridade real de RBAC.

**Tech Stack:** HTML semântico + CSS + JavaScript vanilla do Design Lab.

---

# 1. Resultado executivo

```text
EMPLOYEES_HTML_CHANGED=YES_DESIGN_LAB_ONLY
EMPLOYEES_CSS_CHANGED=YES_DESIGN_LAB_ONLY
EMPLOYEES_JS_CHANGED=YES_DESIGN_LAB_ONLY

EMPLOYEE_FIXTURE_SOURCE=EXPLICIT
EMPLOYEE_COLLECTION_READY_STATE=EXPLICIT
DATASET_TOTAL_SEPARATE_FROM_FILTERED_COUNT=YES
BIOMETRIC_PENDING_DERIVED_FROM_FIXTURES=YES
ADMIN_PSEUDO_KPI=REMOVED

TABLE_PRIORITY=NAME_REGISTRATION|UNIT|BIOMETRIC|STATUS|ACTIONS
ACCOUNT_USERNAME=SECONDARY_METADATA
FUNCTION=SECONDARY_METADATA_AND_FILTER

NEW_EMPLOYEE_PERMISSION=users:create
NEW_EMPLOYEE_TARGET=03.04-novo-funcionario-v2.html
BIOMETRIC_ACTION_PERMISSION=biometrics:manage
ROW_READONLY_FALLBACK=YES
BACKEND_AUTHORITY_PRESERVED=YES

COLLECTION_STATES=LOADING|EMPTY_DATASET|READY|FILTER_NO_RESULTS|ERROR|OFFLINE|NO_PERMISSION
FILTER_NO_RESULTS_DISTINCT_FROM_EMPTY_DATASET=YES
FAKE_PAGINATION=REMOVED

LOCAL_EMPLOYEES_DIMENSIONING=rem/fr/minmax/container-query
INTERMEDIATE_TABLE_TO_CARD_SWITCH=CONTAINER_AWARE
REDUCED_MOTION_LOCAL_SUPPORT=YES
COMPONENTS_CSS_GLOBAL_REWRITE=NO
```

---

# 2. Fechamento dos gaps HIGH de K1

## K1-H1 — Resumos sem contrato confiável de significado/origem

```text
STATUS=CLOSED_SOURCE_LEVEL
```

- o total da coleção é derivado de `data-employee-row` e não é mais sobrescrito pelos filtros;
- a contagem de biometrias pendentes é derivada das próprias fixtures;
- os cards declaram fonte local e estado `READY`;
- o pseudo-KPI `Admin` foi removido;
- a contagem filtrada permanece no rodapé como informação de consulta, separada do total da coleção.

## K1-H2 — Hierarquia da tabela divergente

```text
STATUS=CLOSED_SOURCE_LEVEL
```

A hierarquia atual é:

```text
Funcionário / Matrícula
Unidade
Biometria
Status
Ações
```

Username e função foram rebaixados para metadado da pessoa. `FUNCIONARIO != CONTA_DE_USUARIO` permanece preservado.

## K1-H3 — CTA Novo funcionário sem `users:create`

```text
STATUS=CLOSED_SOURCE_LEVEL
```

O CTA usa `data-requires-permission="users:create"` e aponta para o fluxo canônico do Design Lab `03.04-novo-funcionario-v2.html` somente quando a permissão demonstrativa existe.

## K1-H4 — ações biométricas sem `biometrics:manage`

```text
STATUS=CLOSED_SOURCE_LEVEL
```

Cada CTA de cadastrar/recadastrar biometria exige `biometrics:manage`. Quando a ação mutável não está disponível, a linha usa o texto `Somente leitura` em vez de expor um botão proibido apenas desabilitado.

## K1-H5 — estados da coleção incompletos / Empty conflado

```text
STATUS=CLOSED_SOURCE_LEVEL
```

Foram materializados contratos distintos para:

```text
LOADING
EMPTY_DATASET
READY
FILTER_NO_RESULTS
ERROR
OFFLINE
NO_PERMISSION
```

`FILTER_NO_RESULTS` ocorre apenas dentro de uma coleção `READY` após busca/filtro local. `EMPTY_DATASET` é um estado de coleção separado. Falha e offline também permanecem distintos.

## K1-H6 — paginação fictícia

```text
STATUS=CLOSED
FAKE_PAGINATION=REMOVED
```

Os botões `1 / 2 / Próxima` foram removidos. A tela informa explicitamente que a amostra local não simula paginação remota.

## K1-H7 — variantes RBAC das ações por linha

```text
STATUS=CLOSED_AS_SOURCE_CONTRACT
```

O `body` declara papel e permissões da fixture. `employees-v1.js` aplica visibilidade de affordances por `data-requires-permission`, sem fingir autorização real de backend.

Contrato demonstrativo resultante:

```text
admin/super_admin => leitura + criar + biometria quando permissões presentes
manager           => leitura + criar; biometria ausente
auditor           => leitura; mutações ausentes
operator          => não deve receber a superfície admin; NO_PERMISSION é contrato de fallback, não substituto de roteamento/autorização backend
```

---

# 3. Responsividade e dimensionamento local

`employees-v1.css` foi normalizado apenas na camada local tocada por K2:

```text
LAYOUT_UNITS=rem/fr/minmax
PX_GENERAL_LAYOUT_POLICY=REMOVED
PX_REMAINING=1px_TECHNICAL_BORDERS_ONLY
CONTAINER_NAME=employee-list
TABLE_TO_CARD_SWITCH=@container max-width 55rem
NARROW_CARD_SWITCH=@container max-width 30rem
VIEWPORT_TOOLBAR_SWITCH=64rem
VIEWPORT_SINGLE_COLUMN_SWITCH=48rem
REDUCED_MOTION=SUPPORTED
```

A antiga faixa problemática `min-width: 840px` + conversão para cards apenas em `720px` deixou de governar a resposta. A tabela ainda possui largura mínima em `rem`, mas a conversão para cards ocorre por espaço real do container antes de a composição precisar espremer a tabela.

---

# 4. Verificação source-level

Arquivos verificados após implementação:

```text
docs/nf-01/prototype/screens/03.01-funcionarios.html
docs/nf-01/prototype/assets/employees-v1.css
docs/nf-01/prototype/assets/employees-v1.js
```

Blobs verificados:

```text
EMPLOYEES_HTML_SHA=847fe0e08e08cbfbf4703f83c774ea7091fee8ca
EMPLOYEES_CSS_SHA=ea2c2ff894f8997aefcb25b9535b934038ceeac5
EMPLOYEES_JS_SHA=edd73fb59c01ae71efc85b3a0bafe69074b0216a
```

Comparação pré-K2 `8d8ab199a3a898dee29664dcacbf4bdcbf065162` → implementação `057e1238c56daddf17a0e5232c3f642a870116a1` confirmou exatamente quatro caminhos nessa etapa:

```text
docs/nf-01/60_NF01_PHASE_K_K2_EMPLOYEES_CANONICAL_RECONCILIATION_2026-08-17.md
docs/nf-01/prototype/screens/03.01-funcionarios.html
docs/nf-01/prototype/assets/employees-v1.css
docs/nf-01/prototype/assets/employees-v1.js
```

Nenhum `components.css`, AppShell, produção ou backend entrou nessa comparação.

Verificações textuais:

```text
SUMMARY_ADMIN_PSEUDO_KPI_ABSENT=PASS
FAKE_PAGINATION_CONTROLS_ABSENT=PASS
USERS_CREATE_PERMISSION_METADATA=PASS
BIOMETRICS_MANAGE_PERMISSION_METADATA=PASS
UNIT_COLUMN_PRESENT=PASS
STATUS_COLUMN_PRESENT=PASS
FUNCTION_FILTER_SEMANTICS=PASS
COLLECTION_STATE_PANELS=PASS
FILTER_NO_RESULTS_SEPARATE=PASS
CONTAINER_QUERY_PRESENT=PASS
GENERAL_PX_LAYOUT_REMOVED=PASS
```

---

# 5. Limites do aceite

K2 não declara homologação completa.

```text
BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
INTERMEDIATE_WIDTH_VISUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
SCREEN_READER_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

Testes unitários e de integração derivados por K1 continuam como contrato futuro, incluindo:

```text
users:create absent => New employee CTA absent
biometrics:manage absent => biometric CTA absent
filtered visible count != dataset total
FILTER_NO_RESULTS != EMPTY_DATASET
ERROR != EMPTY_DATASET
OFFLINE != ERROR
no pagination without pagination dataset/contract
manager => no biometric affordance
auditor => read-only
operator => no Employees/AppShell administrative surface
```

---

# 6. Itens diferidos preservados

```text
GLOBAL_COMPONENTS_CSS_DIMENSIONING_DEBT=DEFERRED
DETAIL_DRAWER=DEFERRED_UNTIL_NEEDED
CROSS_SCREEN_COHERENCE=DEFERRED_TO_PHASE_M
FULL_RESPONSIVE_A11Y_VALIDATION=DEFERRED_TO_PHASE_N
RUNTIME_RBAC_ENFORCEMENT=NOT_IMPLEMENTED_IN_NF01
```

---

# 7. Próxima fronteira

K2 implementa a reconciliação, mas não fecha automaticamente a Fase K.

```text
PHASE_K_EMPLOYEES_RECONCILIATION=IN_PROGRESS
K1=COMPLETE
K2=COMPLETE
K3=NOT_STARTED

NEXT_OFFICIAL_PHASE=K_EMPLOYEES_RECONCILIATION
NEXT_OFFICIAL_ITEM=K3_DEFINITION_GATE
```

K3 deverá reauditar Funcionários pós-K2, identificar regressões/gaps residuais e decidir se a Fase K pode ser encerrada em base source-level.
