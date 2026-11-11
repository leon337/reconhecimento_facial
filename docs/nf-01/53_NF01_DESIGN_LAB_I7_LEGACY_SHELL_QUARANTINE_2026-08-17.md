# NF-01 — Fase I — I7 — Quarentena do AppShell legado

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
I7_LEGACY_SHELL_QUARANTINE=APPROVED_BY_LEANDRO
I7_STATUS=COMPLETE
PHASE_I_DESIGN_LAB_APPSHELL=IN_PROGRESS
IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY

HISTORICAL_V1=PRESERVED
CURRENT_SURFACES=UNCHANGED_CONTENT
PHASE_J=NOT_STARTED
PHASE_K=NOT_STARTED
PHASE_L=NOT_STARTED
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate autoriza exclusivamente separar a implementação histórica do shell V1 do substrato atual. Não autoriza redesign, produção, backend, NF-02, deploy ou merge.

## Problema encerrado

Antes de I7, `components.css` ainda continha a antiga implementação global de `.app-shell`, `.sidebar`, `.topbar`, navegação e controles de contexto/perfil, enquanto `app-shell.css` já era o proprietário do AppShell canônico atual.

Também `interactions.js` ainda continha o controlador histórico de `body.nav-open + .sidebar + [data-nav-toggle]`.

I7 elimina essa dupla propriedade.

## Arquitetura resultante

```text
CURRENT SURFACES
├── 02.01-dashboard.html
├── 03.01-funcionarios.html
└── 03.04-novo-funcionario-v2.html
        ↓
   app-shell.css
   app-shell.js

HISTORICAL V1
└── 03.03-novo-funcionario.html
        ↓
   legacy-shell.css
   legacy-shell.js
```

```text
CURRENT_APPSHELL_OWNER=app-shell.css+app-shell.js
CANONICAL_APPSHELL=ONE
GLOBAL_COMPONENTS_OWNS_LEGACY_SHELL=NO
GLOBAL_INTERACTIONS_OWNS_LEGACY_NAV=NO
LEGACY_SHELL_QUARANTINED=YES
HISTORICAL_V1_PRESERVED=YES
HISTORICAL_V1_MIGRATED=NO
ACTIVE_SURFACE_LEGACY_SHELL_DEPENDENCY=0
```

## Arquivos criados

```text
docs/nf-01/prototype/assets/legacy-shell.css
docs/nf-01/prototype/assets/legacy-shell.js
```

`legacy-shell.css` é escopado por `body[data-legacy-shell]`. `legacy-shell.js` só inicializa quando esse marcador existe.

## Arquivos alterados

```text
docs/nf-01/prototype/assets/components.css
docs/nf-01/prototype/assets/interactions.js
docs/nf-01/prototype/screens/03.03-novo-funcionario.html
```

### `components.css`

Permanece responsável por base visual, controles compartilhados, páginas, Dashboard/áreas históricas de conteúdo, catálogo e responsividade de conteúdo. Não contém mais a implementação estrutural do shell legado.

### `interactions.js`

Permanece com data demonstrativa, Toast e `data-demo-action`. O controlador de navegação legado foi removido.

### `03.03-novo-funcionario.html`

A referência V1 histórica foi preservada e agora declara:

```text
body[data-legacy-shell]
components.css
legacy-shell.css
new-employee-v1.css
legacy-shell.js
interactions.js
new-employee-v1.js
```

A antiga dependência de `dashboard-v3.css` também foi removida da V1, pois não pertence ao shell histórico nem ao conteúdo do formulário V1.

## Validação source-level executada

```text
COMPONENTS_GLOBAL_LEGACY_SHELL_REMOVED=PASS
SHARED_INTERACTIONS_LEGACY_NAV_REMOVED=PASS
LEGACY_CSS_SCOPED_TO_DATA_LEGACY_SHELL=PASS
LEGACY_JS_SCOPED_TO_DATA_LEGACY_SHELL=PASS
HISTORICAL_V1_IMPORTS_LEGACY_CSS=PASS
HISTORICAL_V1_IMPORTS_LEGACY_JS=PASS
HISTORICAL_V1_DATA_LEGACY_SHELL_MARKER=PASS
HISTORICAL_V1_DASHBOARD_CSS_DEPENDENCY_REMOVED=PASS

DASHBOARD_IMPORTS_APP_SHELL_CSS=PASS
EMPLOYEES_IMPORTS_APP_SHELL_CSS=PASS
ONBOARDING_V2_IMPORTS_APP_SHELL_CSS=PASS
ACTIVE_SURFACE_IMPORTS_LEGACY_SHELL=NO
```

Não foram declarados executados em I7:

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

Sem `false-green`: a validação deste gate é estrutural/source-level.

## Testes futuros derivados

### Unitários

```text
legacy-shell.js sem body[data-legacy-shell] => no-op
legacy-shell.js com V1 => controla apenas navegação V1
app-shell mount duplicado => one shell
shared interactions => não controla navegação
```

### Integração

```text
Dashboard + Employees + Onboarding V2
→ app-shell only

Historical V1
→ legacy-shell only

EXPECTED:
CURRENT_X_LEGACY_CROSS_DEPENDENCY=0
```

## Próxima fronteira

```text
NEXT_OFFICIAL_ITEM=I8_DEFINITION_GATE
```

I8 deve ser definido a partir do estado real pós-I7. Nenhuma aprovação de I8 é inferida deste gate.
