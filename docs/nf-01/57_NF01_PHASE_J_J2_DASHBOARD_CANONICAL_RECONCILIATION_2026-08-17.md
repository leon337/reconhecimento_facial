# NF-01 — Fase J — J2 — Reconciliação canônica do Dashboard

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
J2_DASHBOARD_CANONICAL_RECONCILIATION=APPROVED_BY_LEANDRO
J2_STATUS=COMPLETE
PHASE_J_DASHBOARD_RECONCILIATION=IN_PROGRESS
IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY

TARGET_HTML=docs/nf-01/prototype/screens/02.01-dashboard.html
TARGET_CSS=docs/nf-01/prototype/assets/dashboard-v3.css

PRODUCTION_CHANGE=NO
PHASE_K=NOT_STARTED
PHASE_L=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate consumiu exclusivamente a primeira reconciliação visual/semântica do Dashboard a partir da matriz J1. Nenhum código de produção, backend, migration, NF-02, deploy ou merge foi autorizado.

## Resultado executivo

```text
J1_HIGH_GAP_THEMES=6
J2_HIGH_GAPS_RECONCILED_SOURCE_LEVEL=6/6
J2_VISUAL_RECONCILIATION=COMPLETE_FOR_APPROVED_SCOPE

APPSHELL_PRESERVED=YES
PAGE_HEADER_PRESERVED=YES
THREE_CANONICAL_KPI_CONCEPTS=PRESERVED
RECENT_ACTIVITY_CONCEPT=PRESERVED
ATTENTION_CONCEPT=PRESERVED
DEMO_DATA_NOTICE=PRESERVED_AND_HARDENED
AI_PREDIX_PRIMARY_CARD=NO
PUNCH_INSIDE_ADMIN_DASHBOARD=NO
```

## Reconciliação dos achados J1

### J1-H1 — MetricCards sem contrato completo de estado/origem

Resolvido no Design Lab por:

```text
VISIBLE_READY_FIXTURE_STATE=EXPLICIT
DATA_SOURCE_METADATA=EXPLICIT
CONTEXT_METADATA=EXPLICIT
LAST_UPDATED_FOR_RECORDS=EXPLICIT

STATE_TEMPLATES=
  LOADING
  EMPTY
  ERROR
  OFFLINE
  NO_PERMISSION
  TELEMETRY_UNAVAILABLE
```

Os templates permanecem dentro de `<template>` e portanto não simulam conteúdo vivo. São contrato visual/source-level para implementação futura.

### J1-H2 — tendência `+2 no mês` sem fonte canônica

```text
UNSOURCED_MONTHLY_TREND=REMOVED
EMPLOYEE_TOTAL_CONCEPT=PRESERVED
```

O Dashboard não inventa tendência derivada que o contrato canônico não consegue sustentar.

### J1-H3 — Atividade recente sem variantes de estado

```text
CURRENT_ACTIVITY_STATE=READY_DEMO
ACTIVITY_SOURCE=EXPLICIT_FIXTURE
DUPLICATE_RECORD_ACTION=REMOVED
PRIMARY_RECORDS_ACTION=ONE
REQUIRED_PERMISSION=punch:view

ACTIVITY_STATE_TEMPLATES=
  LOADING
  EMPTY
  ERROR
  OFFLINE
  NO_PERMISSION
```

### J1-H4 — falso verde em Atenção necessária

O texto anterior `Sem outras pendências` foi removido.

```text
FALSE_GREEN_SUMMARY=REMOVED
ATTENTION_SOURCE_POLICY=EXPLICIT
NO_SIGNAL_DOES_NOT_MEAN_ALL_CLEAR=YES
```

A superfície agora informa que somente itens com fonte confirmada devem aparecer e que ausência de sinal não autoriza inferência de normalidade.

### J1-H5 — Cadastrar biometria genérico sem entidade/contexto

```text
GENERIC_DASHBOARD_BIOMETRIC_ACTION=REMOVED
GENERIC_DASHBOARD_EMPLOYEE_CREATE_ACTION=REMOVED
QUICK_ACTIONS_PANEL=REMOVED
BIOMETRIC_ACTION_REMAINS_CONTEXTUAL_TO_EMPLOYEE_FLOW=YES
```

`Ver registros` permanece no Dashboard como ação operacional de leitura condicionada a `punch:view`.

