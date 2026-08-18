# NF-01 — Fase I — I3 — Substrato reutilizável do AppShell

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
I3_SHARED_APPSHELL_SUBSTRATE=APPROVED_BY_LEANDRO
I3_STATUS=COMPLETE
PHASE_I_DESIGN_LAB_APPSHELL=IN_PROGRESS
IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY
SCREEN_MIGRATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação consumida neste gate autoriza exclusivamente a materialização do substrato reutilizável do AppShell dentro de `docs/nf-01/prototype/**`. Não autoriza migração em massa de telas, alteração de produção, backend, NF-02, deploy ou merge.

## Objetivo executado

I3 transforma a baseline visual isolada de I1 em uma infraestrutura interna reutilizável do Design Lab:

```text
PAGE METADATA + PAGE CONTENT
              ↓
       app-shell.js
              ↓
┌──────────────────────────────┐
│ AppShell compartilhado       │
│ ├─ CollapsibleSidebar        │
│ ├─ TopHeader                 │
│ └─ MainWorkspace             │
│    └─ conteúdo preservado    │
└──────────────────────────────┘
```

A página deixa de possuir/copy-pastear a estrutura global do shell e passa a fornecer somente metadados de composição e conteúdo próprio.

## Arquivos materializados

```text
docs/nf-01/prototype/assets/app-shell.css
docs/nf-01/prototype/assets/app-shell.js
```

A referência canônica foi migrada:

```text
docs/nf-01/prototype/screens/01.01-app-shell.html
```

Documentação do laboratório reconciliada:

```text
docs/nf-01/prototype/README.md
```

Arquivos temporários de I1 removidos após a referência deixar de consumi-los:

```text
docs/nf-01/prototype/assets/app-shell-i1.css  => REMOVED
docs/nf-01/prototype/assets/app-shell-i1.js   => REMOVED
```

Referências históricas textuais em checkpoints anteriores permanecem válidas como registro do que I1 materializou; não são dependências de runtime.

## Contrato de consumo da página

A página consumidora fornece:

```text
<body
  data-app-shell-active="..."
  data-app-shell-context-title="..."
  data-app-shell-context-subtitle="..."
  ...>

  <main id="conteudo" data-app-shell-content>
    Breadcrumb
    PageHeader
    PageContent
  </main>
</body>
```

I3 não congela todos esses atributos como API de produção. Eles são a interface interna atual do Design Lab para provar reutilização e separação de responsabilidade.

## Contrato do substrato compartilhado

```text
CANONICAL_APPSHELL=ONE
NEUTRAL_SHARED_CSS=YES
NEUTRAL_SHARED_JS=YES
I1_CLASS_NAMES_AS_PERMANENT_API=NO

PAGE_OWNS_GLOBAL_SHELL=NO
PAGE_OWNS_PAGE_CONTENT=YES
COPY_SHELL_MARKUP_PER_SCREEN=NO
COPY_SHELL_BEHAVIOR_PER_SCREEN=NO

SHARED_SIDEBAR_STRUCTURE=YES
SHARED_TOPHEADER_STRUCTURE=YES
SHARED_RESPONSIVE_BEHAVIOR=YES
SHARED_FOCUS_MOBILE_BEHAVIOR=YES
```

## Montagem e preservação semântica

O bootstrap reaproveita o `main` existente da página:

```text
EXISTING_MAIN
      ↓
MOVE_INTO_SHARED_WORKSPACE
      ↓
SAME_MAIN_NODE_PRESERVED
```

Guardrails:

```text
SINGLE_MAIN=REQUIRED
SECOND_MAIN_CREATED_BY_BOOTSTRAP=NO
SKIP_LINK=SHARED
PAGE_CONTENT_PRESERVED=YES
SEMANTIC_ORDER_PRESERVED=YES
```

A montagem possui proteção contra duplicação:

```text
FIRST_MOUNT  => CREATE_SHELL
SECOND_MOUNT => NO_DUPLICATE_SHELL
```

O contrato futuro de teste é:

```text
NF01AppShell.mount()
NF01AppShell.mount()

EXPECTED:
APP_SHELL_COUNT=1
SIDEBAR_COUNT=1
TOPHEADER_COUNT=1
MAIN_COUNT=1
SKIP_LINK_COUNT=1
```

## Comportamento compartilhado preservado

### Desktop largo

```text
SIDEBAR_DEFAULT=EXPANDED
USER_CAN_TOGGLE_COMPACT=YES
COMPACT_PREFERENCE_LOCAL_NON_SENSITIVE=YES
RELEASED_WIDTH_RETURNS_TO_WORKSPACE=YES
```

### Faixa intermediária

```text
SIDEBAR=COMPACT
DEAD_GUTTER=NO
COMPACT_LABEL_ON_HOVER_OR_FOCUS=YES
```

### Mobile

```text
SIDEBAR=OVERLAY
MOBILE_MENU_BUTTON=YES
BACKDROP_CLOSE=YES
ESCAPE_CLOSE=YES
CLOSED_NAVIGATION=INERT
OPEN_NAVIGATION=>BACKGROUND_MAIN_REGION_INERT
FOCUS_ENTERS_NAVIGATION=YES
FOCUS_CONTAINED_WHILE_OVERLAY_OPEN=YES
FOCUS_RETURNS_TO_TRIGGER_ON_CLOSE=YES
BODY_SCROLL_LOCK_WHILE_OPEN=YES
```

