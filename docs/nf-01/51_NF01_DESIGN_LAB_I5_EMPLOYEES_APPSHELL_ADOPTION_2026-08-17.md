# NF-01 — Fase I — I5 — Adoção incremental do AppShell em Funcionários

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
I5_EMPLOYEES_SHARED_APPSHELL_ADOPTION=APPROVED_BY_LEANDRO
I5_STATUS=COMPLETE
PHASE_I_DESIGN_LAB_APPSHELL=IN_PROGRESS
IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY
EMPLOYEES_CONTENT_REDESIGN=NO
PHASE_K_EMPLOYEES_RECONCILIATION=NOT_STARTED
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação consumida neste gate autoriza exclusivamente a adoção estrutural do substrato compartilhado do AppShell pela tela Funcionários do Design Lab. Não autoriza redesign do conteúdo, Fase K, alteração de produção, backend, NF-02, deploy ou merge.

## Objetivo executado

I5 tornou `screens/03.01-funcionarios.html` o segundo consumidor incremental real do substrato criado em I3:

```text
Employees Content V1
        ↓
<main data-app-shell-content>
        ↓
app-shell.js + app-shell.css
        ↓
CollapsibleSidebar + TopHeader + MainWorkspace
```

A mudança foi de casco estrutural, não de conteúdo.

## Arquivos alterados

```text
docs/nf-01/prototype/screens/03.01-funcionarios.html
docs/nf-01/prototype/assets/employees-v1.css
docs/nf-01/prototype/README.md
docs/nf-01/prototype/index.html
```

Substrato compartilhado consumido, sem fork local:

```text
docs/nf-01/prototype/assets/app-shell.css
docs/nf-01/prototype/assets/app-shell.js
```

`employees-v1.js` foi preservado sem mudança funcional.

## Shell legado removido da tela Funcionários

Foram removidos de `03.01-funcionarios.html`:

```text
skip link próprio
Sidebar própria
navegação própria
TopHeader próprio
mobile-menu markup próprio
wrappers locais do shell legado
```

A tela agora fornece:

```text
BODY METADATA
+
MAIN / EMPLOYEES CONTENT
```

O AppShell compartilhado fornece:

```text
SKIP LINK
SIDEBAR
TOPHEADER
MAIN WORKSPACE WRAPPER
ACTIVE NAV=employees
DESKTOP COMPACT
MOBILE OVERLAY
INERT
ESCAPE
FOCUS
REDUCED MOTION
```

## Conteúdo preservado

I5 não iniciou a reconciliação visual/semântica da Fase K. Permaneceram:

```text
Breadcrumb
PageHeader
Novo funcionário CTA demonstrativo
aviso de dados demonstrativos
summary cards
Search
filtro de biometria
filtro de função
limpar filtros
DataTable demonstrativa
Pagination demonstrativa
EmptyState
employees-v1.js
Toast/interações demonstrativas
```

```text
EMPLOYEES_CONTENT_REDESIGN_IN_I5=NO
PHASE_K_EMPLOYEES_RECONCILIATION=NOT_STARTED
```

## CSS

`employees-v1.css` deixou de conter refinamentos de Sidebar/TopHeader/menu do shell legado e ficou restrito ao conteúdo específico de Funcionários.

```text
EMPLOYEES_LOCAL_SHELL_CSS=REMOVED
EMPLOYEES_CONTENT_CSS=PRESERVED
```

`components.css` ainda mantém estilos históricos de shell porque onboarding e referências históricas ainda não foram migrados. I5 não executa limpeza global antecipada.

```text
GLOBAL_LEGACY_SHELL_CSS_REMOVAL_IN_I5=NO
```

## JavaScript

`employees-v1.js` continua responsável somente pela demonstração local de busca, filtros, contagem visível e EmptyState.

`interactions.js` foi preservado para Toast/interações demonstrativas e compatibilidade histórica. O controlador legado de navegação não encontra na tela migrada `[data-nav-toggle]` nem `.sidebar`, portanto não assume o shell da tela.

```text
EMPLOYEES_SHARED_SHELL_CONTROLLER=app-shell.js
EMPLOYEES_FILTER_CONTROLLER=employees-v1.js
EMPLOYEES_OLD_NAV_CONTROLLER_EFFECTIVE=NO
GLOBAL_INTERACTIONS_CLEANUP_IN_I5=NO
```

## Contrato I5 congelado

```text
I5_TARGET=docs/nf-01/prototype/screens/03.01-funcionarios.html
CANONICAL_APPSHELL=ONE
EMPLOYEES_SHARED_APPSHELL=YES
ACTIVE_NAV=employees
COPY_SHELL_PER_SCREEN=NO

ONE_DECLARED_MAIN=YES
LOCAL_SIDEBAR_MARKUP=NO
LOCAL_TOPHEADER_MARKUP=NO
SHARED_APP_SHELL_CSS=YES
SHARED_APP_SHELL_JS=YES

EMPLOYEES_CONTENT_PRESERVED=YES
EMPLOYEES_CONTENT_REDESIGN=NO
PHASE_K=NOT_STARTED

DASHBOARD_SHARED_APPSHELL=YES
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
EMPLOYEES_IMPORTS_SHARED_APP_SHELL_CSS=PASS
EMPLOYEES_IMPORTS_SHARED_APP_SHELL_JS=PASS
EMPLOYEES_ACTIVE_NAV_METADATA=PASS
EMPLOYEES_HAS_ONE_DECLARED_MAIN=PASS
EMPLOYEES_MAIN_HAS_CONSUMER_MARKER=PASS
EMPLOYEES_LOCAL_SIDEBAR_MARKUP_REMOVED=PASS
EMPLOYEES_LOCAL_TOPHEADER_MARKUP_REMOVED=PASS
EMPLOYEES_CONTENT_BLOCKS_PRESERVED=PASS
EMPLOYEES_V1_SHELL_RULES_REMOVED=PASS
EMPLOYEES_FILTER_SCRIPT_PRESERVED=PASS
```

Não foram declarados executados em I5:

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

Sem `false-green`: I5 prova adoção estrutural/source-level e reutilização do mesmo AppShell em duas telas; acceptance visual e integração completa permanecem para gates posteriores.

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
filters preserved independently of shell
```

### Integração

```text
Shared AppShell
├── Dashboard Content
└── Employees Content

EXPECTED PER CONSUMER:
APP_SHELL_COUNT=1
SIDEBAR_COUNT=1
TOPHEADER_COUNT=1
MAIN_COUNT=1
SKIP_LINK_COUNT=1
LOCAL_LEGACY_SHELL_COUNT=0
```

Também testar que a mesma preferência de shell, comportamento mobile, foco, Escape e `inert` são consistentes nos dois consumidores, sem misturar o estado específico do conteúdo de cada página.

## Próxima fronteira

```text
NEXT_OFFICIAL_ITEM=I6_DEFINITION_GATE
```

I6 deve ser definido a partir do estado real pós-I5. Nenhuma aprovação de I6 é inferida deste gate.
