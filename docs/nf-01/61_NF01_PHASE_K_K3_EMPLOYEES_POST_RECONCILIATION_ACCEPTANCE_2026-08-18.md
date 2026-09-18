# NF-01 — Fase K — K3 — Aceite pós-reconciliação de Funcionários

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-18  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
K3_EMPLOYEES_POST_RECONCILIATION_ACCEPTANCE=APPROVED_BY_LEANDRO
K3_STATUS=COMPLETE
K3_ACCEPTANCE=PASS_SOURCE_LEVEL_WITH_ONE_CONTINUITY_FIX
PHASE_K_EMPLOYEES_RECONCILIATION=COMPLETE
PHASE_K_CLOSEOUT_BASIS=SOURCE_LEVEL
UNRESOLVED_EMPLOYEES_CANONICAL_GAPS=0
K4_REQUIRED=NO

IMPLEMENTATION=AUDIT_AND_CONTINUITY_METADATA_ONLY
EMPLOYEES_HTML_CHANGED_IN_K3=NO
EMPLOYEES_CSS_CHANGED_IN_K3=NO
EMPLOYEES_JS_CHANGED_IN_K3=NO
PRODUCTION_CHANGE=NO
PHASE_L=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate foi consumida somente para K3. Nenhuma autorização de Fase L, NF-02, produção, deploy ou merge é inferida.

---

# 1. Objetivo

Reauditar `Funcionários` após K2 contra K1, contratos canônicos de RBAC/estados e wireframe. K3 não abre novo redesign; somente uma inconsistência objetiva poderia receber correção mínima.

Fontes:

```text
docs/nf-01/04_ROLES_PERMISSIONS_AND_STATES.md
docs/nf-01/07_WIREFRAMES.md
docs/nf-01/13_NF01_REMAINING_WORK_ROADMAP.md
docs/nf-01/59_NF01_PHASE_K_K1_EMPLOYEES_CANONICAL_GAP_AUDIT_2026-08-17.md
docs/nf-01/60_NF01_PHASE_K_K2_EMPLOYEES_CANONICAL_RECONCILIATION_2026-08-17.md
docs/nf-01/prototype/screens/03.01-funcionarios.html
docs/nf-01/prototype/assets/employees-v1.css
docs/nf-01/prototype/assets/employees-v1.js
docs/nf-01/prototype/index.html
```

---

# 2. Reauditoria dos sete gaps HIGH de K1

```text
K1-H1 source/state-aware summaries........................ PASS_SOURCE_LEVEL
K1-H2 canonical table priority............................. PASS_SOURCE_LEVEL
K1-H3 users:create-aware New employee CTA.................. PASS_SOURCE_LEVEL
K1-H4 biometrics:manage-aware biometric actions............ PASS_SOURCE_LEVEL
K1-H5 distinct collection/filter states.................... PASS_SOURCE_LEVEL
K1-H6 fake live pagination removed......................... PASS_SOURCE_LEVEL
K1-H7 permission-aware row affordances..................... PASS_SOURCE_LEVEL
```

## H1 — resumo e origem dos dados

- total da amostra é separado da quantidade filtrada;
- total deriva de `rows.length`;
- biometria pendente deriva das fixtures;
- pseudo-KPI `Admin` não existe mais;
- fonte demonstrativa está declarada.

## H2 — hierarquia da tabela

Contrato atual:

```text
Funcionário/Matrícula | Unidade | Biometria | Status | Ações
```

Username e função ficam como metadados secundários. `FUNCIONARIO != CONTA_DE_USUARIO` permanece preservado.

## H3/H4/H7 — affordances por permissão

```text
Novo funcionário     => users:create
Ação biométrica      => biometrics:manage
Sem mutação permitida=> Somente leitura
users:view ausente   => NO_PERMISSION da coleção
```

Isto é contrato visual do Design Lab. O backend continua sendo a autoridade real e precisa revalidar qualquer requisição.

## H5 — estados

```text
LOADING
EMPTY_DATASET
READY
FILTER_NO_RESULTS
ERROR
OFFLINE
NO_PERMISSION
```

`FILTER_NO_RESULTS != EMPTY_DATASET != ERROR` e `OFFLINE != ERROR`.

