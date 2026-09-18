# NF-01 — Fase I — I4 — Adoção incremental do AppShell no Dashboard

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
I4_DASHBOARD_SHARED_APPSHELL_ADOPTION=APPROVED_BY_LEANDRO
I4_STATUS=COMPLETE
PHASE_I_DESIGN_LAB_APPSHELL=IN_PROGRESS
IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY
DASHBOARD_CONTENT_REDESIGN=NO
PHASE_J_DASHBOARD_RECONCILIATION=NOT_STARTED
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação consumida neste gate autoriza exclusivamente a adoção estrutural do substrato compartilhado do AppShell pelo Dashboard do Design Lab. Não autoriza redesenho do conteúdo do Dashboard, Fase J, alteração de produção, backend, NF-02, deploy ou merge.

## Objetivo executado

I4 tornou `screens/02.01-dashboard.html` o primeiro consumidor incremental real do substrato criado em I3:

```text
Dashboard Content V3
        ↓
<main data-app-shell-content>
        ↓
app-shell.js + app-shell.css
        ↓
CollapsibleSidebar + TopHeader + MainWorkspace
```

A troca foi de **casco estrutural**, não de conteúdo.

## Arquivos alterados

```text
docs/nf-01/prototype/screens/02.01-dashboard.html
docs/nf-01/prototype/assets/dashboard-v3.css
docs/nf-01/prototype/README.md
docs/nf-01/prototype/index.html
```

Substrato compartilhado consumido, sem fork local:

```text
docs/nf-01/prototype/assets/app-shell.css
docs/nf-01/prototype/assets/app-shell.js
```

## Shell legado removido da tela Dashboard

Foram removidos de `02.01-dashboard.html`:

```text
skip link próprio do Dashboard
Sidebar própria
navegação própria
TopHeader próprio
mobile-menu controller próprio por markup
wrappers locais do shell legado
```

O Dashboard agora fornece:

```text
BODY METADATA
+
MAIN / DASHBOARD CONTENT
```

O AppShell fornece:

```text
SKIP LINK
SIDEBAR
TOPHEADER
MAIN WORKSPACE WRAPPER
ACTIVE NAV
DESKTOP COMPACT
MOBILE OVERLAY
INERT
ESCAPE
FOCUS
REDUCED MOTION
```

## Conteúdo preservado

I4 não iniciou a reconciliação visual/semântica da Fase J. Permaneceram no Dashboard V3:

```text
PageHeader
Data demonstrativa
KPI cards
Atividade recente
Atenção necessária
Atalhos
Data demonstrativa dinâmica
Toast demonstrativo
```

```text
DASHBOARD_CONTENT_REDESIGN_IN_I4=NO
PHASE_J_DASHBOARD_RECONCILIATION=NOT_STARTED
```

## CSS

`dashboard-v3.css` deixou de conter refinamentos de Sidebar/TopHeader/menu do shell legado e ficou restrito ao conteúdo específico do Dashboard.

```text
DASHBOARD_LOCAL_SHELL_CSS=REMOVED
DASHBOARD_CONTENT_CSS=PRESERVED
```

`components.css` ainda contém estilos históricos de shell porque Funcionários e onboarding ainda não foram migrados. I4 não executa limpeza global antecipada.

```text
GLOBAL_LEGACY_SHELL_CSS_REMOVAL=NO
```

## JavaScript

`interactions.js` foi preservado porque continua responsável por data e Toast demonstrativos e pode ser usado por telas históricas.

O controlador de navegação legado desse arquivo não encontra no Dashboard migrado os seletores `[data-nav-toggle]` e `.sidebar`, portanto não assume o shell da tela.

```text
DASHBOARD_SHARED_SHELL_CONTROLLER=app-shell.js
DASHBOARD_OLD_NAV_CONTROLLER_EFFECTIVE=NO
GLOBAL_INTERACTIONS_CLEANUP=NO
```

## Contrato I4 congelado

```text
I4_TARGET=docs/nf-01/prototype/screens/02.01-dashboard.html
CANONICAL_APPSHELL=ONE
DASHBOARD_SHARED_APPSHELL=YES
ACTIVE_NAV=dashboard
COPY_SHELL_PER_SCREEN=NO

ONE_DECLARED_MAIN=YES
LOCAL_SIDEBAR_MARKUP=NO
LOCAL_TOPHEADER_MARKUP=NO
SHARED_APP_SHELL_CSS=YES
SHARED_APP_SHELL_JS=YES

DASHBOARD_CONTENT_PRESERVED=YES
DASHBOARD_CONTENT_REDESIGN=NO
PHASE_J=NOT_STARTED

EMPLOYEES_SHARED_APPSHELL=NO
ONBOARDING_SHARED_APPSHELL=NO
PUNCH_ROUTE_OUTSIDE_ADMIN_APPSHELL=YES

app/**=UNCHANGED
templates/**=UNCHANGED
static/**=UNCHANGED
migrations/**=UNCHANGED
backend=UNCHANGED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

## Validação executada

Validação source-level executada após a materialização:

```text
DASHBOARD_IMPORTS_SHARED_APP_SHELL_CSS=PASS
DASHBOARD_IMPORTS_SHARED_APP_SHELL_JS=PASS
DASHBOARD_ACTIVE_NAV_METADATA=PASS
DASHBOARD_HAS_ONE_DECLARED_MAIN=PASS
DASHBOARD_MAIN_HAS_CONSUMER_MARKER=PASS
DASHBOARD_LOCAL_SIDEBAR_MARKUP_REMOVED=PASS
DASHBOARD_LOCAL_TOPHEADER_MARKUP_REMOVED=PASS
DASHBOARD_CONTENT_BLOCKS_PRESERVED=PASS
DASHBOARD_V3_SHELL_RULES_REMOVED=PASS
DASHBOARD_CONTENT_RULES_PRESERVED=PASS
```

Não foram declarados executados em I4:

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

Sem `false-green`: I4 prova adoção estrutural/source-level; acceptance visual e integração completa permanecem para gates posteriores.

## Testes futuros derivados

### Unitários

```text
active nav = dashboard
mount duplicado => one shell
compact preference preserved
mobile open/close
aria-expanded
inert
focus/escape
```

### Integração

```text
Dashboard Content
       ↓
Shared AppShell
       ↓
EXPECTED:
APP_SHELL_COUNT=1
SIDEBAR_COUNT=1
TOPHEADER_COUNT=1
MAIN_COUNT=1
SKIP_LINK_COUNT=1
DASHBOARD_CONTENT_BLOCKS=PRESERVED
LEGACY_DASHBOARD_SHELL_COUNT=0
```

## Próxima fronteira

```text
NEXT_OFFICIAL_ITEM=I5_DEFINITION_GATE
```

I5 deve ser definido a partir do estado real pós-I4. Nenhuma aprovação de I5 é inferida deste gate.
