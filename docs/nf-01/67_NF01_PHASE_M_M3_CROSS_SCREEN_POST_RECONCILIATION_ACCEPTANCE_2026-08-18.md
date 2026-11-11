# NF-01 — Fase M — M3 — Aceite pós-reconciliação entre telas

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-18  
**Autoridade humana:** LEANDRO

## Gate e estado

```text
M3_CROSS_SCREEN_POST_RECONCILIATION_ACCEPTANCE=APPROVED_BY_LEANDRO
M3_STATUS=COMPLETE
M3_ACCEPTANCE=PASS_SOURCE_LEVEL_WITH_TWO_CONTINUITY_FIXES
PHASE_M_CROSS_SCREEN_COHERENCE=COMPLETE
PHASE_M_CLOSEOUT_BASIS=SOURCE_LEVEL

M3_BLOCKING_GAPS_FOUND=0
M3_CONTINUITY_DRIFT_FOUND=2
M3_CONTINUITY_DRIFT_FIXED=2
UNRESOLVED_CROSS_SCREEN_BLOCKING_GAPS=0
M4_REQUIRED=NO

IMPLEMENTATION=AUDIT_AND_CONTINUITY_FIXES_ONLY
DASHBOARD_SOURCE_CHANGED_IN_M3=NO
EMPLOYEES_SOURCE_CHANGED_IN_M3=NO
ONBOARDING_SOURCE_CHANGED_IN_M3=NO
SHARED_INTERACTIONS_CHANGED_IN_M3=NO
APPSHELL_CHANGED_IN_M3=NO
M3_PROTOTYPE_README_CHANGED=YES_CONTINUITY_PROPAGATION
PRODUCTION_CHANGE=NO
PHASE_N=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate foi consumida somente para M3. Nenhuma autorização de Fase N, NF-02, produção, deploy ou merge é inferida.

---

## 1. Objetivo

Reauditar o resultado de M2 como uma única jornada de produto e decidir se a Fase M pode ser encerrada em base source-level.

Linha de montagem auditada:

```text
Dashboard
   ↓ handoff real + filtro
Funcionários
   ↓ preservação do estado da lista
Novo funcionário
   ↓ retorno à mesma sessão
