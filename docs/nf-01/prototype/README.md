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

PHASE_J_DASHBOARD_RECONCILIATION=IN_PROGRESS
J1_DASHBOARD_CANONICAL_GAP_AUDIT=COMPLETE
J1_OUTPUT=../56_NF01_PHASE_J_J1_DASHBOARD_CANONICAL_GAP_AUDIT_2026-08-17.md
J2_DASHBOARD_CANONICAL_RECONCILIATION=COMPLETE
J2_OUTPUT=../57_NF01_PHASE_J_J2_DASHBOARD_CANONICAL_RECONCILIATION_2026-08-17.md
J2_HIGH_GAPS_RECONCILED_SOURCE_LEVEL=6/6

ACTIVE_SURFACE_LEGACY_SHELL_DEPENDENCY=0
HISTORICAL_V1=screens/03.03-novo-funcionario.html
HISTORICAL_V1_PRESERVED=YES
HISTORICAL_V1_MIGRATED=NO
NEXT_OFFICIAL_PHASE=J_DASHBOARD_RECONCILIATION
NEXT_OFFICIAL_ITEM=J3_DEFINITION_GATE
PRODUCTION_CHANGE=NO
NF02_STARTED=NO
PR_MERGE=NOT_AUTHORIZED
```

I8 endureceu o bootstrap do AppShell e I9 fechou a Fase I somente em base source-level.

J1 auditou o Dashboard sem mudar o visual. J2 executou a primeira reconciliação canônica de `screens/02.01-dashboard.html` + `assets/dashboard-v3.css`: removeu tendência sem fonte e quick actions inadequadas, deixou uma única ação `Ver registros`, explicitou origem/estado das fixtures, adicionou contratos de estados alternativos, protegeu Atenção necessária contra falso verde e registrou metadados de permissão sem fingir enforcement backend.

J2 também converteu o dimensionamento local tocado para `rem/fr/minmax`; a dívida transversal de `components.css` permanece diferida para gate próprio.

A validação de J2 é source-level do protótipo. O Design Lab não declara teste automatizado, homologação visual ou enforcement RBAC de produção.

Continuam diferidos:

```text
LIVE_HEALTH_OPERATIONAL_UI=NO
RUNTIME_RBAC_ENFORCEMENT=NO
BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
INTERMEDIATE_WIDTH_VISUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
SCREEN_READER_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```
