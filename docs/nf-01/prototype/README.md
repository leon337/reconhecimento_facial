# NF-01 — Design Lab

Laboratório visual isolado da NF-01.

```text
CANONICAL_APPSHELL=ONE
CURRENT_APPSHELL_OWNER=assets/app-shell.css+app-shell.js
CURRENT_APPSHELL_VERSION=i8
LEGACY_SHELL_OWNER=assets/legacy-shell.css+legacy-shell.js
DASHBOARD_SHARED_APPSHELL=YES
EMPLOYEES_SHARED_APPSHELL=YES
ONBOARDING_SHARED_APPSHELL=YES
I7_LEGACY_SHELL_QUARANTINE=COMPLETE
I8_APPSHELL_STRUCTURAL_ACCEPTANCE=COMPLETE
I8_ACCEPTANCE=PASS_SOURCE_LEVEL_WITH_HARDENING
I9_PHASE_I_APPSHELL_CLOSEOUT=COMPLETE
PHASE_I_DESIGN_LAB_APPSHELL=COMPLETE
PHASE_I_CLOSEOUT_BASIS=SOURCE_LEVEL
UNRESOLVED_PHASE_I_STRUCTURAL_GAPS=0

PHASE_J_DASHBOARD_RECONCILIATION=COMPLETE
J1_DASHBOARD_CANONICAL_GAP_AUDIT=COMPLETE
J1_OUTPUT=../56_NF01_PHASE_J_J1_DASHBOARD_CANONICAL_GAP_AUDIT_2026-08-17.md
J2_DASHBOARD_CANONICAL_RECONCILIATION=COMPLETE
J2_OUTPUT=../57_NF01_PHASE_J_J2_DASHBOARD_CANONICAL_RECONCILIATION_2026-08-17.md
J2_HIGH_GAPS_RECONCILED_SOURCE_LEVEL=6/6
J3_DASHBOARD_POST_RECONCILIATION_ACCEPTANCE=COMPLETE
J3_OUTPUT=../58_NF01_PHASE_J_J3_DASHBOARD_POST_RECONCILIATION_ACCEPTANCE_2026-08-17.md
J3_ACCEPTANCE=PASS_SOURCE_LEVEL_WITH_ONE_CONTINUITY_FIX
PHASE_J_CLOSEOUT_BASIS=SOURCE_LEVEL
UNRESOLVED_DASHBOARD_CANONICAL_GAPS=0
J4_REQUIRED=NO

PHASE_K_EMPLOYEES_RECONCILIATION=COMPLETE
K1_EMPLOYEES_CANONICAL_GAP_AUDIT=COMPLETE
K1_OUTPUT=../59_NF01_PHASE_K_K1_EMPLOYEES_CANONICAL_GAP_AUDIT_2026-08-17.md
K1_AUDIT_RESULT=GAPS_FOUND
K1_HIGH_GAP_THEMES=7
EMPLOYEES_VISUAL_CHANGE_IN_K1=NO
K2_EMPLOYEES_CANONICAL_RECONCILIATION=COMPLETE
K2_OUTPUT=../60_NF01_PHASE_K_K2_EMPLOYEES_CANONICAL_RECONCILIATION_2026-08-17.md
K2_ACCEPTANCE=PASS_SOURCE_LEVEL
K2_HIGH_GAPS_RECONCILED_SOURCE_LEVEL=7/7
EMPLOYEES_VISUAL_CHANGE_IN_K2=YES_DESIGN_LAB_ONLY
K3_EMPLOYEES_POST_RECONCILIATION_ACCEPTANCE=COMPLETE
K3_OUTPUT=../61_NF01_PHASE_K_K3_EMPLOYEES_POST_RECONCILIATION_ACCEPTANCE_2026-08-18.md
K3_ACCEPTANCE=PASS_SOURCE_LEVEL_WITH_ONE_CONTINUITY_FIX
PHASE_K_CLOSEOUT_BASIS=SOURCE_LEVEL
UNRESOLVED_EMPLOYEES_CANONICAL_GAPS=0
K4_REQUIRED=NO

PHASE_L_ONBOARDING_RECONCILIATION=IN_PROGRESS
L1_ONBOARDING_CANONICAL_GAP_AUDIT=COMPLETE
L1_OUTPUT=../62_NF01_PHASE_L_L1_ONBOARDING_CANONICAL_GAP_AUDIT_2026-08-18.md
L1_AUDIT_RESULT=GAPS_FOUND
L1_CRITICAL_GAPS=0
L1_HIGH_GAP_THEMES=9
L1_MEDIUM_GAP_THEMES=7
L1_LOW_DEFERRED_OBSERVATIONS=3
ONBOARDING_VISUAL_CHANGE_IN_L1=NO
L2_ONBOARDING_CANONICAL_RECONCILIATION=COMPLETE
L2_OUTPUT=../63_NF01_PHASE_L_L2_ONBOARDING_CANONICAL_RECONCILIATION_2026-08-18.md
L2_ACCEPTANCE=PASS_SOURCE_LEVEL
L2_HIGH_GAPS_RECONCILED_SOURCE_LEVEL=9/9
ONBOARDING_VISUAL_CHANGE_IN_L2=YES_DESIGN_LAB_ONLY

ACTIVE_SURFACE_LEGACY_SHELL_DEPENDENCY=0
HISTORICAL_V1=screens/03.03-novo-funcionario.html
HISTORICAL_V1_PRESERVED=YES
HISTORICAL_V1_MIGRATED=NO
NEXT_OFFICIAL_PHASE=L_ONBOARDING_RECONCILIATION
NEXT_OFFICIAL_ITEM=L3_ONBOARDING_POST_RECONCILIATION_ACCEPTANCE_GATE
L3_APPROVAL_INFERRED=NO
PRODUCTION_CHANGE=NO
NF02_STARTED=NO
PR_MERGE=NOT_AUTHORIZED
```