### Acessibilidade e movimento

```text
SINGLE_MAIN=YES
SKIP_LINK=YES
ARIA_EXPANDED=YES
ICON_ONLY_CONTROL_ACCESSIBLE_NAME=YES
HIDDEN_MOBILE_NAV_NOT_IN_FOCUS_FLOW=YES
REDUCED_MOTION=SUPPORTED
STATE_NOT_COLOR_ONLY=INHERITED_CONTRACT
```

## Fronteira arquitetural

A composição JS existe porque o Design Lab é um protótipo estático.

```text
DESIGN_LAB_JS_COMPOSITION != PRODUCTION_ARCHITECTURE
```

I3 **não** decide:

```text
Flask base template
Jinja inheritance
Jinja include
Jinja macro
frontend framework
client-side router
production state library
```

Essas decisões pertencem à futura implementação, sob os contratos já congelados.

## Telas ainda não migradas

```text
DASHBOARD_RECONCILED_WITH_SHARED_APPSHELL=NO
EMPLOYEES_RECONCILED_WITH_SHARED_APPSHELL=NO
ONBOARDING_RECONCILED_WITH_SHARED_APPSHELL=NO
MASS_SCREEN_REWRITE=NO
BIG_BANG_MIGRATION=NO
```

A tela `01.01-app-shell.html` é a única referência convertida em I3 para provar o substrato antes da adoção incremental.

## `/punch`

```text
PUNCH_ROUTE => OUTSIDE_ADMIN_APPSHELL
SHARED_DESIGN_SYSTEM != SHARED_APPLICATION_SHELL
```

O item “Registrar ponto” no menu do protótipo continua apenas uma saída conceitual para uma jornada independente.

## Validação executada em I3

Foi executada validação estrutural/source-level da materialização final:

```text
SHARED_CSS_CREATED=PASS
SHARED_JS_CREATED=PASS
REFERENCE_HTML_USES_SHARED_ASSETS=PASS
REFERENCE_HTML_HAS_ONE_DECLARED_MAIN=PASS
PAGE_CONTENT_CONTRACT=PASS
SHARED_SHELL_MARKUP_REMOVED_FROM_REFERENCE_PAGE=PASS
I1_RUNTIME_ASSETS_REMOVED=PASS
README_RECONCILED=PASS
MOUNT_DUPLICATION_GUARD_PRESENT=PASS
DESKTOP_COMPACT_CONTRACT_PRESENT=PASS
INTERMEDIATE_COMPACT_CONTRACT_PRESENT=PASS
MOBILE_OVERLAY_CONTRACT_PRESENT=PASS
MOBILE_INERT_CONTRACT_PRESENT=PASS
MOBILE_FOCUS_CONTAINMENT_CONTRACT_PRESENT=PASS
ESCAPE_AND_BACKDROP_CONTRACT_PRESENT=PASS
REDUCED_MOTION_BRANCH_PRESENT=PASS
PUNCH_OUTSIDE_ADMIN_SHELL_CONTRACT=PASS
```

Não declarar como executados em I3:

```text
BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
DOUBLE_MOUNT_RUNTIME_BROWSER_TEST=NO
SCREEN_READER_MANUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
PRODUCTION_E2E=NO
```

A ausência desses testes não invalida a materialização do substrato; eles permanecem para os gates de validação posteriores e não devem receber false-green.

## Testes futuros derivados

### Unitários

- montagem idempotente;
- preferência compacta;
- `aria-expanded` e nome acessível do toggle;
- sidebar mobile fechada `inert`;
- foco entra/permanece/retorna no overlay;
- `Escape` e backdrop;
- reduced motion sem perda de informação.

### Integração

- página com `main` existente → AppShell → exatamente um `main`;
- dupla chamada de `mount()` → nenhuma duplicação;
- AppShell + Dashboard;
- AppShell + Funcionários;
- AppShell + onboarding;
- desktop → intermediário → mobile;
- navegação administrativa sem incorporar `/punch`.

## Invariantes preservadas

```text
app/**=UNCHANGED
templates/**=UNCHANGED
static/**=UNCHANGED
migrations/**=UNCHANGED
backend/routes=UNCHANGED
DECISOES_CONGELADAS.md=UNCHANGED
NF02=NOT_STARTED
Ponto_to_AttendanceEvent=NOT_EXECUTED
AI=NOT_IMPLEMENTED
OBSERVABILITY_BACKEND=NOT_IMPLEMENTED
DEPLOY=NO
PRODUCTION_HOMOLOGATION=NO
LEGAL_CONFORMITY_DECLARED=NO
FINAL_HUMAN_GATE=NOT_READY
PR_MERGE=NOT_AUTHORIZED
```

## Próxima decisão

I3 conclui o substrato compartilhado. A próxima decisão deve definir a primeira adoção incremental/reconciliação real do AppShell em uma superfície existente, sem assumir que Dashboard, Funcionários ou onboarding já estão reconciliados.

```text
NEXT_OFFICIAL_ITEM=I4_DEFINITION_GATE
```