Funcionários
```

---

## 2. Fontes reauditas

```text
docs/nf-01/65_NF01_PHASE_M_M1_CROSS_SCREEN_COHERENCE_AUDIT_2026-08-18.md
docs/nf-01/66_NF01_PHASE_M_M2_CROSS_SCREEN_COHERENCE_RECONCILIATION_2026-08-18.md
docs/nf-01/13_NF01_REMAINING_WORK_ROADMAP.md
docs/nf-01/prototype/README.md
docs/nf-01/prototype/index.html
docs/nf-01/prototype/screens/02.01-dashboard.html
docs/nf-01/prototype/screens/03.01-funcionarios.html
docs/nf-01/prototype/assets/employees-v1.js
docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
docs/nf-01/prototype/assets/interactions.js
docs/nf-01/prototype/assets/new-employee-v2.js
```

---

## 3. Reauditoria dos cinco temas HIGH de M1

```text
M1-H1 identidade das fixtures entre telas................ PASS_SOURCE_LEVEL
M1-H2 contexto/unidade compartilhados..................... PASS_SOURCE_LEVEL
M1-H3 proveniência da amostra............................. PASS_SOURCE_LEVEL
M1-H4 Dashboard -> Funcionários handoff real.............. PASS_SOURCE_LEVEL
M1-H5 principal/permissões compartilhados................. PASS_SOURCE_LEVEL
```

### H1 — identidade

Dashboard e Funcionários permanecem coerentes para a amostra compartilhada:

```text
Maria Silva  = 00123
João Souza   = 00124
Lucas Santos = 00131
Ana Paula    = 00142
```

### H2 — contexto

```text
EMPRESA=Potiguar Locações
APP_CONTEXT=Galpão principal · contexto demonstrativo
PROFILE=Administrador Demo
ROLE=Admin · perfil fictício
```

No onboarding, `app-shell.js` monta o shell; `interactions.js` sincroniza o contexto/principal visível; `new-employee-v2.js` inicializa depois com o conjunto demonstrativo sincronizado.

### H3 — proveniência

```text
SHARED_EMPLOYEE_SOURCE=fixture:employees-k2
DASHBOARD_EMPLOYEE_COUNT=6
EMPLOYEES_DATASET_COUNT=6
DASHBOARD_PENDING_BIOMETRICS=2
EMPLOYEES_PENDING_BIOMETRICS=2_DERIVED_FROM_SAMPLE
REGISTROS_HOJE_SOURCE=SEPARATE_RECORD_FIXTURE
```

### H4 — handoff

```text
Dashboard
→ 03.01-funcionarios.html?biometric=missing&source=dashboard
→ employees-v1.js reconhece query explícita
→ biometric=missing prevalece sobre estado restaurado
→ lista preserva filtros em sessionStorage escopado ao contexto
```

### H5 — principal e permissões

```text
SHARED_DEMO_PROFILE=Administrador Demo|admin
SHARED_DEFAULT_PERMISSIONS=users:view users:create biometrics:manage punch:view punch:create
ONBOARDING_PROFILE_SELECTOR=EXPLICIT_TEST_OVERRIDE
RUNTIME_BACKEND_RBAC=NOT_IMPLEMENTED_IN_NF01
```

---

## 4. Drifts encontrados e corrigidos

### M3-D1 — roadmap da Fase M desatualizado

Antes de M3, `13_NF01_REMAINING_WORK_ROADMAP.md` ainda declarava:

```text
M Coerência entre telas.... NOT_STARTED
NEXT_OFFICIAL_ITEM=M1_CROSS_SCREEN_COHERENCE_AUDIT_GATE
```

M3 sincronizou o roadmap para:

```text
PHASE_M_CROSS_SCREEN_COHERENCE=COMPLETE
M1=COMPLETE
M2=COMPLETE
M3=COMPLETE
PHASE_M_CLOSEOUT_BASIS=SOURCE_LEVEL
UNRESOLVED_CROSS_SCREEN_BLOCKING_GAPS=0
M4_REQUIRED=NO
NEXT_OFFICIAL_PHASE=N_DESIGN_LAB_VALIDATION
NEXT_OFFICIAL_ITEM=N1_DESIGN_LAB_VALIDATION_DEFINITION_GATE
```

O roadmap foi normalizado como índice canônico de estado. Detalhes históricos continuam preservados nos checkpoints numerados e no histórico Git; nenhuma decisão congelada foi modificada.

### M3-D2 — `V2` ainda visível no índice do Design Lab

`prototype/index.html` ainda exibia `Novo Funcionário V2 canônico`, embora M2 já tivesse definido `Novo Funcionário` como linguagem visível da superfície ativa.

M3 alterou somente essa rotulagem para:

```text
Novo Funcionário canônico
```

O nome técnico do arquivo `03.04-novo-funcionario-v2.html` permanece inalterado.

---

## 5. Arquivos alterados em M3

```text
docs/nf-01/prototype/index.html
docs/nf-01/13_NF01_REMAINING_WORK_ROADMAP.md
docs/nf-01/67_NF01_PHASE_M_M3_CROSS_SCREEN_POST_RECONCILIATION_ACCEPTANCE_2026-08-18.md
docs/nf-01/prototype/README.md   # propagação de continuidade M3
```

Não foram alterados em M3:

```text
02.01-dashboard.html
03.01-funcionarios.html
employees-v1.js
03.04-novo-funcionario-v2.html
interactions.js
new-employee-v2.js
app-shell.css
app-shell.js
produção
backend
```

---

## 6. Aceite source-level

```text
M3_SHARED_EMPLOYEE_IDENTITIES=PASS_SOURCE_LEVEL
M3_SHARED_CONTEXT=PASS_SOURCE_LEVEL
M3_SHARED_FIXTURE_PROVENANCE=PASS_SOURCE_LEVEL
M3_DASHBOARD_TO_EMPLOYEES_HANDOFF=PASS_SOURCE_LEVEL
M3_SHARED_DEMO_PRINCIPAL_AND_PERMISSIONS=PASS_SOURCE_LEVEL
M3_EMPLOYEES_LIST_STATE_RESTORE=PASS_SOURCE_LEVEL
M3_ONBOARDING_NO_REAL_LIST_MUTATION=PASS_SOURCE_LEVEL
M3_VISIBLE_ONBOARDING_NAME_WITHOUT_V2=PASS_SOURCE_LEVEL_AFTER_CONTINUITY_FIX
M3_ROADMAP_CONTINUITY=PASS_AFTER_SYNC
M3_PROTOTYPE_README_CONTINUITY=PASS_AFTER_SYNC
```

---

## 7. Validação ainda diferida

```text
M3_PASS_SOURCE_LEVEL != FULL_VISUAL_ACCEPTANCE
M3_PASS_SOURCE_LEVEL != FULL_ACCESSIBILITY_ACCEPTANCE
M3_PASS_SOURCE_LEVEL != PRODUCTION_READY

BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
INTERMEDIATE_WIDTH_VISUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
SCREEN_READER_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

Os testes unitários e de integração derivados em J/K/L/M continuam requisitos para a trilha de validação. A análise source-level não é tratada como substituto desses testes.

---

## 8. Resultado da Fase M

```text
PHASE_M_RESULT=COMPLETE_SOURCE_LEVEL
PHASE_M_COMPLETE != NF01_COMPLETE
UNRESOLVED_CROSS_SCREEN_BLOCKING_GAPS=0
M4_REQUIRED=NO
FULL_VISUAL_ACCEPTANCE=DEFERRED_TO_PHASE_N
FULL_ACCESSIBILITY_ACCEPTANCE=DEFERRED_TO_PHASE_N
AUTOMATED_ACCEPTANCE=DEFERRED_TO_PHASE_N
```

---

## 9. Próximo gate

```text
NEXT_OFFICIAL_PHASE=N_DESIGN_LAB_VALIDATION
NEXT_OFFICIAL_ITEM=N1_DESIGN_LAB_VALIDATION_DEFINITION_GATE
N1_APPROVAL_INFERRED=NO
```

A Fase N não é iniciada por este checkpoint.

---

## 10. Invariantes

```text
app/**=UNCHANGED
templates/**=UNCHANGED
static/**=UNCHANGED
migrations/**=UNCHANGED
DECISOES_CONGELADAS.md=UNCHANGED
backend/routes=UNCHANGED
NF02=NOT_STARTED
Ponto_to_AttendanceEvent=NOT_EXECUTED
AI=NOT_IMPLEMENTED
OBSERVABILITY_BACKEND=NOT_IMPLEMENTED
DEPLOY=NO
PRODUCTION_HOMOLOGATION=NO
LEGAL_CONFORMITY_DECLARED=NO
FINAL_HUMAN_GATE=NOT_READY
PR_MERGE=BLOCKED_UNTIL_EXPLICIT_APPROVAL
```
