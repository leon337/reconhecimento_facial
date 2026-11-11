# NF-01 — Fase I — I6 — Adoção incremental do AppShell no Novo Funcionário V2

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
I6_ONBOARDING_V2_SHARED_APPSHELL_ADOPTION=APPROVED_BY_LEANDRO
I6_STATUS=COMPLETE
PHASE_I_DESIGN_LAB_APPSHELL=IN_PROGRESS
IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY
ONBOARDING_CONTENT_REDESIGN=NO
PHASE_L_ONBOARDING_RECONCILIATION=NOT_STARTED
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate autoriza exclusivamente a troca do casco administrativo do Novo Funcionário V2 pelo AppShell compartilhado do Design Lab. Não autoriza a reconciliação visual/semântica da Fase L, alteração de produção, backend, NF-02, deploy ou merge.

## Objetivo executado

`screens/03.04-novo-funcionario-v2.html` tornou-se o terceiro consumidor real do substrato compartilhado criado em I3:

```text
Onboarding V2 Content
        ↓
<main data-app-shell-content>
        ↓
app-shell.js + app-shell.css
        ↓
CollapsibleSidebar + TopHeader + MainWorkspace
```

A mudança foi de casco estrutural; o wizard V2 continua preservado como conteúdo histórico ainda sujeito à Fase L.

## Contrato congelado

```text
I6_TARGET=docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
CANONICAL_APPSHELL=ONE
ONBOARDING_SHARED_APPSHELL=YES
ACTIVE_NAV=employees
ONBOARDING_IS_SUBFLOW_OF_EMPLOYEES=YES

LOCAL_ADMIN_SIDEBAR_MARKUP=NO
LOCAL_ADMIN_TOPHEADER_MARKUP=NO
SHARED_APP_SHELL_CSS=YES
SHARED_APP_SHELL_JS=YES
DASHBOARD_V3_CSS_DEPENDENCY=REMOVED
ONE_DECLARED_MAIN=YES
MAIN_HAS_CONSUMER_MARKER=YES

WIZARD_V2_CONTENT_PRESERVED=YES
WIZARD_8_STEPS_PRESERVED=YES
DRAFT_DEMO_PRESERVED=YES
VALIDATION_DEMO_PRESERVED=YES
NEW_EMPLOYEE_V2_JS_PRESERVED=YES

VERTICAL_WIZARD_RAIL_REMOVED_IN_I6=NO
HORIZONTAL_STEPPER_IMPLEMENTED_IN_I6=NO
CONTEXT_DRAWER_IMPLEMENTED_IN_I6=NO
STICKY_ACTIONS_REDESIGNED_IN_I6=NO
PHASE_L=NOT_STARTED

DASHBOARD_SHARED_APPSHELL=YES
EMPLOYEES_SHARED_APPSHELL=YES
ONBOARDING_SHARED_APPSHELL=YES
PUNCH_ROUTE_OUTSIDE_ADMIN_APPSHELL=YES

app/**=UNCHANGED
templates/**=UNCHANGED
static/**=UNCHANGED
migrations/**=UNCHANGED
backend=UNCHANGED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

## Validação source-level executada

```text
ONBOARDING_IMPORTS_SHARED_APP_SHELL_CSS=PASS
ONBOARDING_IMPORTS_SHARED_APP_SHELL_JS=PASS
ONBOARDING_ACTIVE_NAV_METADATA=PASS
ONBOARDING_HAS_ONE_DECLARED_MAIN=PASS
ONBOARDING_MAIN_HAS_CONSUMER_MARKER=PASS
ONBOARDING_LOCAL_SIDEBAR_MARKUP_REMOVED=PASS
ONBOARDING_LOCAL_TOPHEADER_MARKUP_REMOVED=PASS
DASHBOARD_V3_CSS_DEPENDENCY_REMOVED=PASS
ONBOARDING_WIZARD_CONTENT_PRESERVED=PASS
ONBOARDING_V2_SCRIPT_PRESERVED=PASS
```

Não foram declarados executados em I6:

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

Sem `false-green`: I6 prova adoção estrutural/source-level. A reconciliação do wizard com `HorizontalStepper`, `ContextDrawer`, `StickyFormActions` e demais decisões congeladas pertence à Fase L.

## Linha de montagem

```text
AppShell compartilhado
├── Dashboard........ COMPLETE_I4
├── Funcionários..... COMPLETE_I5
└── Onboarding V2.... COMPLETE_I6
```

## Testes futuros derivados

### Unitários

```text
active nav = employees
mount duplicado => one shell
compact preference preserved
mobile open/close
aria-expanded
inert
focus/escape
```

### Integração

```text
AppShell
├── Dashboard content
├── Employees content
└── Onboarding V2 content

EXPECTED:
ONE_SHELL_PER_PAGE
ONE_SIDEBAR_PER_PAGE
ONE_TOPHEADER_PER_PAGE
ONE_MAIN_PER_PAGE
CONTENT_STATE_INDEPENDENT
```

## Próxima fronteira

```text
NEXT_OFFICIAL_ITEM=I7_DEFINITION_GATE
```

I7 deve ser definido a partir do estado real pós-I6. Nenhuma aprovação de I7 é inferida deste gate.