## H6 — paginação

Nenhuma paginação remota é simulada sobre as seis fixtures. A paginação somente pode reaparecer quando existir dataset/contrato real que a sustente.

---

# 3. Reauditoria dos temas MEDIUM de K1

```text
ACCOUNT_USERNAME_DEMOTED=PASS_SOURCE_LEVEL
BIOMETRIC_ACTION_ACCESSIBLE_NAME_CONTEXTUAL=PASS_SOURCE_LEVEL
FAKE_SORTING_NOT_INTRODUCED=PASS_SOURCE_LEVEL
INTERMEDIATE_RESPONSIVE_GAP_RECONCILED=PASS_SOURCE_LEVEL
LOCAL_GENERAL_PX_LAYOUT_REMOVED=PASS_SOURCE_LEVEL
NEW_EMPLOYEE_V2_LINK_WHEN_PERMITTED=PASS_SOURCE_LEVEL
```

A camada local usa `rem/fr/minmax` e container query. `1px` permanece apenas como exceção técnica para bordas.

---

# 4. AppShell e escopo

A comparação do head pré-K2 `8d8ab199a3a898dee29664dcacbf4bdcbf065162` com o head pós-K2 confirmou que a implementação tocou somente:

```text
docs/nf-01/13_NF01_REMAINING_WORK_ROADMAP.md
docs/nf-01/60_NF01_PHASE_K_K2_EMPLOYEES_CANONICAL_RECONCILIATION_2026-08-17.md
docs/nf-01/prototype/README.md
docs/nf-01/prototype/assets/employees-v1.css
docs/nf-01/prototype/assets/employees-v1.js
docs/nf-01/prototype/screens/03.01-funcionarios.html
```

K2 não alterou `components.css`, AppShell, backend ou produção.

```text
CANONICAL_APPSHELL=ONE
EMPLOYEES_SHARED_APPSHELL=YES
ACTIVE_SURFACE_LEGACY_SHELL_DEPENDENCY=0
RUNTIME_RBAC_ENFORCEMENT=NOT_IMPLEMENTED_IN_NF01
```

---

# 5. Finding K3 — continuidade do índice do Design Lab

A auditoria encontrou um único desvio objetivo fora da superfície funcional:

```text
K3_BLOCKING_GAPS_FOUND=0
K3_CONTINUITY_DRIFT_FOUND=1
K3_CONTINUITY_DRIFT_FIXED=1
K3_CONTINUITY_FIX=docs/nf-01/prototype/index.html
```

Antes:

```text
03.01 · I5
Funcionários Desktop V1
Consumidor do AppShell.
```

Depois:

```text
03.01 · K3
Funcionários canônico
Fase K reconciliada em base source-level.
```

A correção é exclusivamente metainformação do Design Lab. `03.01-funcionarios.html`, `employees-v1.css` e `employees-v1.js` não foram alterados em K3.

---

# 6. Limites do aceite

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

Logo:

```text
PHASE_K_COMPLETE_SOURCE_LEVEL != NF01_COMPLETE
PHASE_K_COMPLETE_SOURCE_LEVEL != FULL_VISUAL_ACCEPTANCE
PHASE_K_COMPLETE_SOURCE_LEVEL != AUTOMATED_TEST_PASS
PHASE_K_COMPLETE_SOURCE_LEVEL != PRODUCTION_READY
```

A homologação visual, responsiva, acessível e automatizada continua diferida para a Fase N.

---

# 7. Fechamento da Fase K

```text
K1=COMPLETE
K2=COMPLETE
K3=COMPLETE
K4_REQUIRED=NO

PHASE_K_EMPLOYEES_RECONCILIATION=COMPLETE
PHASE_K_RESULT=COMPLETE_SOURCE_LEVEL
UNRESOLVED_EMPLOYEES_CANONICAL_GAPS=0
```

Próxima fronteira:

```text
NEXT_OFFICIAL_PHASE=L_ONBOARDING_RECONCILIATION
NEXT_OFFICIAL_ITEM=L1_DEFINITION_GATE
```

L1 não é iniciado nem aprovado por este checkpoint.