### J1-H6 — RBAC não materializado nas variantes

J2 materializa o contrato source-level sem fingir enforcement de produção:

```text
VISIBLE_DEMO_ROLE=admin
VISIBLE_DEMO_PERMISSIONS=EXPLICIT_DATA_METADATA
RECORDS_ACTION_PERMISSION=punch:view
ATTENTION_EMPLOYEE_VIEW_PERMISSION=users:view
DASHBOARD_NO_PERMISSION_TEMPLATE=DEFINED
OPERATOR_ADMIN_SHELL_ACCESS=NO_BY_CANONICAL_CONTRACT
RUNTIME_RBAC_ENFORCEMENT=NOT_IMPLEMENTED_IN_NF01
BACKEND_REMAINS_AUTHORITY=YES
```

A NF-01 continua sendo protótipo; os `data-*` não substituem autorização backend.

## Dimensionamento local

J2 substituiu a política local anterior em `dashboard-v3.css` por unidades relativas no escopo tocado:

```text
LOCAL_LAYOUT_UNIT=rem/fr/minmax
KPI_GRID=auto-fit + minmax
LOCAL_BREAKPOINTS=rem
DASHBOARD_V3_GENERAL_LAYOUT_PX=REMOVED
COMPONENTS_CSS_GLOBAL_PX_DEBT=DEFERRED
```

Não houve reescrita transversal de `components.css` porque J1 explicitamente diferiu essa dívida para gate próprio.

## Saúde operacional

```text
LIVE_HEALTH_ACTION=NOT_ADDED
HEALTH_OPERATIONAL_ROLE=DEFERRED
HEALTHY_WITHOUT_SIGNAL=PROHIBITED
OBSERVABILITY_BACKEND=NOT_IMPLEMENTED
```

A posição conceitual de saúde permanece reservada nos documentos canônicos, mas não é apresentada como funcionalidade viva.

## Source-level validation de J2

```text
DASHBOARD_USES_SHARED_APPSHELL=PASS
SINGLE_MAIN=PASS_SOURCE_LEVEL
CANONICAL_KPI_COUNT=3
UNSOURCED_MONTHLY_TREND_PRESENT=NO
QUICK_ACTION_EMPLOYEE_CREATE_PRESENT=NO
QUICK_ACTION_GENERIC_BIOMETRIC_PRESENT=NO
RECORDS_PRIMARY_ACTION_COUNT=1_SOURCE_LEVEL
RECORDS_REQUIRED_PERMISSION=punch:view
FALSE_GREEN_NO_OTHER_PENDING_TEXT_PRESENT=NO
ATTENTION_SOURCE_POLICY_PRESENT=YES
METRIC_STATE_TEMPLATES_PRESENT=YES
ACTIVITY_STATE_TEMPLATES_PRESENT=YES
DASHBOARD_NO_PERMISSION_TEMPLATE_PRESENT=YES
DEMO_DATA_DISCLOSURE_PRESENT=YES
DASHBOARD_V3_LOCAL_BREAKPOINT_UNIT=rem
```

## Limites da validação

J2 é Design Lab. Nenhum novo teste automatizado foi declarado como executado:

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

Portanto:

```text
J2_COMPLETE != PHASE_J_COMPLETE
J2_COMPLETE != VISUAL_HOMOLOGATION
J2_COMPLETE != AUTOMATED_TEST_PASS
J2_COMPLETE != PRODUCTION_READY
```

## Testes derivados preservados

### Unitários futuros

```text
metric state resolver => LOADING|READY|EMPTY|ERROR|OFFLINE|NO_PERMISSION
unsourced metric derivative => not rendered
permission missing => forbidden action not rendered
attention source absent => no false-green summary
records action => hidden without punch:view
```

### Integração futura

```text
admin/super_admin => permitted operational Dashboard affordances
manager => no biometrics:manage affordance
auditor => read-only affordances only
operator => no admin Dashboard/AppShell

Dashboard source failure
→ explicit state
→ no invented zero
→ no invented healthy/all-clear
```

## Próxima fronteira

```text
NEXT_OFFICIAL_PHASE=J_DASHBOARD_RECONCILIATION
NEXT_OFFICIAL_ITEM=J3_DEFINITION_GATE
```

J3 deve auditar o resultado pós-J2 e decidir o próximo incremento da Fase J. Nenhuma aprovação de J3 é inferida deste gate.
