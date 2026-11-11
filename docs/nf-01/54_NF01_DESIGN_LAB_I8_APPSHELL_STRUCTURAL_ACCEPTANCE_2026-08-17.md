# NF-01 — Fase I — I8 — Aceite estrutural do AppShell

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
I8_APPSHELL_STRUCTURAL_ACCEPTANCE=APPROVED_BY_LEANDRO
I8_STATUS=COMPLETE
I8_ACCEPTANCE=PASS_SOURCE_LEVEL_WITH_HARDENING
PHASE_I_DESIGN_LAB_APPSHELL=IN_PROGRESS
IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY

VISUAL_REDESIGN=NO
PHASE_J=NOT_STARTED
PHASE_K=NOT_STARTED
PHASE_L=NOT_STARTED
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate autoriza exclusivamente auditoria source-level e hardening estrutural do AppShell do Design Lab. Não autoriza redesign de conteúdo, produção, backend, NF-02, deploy ou merge.

## Escopo auditado

```text
docs/nf-01/prototype/assets/app-shell.css
docs/nf-01/prototype/assets/app-shell.js
docs/nf-01/prototype/screens/01.01-app-shell.html
docs/nf-01/prototype/screens/02.01-dashboard.html
docs/nf-01/prototype/screens/03.01-funcionarios.html
docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
docs/nf-01/prototype/screens/03.03-novo-funcionario.html  # histórico/quarentena
```

## Achados de hardening

### I8-F1 — contrato de um único `main`

Antes de I8, o bootstrap usava `querySelector('[data-app-shell-content]')`: múltiplos candidatos poderiam existir sem rejeição explícita.

I8 endureceu o contrato:

```text
EXACTLY_ONE_[data-app-shell-content]=REQUIRED
CONTENT_ELEMENT_MUST_BE_MAIN=REQUIRED
DUPLICATE_OR_INVALID_CONTENT_MARKER=>MOUNT_ABORTED
```

Um root canônico pré-existente antes de uma montagem válida agora também aborta com warning, em vez de marcar silenciosamente o body como montado.

### I8-F2 — foco no overlay mobile

Antes de I8, a abertura mobile procurava o primeiro `a` ou `button`, podendo selecionar o botão de collapse que fica `display:none` no breakpoint mobile. Além disso, o gatilho de retorno era capturado depois da aplicação de `inert` ao `mainRegion`.

I8 endureceu o fluxo:

```text
MOBILE_TRIGGER_CAPTURE=BEFORE_MAIN_REGION_INERT
SIDEBAR_FOCUSABLES=VISIBLE_AND_OPERABLE_ONLY
HIDDEN_COLLAPSE_BUTTON=EXCLUDED_FROM_MOBILE_FOCUS_SET
OPEN=>FOCUS_FIRST_VISIBLE_SIDEBAR_CONTROL
CLOSE=>RESTORE_FOCUS_TO_TRIGGER_WHEN_REQUESTED
FOCUS_TRAP=>USES_SAME_VISIBLE_FOCUSABLE_SET
```

## Contrato source-level verificado

```text
CANONICAL_APPSHELL=ONE
APPSHELL_VERSION=i8

EXACTLY_ONE_CONTENT_MAIN_REQUIRED=YES
MOUNT_TWICE_DUPLICATES_SHELL=NO_BY_GUARD
PREEXISTING_CANONICAL_ROOT_CONFLICT=ABORT

SHELL_MARKUP_DECLARED_ROOT_COUNT=1
SHELL_MARKUP_DECLARED_SIDEBAR_COUNT=1
SHELL_MARKUP_DECLARED_TOPHEADER_COUNT=1
SHELL_MARKUP_DECLARED_SKIP_LINK_COUNT=1
PAGE_MAIN_PRESERVED_BY_MOVE=YES

ACTIVE_NAV_FROM_PAGE_METADATA=YES
CROSS_PAGE_COMPACT_PREFERENCE_STORAGE_KEY=SHARED

DESKTOP_WIDE_QUERY=min-width:70rem
INTERMEDIATE_QUERY=48rem..69.99rem
MOBILE_QUERY=max-width:47.99rem

DESKTOP_EXPANDED_COMPACT=DEFINED
INTERMEDIATE_COMPACT=DEFINED
MOBILE_OVERLAY=DEFINED
MOBILE_BACKGROUND_INERT=DEFINED
MOBILE_SIDEBAR_INERT_WHEN_CLOSED=DEFINED
ESCAPE_CLOSE=DEFINED
BACKDROP_CLOSE=DEFINED
FOCUS_ENTRY_HARDENED=YES
FOCUS_TRAP_HARDENED=YES
FOCUS_RETURN_HARDENED=YES
REDUCED_MOTION_BRANCH=DEFINED

DASHBOARD_SHARED_APPSHELL=YES
EMPLOYEES_SHARED_APPSHELL=YES
ONBOARDING_SHARED_APPSHELL=YES
ACTIVE_SURFACE_LEGACY_SHELL_DEPENDENCY=0
HISTORICAL_V1_LEGACY_SHELL_ISOLATED=YES

PUNCH_ADMIN_APPSHELL_PAGE=NO
PUNCH_NAV_ITEM_MARKED_INDEPENDENT=YES
HEADER_CONTEXT_MUTATES_FORM=NO_SOURCE_HANDLER
DESIGN_LAB_JS_FREEZES_FLASK_ARCHITECTURE=NO
```

## Evidência de consumidores

```text
02.01-dashboard.html
→ app-shell.css
→ one <main data-app-shell-content>
→ data-app-shell-active=dashboard
→ app-shell.js

03.01-funcionarios.html
→ app-shell.css
→ one <main data-app-shell-content>
→ data-app-shell-active=employees
→ app-shell.js

03.04-novo-funcionario-v2.html
→ app-shell.css
→ one <main data-app-shell-content>
→ data-app-shell-active=employees
→ app-shell.js

03.03-novo-funcionario.html
→ body[data-legacy-shell]
→ legacy-shell.css/js
→ historical only
```

## Limite da aceitação

I8 é deliberadamente **source-level**. O seguinte continua não executado:

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
PASS_SOURCE_LEVEL != VISUAL_HOMOLOGATION
PASS_SOURCE_LEVEL != AUTOMATED_TEST_PASS
PASS_SOURCE_LEVEL != PRODUCTION_READY
```

## Testes derivados para fases posteriores

### Unitários

```text
0 ou 2 content markers => mount aborts
non-main content marker => mount aborts
mount repetido => one shell
stored compact preference => restored on desktop wide
mobile focus set => excludes display:none controls
Escape/backdrop => closes overlay
close => focus returns to opener
```

### Integração

```text
Dashboard → Funcionários
→ same AppShell behavior
→ compact preference preserved

Funcionários → Novo Funcionário V2
→ same AppShell behavior
→ onboarding state independent

Historical V1
→ legacy shell only
→ no current/legacy cross-dependency
```

## Próxima fronteira

```text
NEXT_OFFICIAL_ITEM=I9_PHASE_I_CLOSEOUT_GATE
```

I9 deve reconciliar I1–I8 e decidir formalmente se a Fase I pode ser encerrada. Nenhuma aprovação de I9 é inferida deste gate.
