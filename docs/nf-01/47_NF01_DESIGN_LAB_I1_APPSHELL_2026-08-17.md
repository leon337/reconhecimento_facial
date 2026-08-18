# NF-01 — Fase I — I1 — AppShell no Design Lab

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
I1_DESIGN_LAB_APPSHELL=APPROVED_BY_LEANDRO
I1_STATUS=COMPLETE
PHASE_I_DESIGN_LAB_APPSHELL=IN_PROGRESS
IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação autoriza e este checkpoint registra exclusivamente a materialização do AppShell no laboratório isolado `docs/nf-01/prototype/**`. Não autoriza alteração de produção, backend, NF-02, deploy ou merge.

## Objetivo executado

Materializar uma referência canônica isolada para:

```text
CollapsibleSidebar
+
TopHeader
+
MainWorkspace
+
Breadcrumb
+
PageHeader
+
landmarks / skip link
+
comportamento desktop / intermediário / mobile
```

A referência não redesenha ainda Dashboard, Funcionários ou Novo Funcionário. Essas telas históricas permanecem preservadas para reconciliação posterior.

## Arquivos materializados

```text
docs/nf-01/prototype/screens/01.01-app-shell.html
docs/nf-01/prototype/assets/app-shell-i1.css
docs/nf-01/prototype/assets/app-shell-i1.js
```

Arquivos de navegação/documentação do laboratório reconciliados:

```text
docs/nf-01/prototype/index.html
docs/nf-01/prototype/README.md
```

## Contrato materializado

### Desktop largo

```text
SIDEBAR_DEFAULT=EXPANDED
SIDEBAR_EXPANDED≈248px token existente
SIDEBAR_COMPACT≈72px token existente
USER_CAN_TOGGLE_COMPACT=YES
COMPACT_PREFERENCE_LOCAL_NON_SENSITIVE=YES
RELEASED_WIDTH_RETURNS_TO_WORKSPACE=YES
```

A preferência de compactação usa armazenamento local apenas como preferência visual não sensível. Nenhuma informação pessoal, de RBAC, tenant, biometria ou domínio é persistida pelo AppShell.

### Faixa intermediária

```text
SIDEBAR=COMPACT
DEAD_GUTTER=NO
NAVIGATION_ACCESSIBLE_NAME=PRESERVED
COMPACT_TOOLTIP_ON_HOVER_AND_FOCUS=YES
```

### Mobile

```text
SIDEBAR=OVERLAY
MOBILE_MENU_BUTTON=YES
BACKDROP_CLOSE=YES
ESCAPE_CLOSE=YES
CLOSED_NAVIGATION=INERT
OPEN_NAVIGATION=>BACKGROUND_MAIN_INERT
FOCUS_ENTERS_NAVIGATION=YES
FOCUS_RETURNS_TO_TRIGGER_ON_CLOSE=YES
BODY_SCROLL_LOCK_WHILE_OPEN=YES
```

### Estrutura semântica e acessibilidade

```text
SKIP_LINK=YES
SINGLE_MAIN=YES
NAV_LANDMARK=YES
VISIBLE_FOCUS=INHERITED_FROM_DESIGN_SYSTEM
ICON_ONLY_CONTROLS_HAVE_ACCESSIBLE_NAMES=YES
ARIA_EXPANDED_FOR_NAV_CONTROLS=YES
HIDDEN_MOBILE_NAV_NOT_IN_FOCUS_FLOW=YES
REDUCED_MOTION=SUPPORTED
SEMANTIC_ORDER_PRESERVED=YES
```

### Contexto e jornadas

```text
TOPHEADER_APP_CONTEXT=DEMONSTRATIVE_ONLY
APP_CONTEXT != EMPRESA_DO_VINCULO
PUNCH_ROUTE => OUTSIDE_ADMIN_APPSHELL
SHARED_DESIGN_SYSTEM != SHARED_APPLICATION_SHELL
```

`Registrar ponto` aparece somente como saída conceitual para uma jornada independente; I1 não envolve o fluxo `/punch` dentro do shell administrativo.

## Responsividade materializada

A baseline usa três comportamentos, sem transformar os valores em taxonomia de dispositivo:

```text
>=70rem................ sidebar expandida/recolhível
48rem–69.99rem......... sidebar compacta
<48rem.................. overlay mobile
```

Os valores são decisões da referência visual I1 e continuam subordinados ao princípio H7:

```text
COMPONENT_SPACE != DEVICE_NAME
RESPONSIVE != SHRINK_DESKTOP
```

A validação ampla 360/768/1024/1440+, intermediários, zoom 200%, screen reader e contraste permanece no acceptance gate posterior da NF-01.

## Validação executada em I1

Foi executada validação estrutural/source-level dos artefatos materializados:

```text
REFERENCE_HTML_CREATED=PASS
SHARED_I1_CSS_CREATED=PASS
SHARED_I1_JS_CREATED=PASS
SINGLE_MAIN_CONTRACT=PASS
SKIP_LINK_CONTRACT=PASS
DESKTOP_COLLAPSE_CONTRACT=PASS
COMPACT_PREFERENCE_CONTRACT=PASS
INTERMEDIATE_COMPACT_CONTRACT=PASS
MOBILE_OVERLAY_CONTRACT=PASS
MOBILE_INERT_CONTRACT=PASS
ESCAPE_AND_BACKDROP_CONTRACT=PASS
FOCUS_RETURN_CONTRACT=PASS
REDUCED_MOTION_BRANCH=PASS
PUNCH_OUTSIDE_ADMIN_SHELL_CONTRACT=PASS
PROTOTYPE_INDEX_UPDATED=PASS
PROTOTYPE_README_UPDATED=PASS
```

Não declarar como executados neste ponto:

```text
BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
SCREEN_READER_MANUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
PRODUCTION_E2E=NO
```

Esses itens pertencem às etapas posteriores de validação e não são false-green de I1.

## Testes futuros derivados

### Unitários

- persistência e restauração da preferência compacta;
- transição expanded/compact sem reservar largura morta;
- `aria-expanded` e accessible name do toggle;
- sidebar mobile fechada `inert`;
- abertura/fechamento mobile e retorno de foco;
- reduced motion sem perda de informação.

### Integração

- AppShell + Dashboard;
- AppShell + Funcionários;
- AppShell + onboarding;
- troca de viewport desktop → intermediário → mobile;
- overlay mobile + teclado + Escape + backdrop;
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

I1 fecha a baseline estrutural inicial do AppShell. O próximo item da Fase I deve ser definido a partir da auditoria da baseline materializada, sem assumir por inferência que Dashboard, Funcionários ou onboarding já foram reconciliados.

```text
NEXT_OFFICIAL_ITEM=I2_DEFINITION_GATE
```