I8 endureceu o bootstrap do AppShell e I9 fechou a Fase I somente em base source-level.

J1 auditou o Dashboard sem mudar o visual. J2 executou a reconciliação canônica de `screens/02.01-dashboard.html` + `assets/dashboard-v3.css`. J3 reauditorou o resultado, corrigiu somente metainformação do índice do laboratório e encerrou a Fase J em base source-level.

K1 auditou `screens/03.01-funcionarios.html` + `assets/employees-v1.css` + `assets/employees-v1.js` sem alterar esses arquivos. K2 reconciliou os sete temas HIGH: métricas agora derivam das fixtures e não se confundem com resultados filtrados; o pseudo-KPI `Admin` foi removido; a tabela prioriza Nome/Matrícula, Unidade, Biometria e Status; `Novo funcionário` exige `users:create`; ações biométricas exigem `biometrics:manage`; os estados `LOADING`, `EMPTY_DATASET`, `READY`, `FILTER_NO_RESULTS`, `ERROR`, `OFFLINE` e `NO_PERMISSION` estão separados; e a paginação fictícia foi removida. O CSS local foi normalizado para `rem/fr/minmax` e container query.

K3 reauditorou Funcionários pós-K2. Nenhum gap bloqueante foi encontrado; a única inconsistência objetiva estava no tile de `prototype/index.html`, que ainda descrevia Funcionários como etapa I5. O tile foi atualizado para K3/Fase K reconciliada, sem alterar novamente `03.01-funcionarios.html`, `employees-v1.css` ou `employees-v1.js`. A Fase K foi encerrada em base source-level.

L1 auditou `screens/03.04-novo-funcionario-v2.html` + `assets/new-employee-v2.css` + `assets/new-employee-v2.js` sem alterá-los. L2 reconciliou os nove temas HIGH no Design Lab: stepper horizontal + `Ver etapas`, ContextDrawer sob demanda, StickyFormActions unificadas, affordances demonstrativas de `users:create`/`biometrics:manage`, `NEEDS_REVIEW`, ciclo `VISIBLE_ACTIVE/HIDDEN_RETAINED` separado de `activePayloadPreview`, estados persistentes `PERMISSION_ERROR/OFFLINE/CONFLICT/SAVE_ERROR/SUBMIT_OUTCOME_UNKNOWN`, FieldGroup/ErrorSummary source-level e seis EntityPickers locais demonstrativos. A implementação preserva as oito etapas, AppShell compartilhado e isolamento de produção.

A primeira tentativa de L2 foi interrompida e deixou o roadmap substituído por `PLACEHOLDER` e o checkpoint 63 prematuramente marcado como concluído. A recuperação restaurou o roadmap byte-a-byte antes da implementação real, corrigiu o checkpoint e manteve o histórico sem force-push ou reescrita.

A dívida transversal de `components.css`, a coerência cruzada entre telas e a validação completa de responsividade/acessibilidade permanecem diferidas para seus gates próprios.

Continuam diferidos:

```text
LIVE_HEALTH_OPERATIONAL_UI=NO
RUNTIME_RBAC_ENFORCEMENT=NO
BACKEND_DRAFT_REVISION=NO
REAL_TRANSACTIONAL_IDEMPOTENT_SUBMIT=NO
REMOTE_ENTITY_PICKER=NO
REAL_CAMERA_OR_BIOMETRIC_STORAGE=NO
BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
INTERMEDIATE_WIDTH_VISUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
SCREEN_READER_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```
