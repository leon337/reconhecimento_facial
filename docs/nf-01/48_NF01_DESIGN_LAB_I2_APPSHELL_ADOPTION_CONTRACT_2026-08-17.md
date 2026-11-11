# NF-01 — Fase I — I2 — Contrato de adoção do AppShell

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
I2_APPSHELL_ADOPTION_CONTRACT=APPROVED_BY_LEANDRO
I2_STATUS=COMPLETE
PHASE_I_DESIGN_LAB_APPSHELL=IN_PROGRESS
IMPLEMENTATION_SCOPE=DOCUMENTAL_CONTRACT_ONLY
SCREEN_RECONCILIATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação consumida neste gate autoriza exclusivamente a definição do contrato de adoção/reuso do AppShell da NF-01. Não autoriza migração das telas, alteração de produção, backend, NF-02, deploy ou merge.

## Problema arquitetural identificado após I1

I1 materializou a baseline isolada do AppShell em:

```text
docs/nf-01/prototype/screens/01.01-app-shell.html
docs/nf-01/prototype/assets/app-shell-i1.css
docs/nf-01/prototype/assets/app-shell-i1.js
```

Ao mesmo tempo, telas históricas do laboratório ainda utilizam uma estrutura anterior de shell baseada em `components.css` e classes como `.app-shell`, `.sidebar` e `.topbar`.

Isso é aceitável como estado transitório de comparação, porém não como arquitetura permanente.

```text
I1_REFERENCE
+
LEGACY_SCREEN_SHELLS
        ↓
TEMPORARY_COEXISTENCE
        ↓
MUST_CONVERGE_BEFORE_SCREEN_RECONCILIATION
```

## Decisão canônica de I2

Existe **um único AppShell administrativo canônico** como contrato de produto:

```text
AppShell
├─ CollapsibleSidebar
├─ TopHeader
└─ MainWorkspace
   ├─ Breadcrumb
   ├─ PageHeader
   └─ PageContent
```

O conteúdo de cada página é consumidor do shell; não é proprietário de uma implementação própria do shell.

```text
PAGE_CONTENT != SHELL_IMPLEMENTATION
```

## Contrato de adoção

```text
CANONICAL_APPSHELL=ONE
I1_REFERENCE=PRESERVED
LEGACY_APP_SHELL=SUPERSEDED_FOR_NEW_WORK
LEGACY_SCREEN_CONTENT=PRESERVED_FOR_RECONCILIATION

SHARED_APPSHELL_STRUCTURE=REQUIRED
SHARED_APPSHELL_BEHAVIOR=REQUIRED
COPY_PASTE_SHELL_PER_SCREEN=PROHIBITED
SCREEN_LOCAL_SHELL_FORK=PROHIBITED_FOR_NEW_WORK
```

I2 não exige apagar imediatamente o shell histórico das telas existentes. Ele o classifica como material transitório a ser substituído quando cada superfície entrar em sua etapa oficial de reconciliação.

## Interface conceitual neutra

I2 congela a interface conceitual, não uma biblioteca, framework ou template engine:

```text
AppShell
├─ SidebarRegion
├─ HeaderRegion
└─ WorkspaceRegion
   ├─ BreadcrumbRegion
   ├─ PageHeaderRegion
   └─ PageContentSlot
```

Responsabilidades:

```text
AppShell
→ estrutura administrativa
→ comportamento expandido/compacto/overlay
→ landmarks
→ skip link
→ coordenação de foco do shell
→ espaço disponível do workspace

PageContent
→ conteúdo e ações da superfície
→ estados da tarefa
→ componentes específicos da página
```

## O que deve ser compartilhado

A adoção futura deve preservar uma única implementação comportamental para:

```text
SIDEBAR_EXPANDED_COMPACT_OVERLAY
SIDEBAR_PREFERENCE_NON_SENSITIVE
RELEASED_WIDTH_TO_WORKSPACE
MOBILE_OVERLAY
BACKDROP
ESCAPE
FOCUS_ENTRY_RETURN
INERT_BACKGROUND
TOPHEADER_STRUCTURE
APP_CONTEXT_PRESENTATION
SINGLE_MAIN
SKIP_LINK
RESPONSIVE_SHELL_REFLOW
REDUCED_MOTION
```

A página não deve duplicar esses mecanismos.

## O que pode variar por página

```text
ACTIVE_NAV_ITEM
BREADCRUMB_CONTENT
PAGE_TITLE
PAGE_DESCRIPTION
PAGE_PRIMARY_ACTION
PAGE_CONTENT
AUTHORIZED_GLOBAL_ACTIONS_WHEN_APPLICABLE
```

Variação de conteúdo não cria uma nova variante arquitetural de AppShell.

## Identidade visual e nomes temporários

As classes `.i1-*` pertencem à materialização de referência de I1 e **não são congeladas como API definitiva**.

```text
I1_CLASS_NAMES=REFERENCE_IMPLEMENTATION_DETAIL
I1_CLASS_NAMES_AS_PERMANENT_PUBLIC_API=NOT_FROZEN
```

I2 exige que a implementação reutilizável futura possua nomenclatura neutra e compatível com o contrato canônico, sem carregar o número da etapa como identidade permanente.

Exemplo conceitual:

```text
app-shell
app-shell__sidebar
app-shell__header
app-shell__workspace
```

Os nomes exatos ainda não são congelados neste gate.

## Estratégia de convergência

A sequência correta é:

```text
I1
→ baseline visual/estrutural isolada

I2
→ contrato de adoção/reuso

I3+
→ materializar substrato compartilhável
→ reconciliar superfícies uma por vez
→ validar integração
```

Não executar:

```text
MASS_SCREEN_REWRITE
BIG_BANG_MIGRATION
COPY_I1_HTML_INTO_EVERY_SCREEN
PARALLEL_SHELL_VARIANTS
```

## Superfícies ainda não reconciliadas

```text
DASHBOARD_RECONCILED_WITH_CANONICAL_APPSHELL=NO
EMPLOYEES_RECONCILED_WITH_CANONICAL_APPSHELL=NO
ONBOARDING_RECONCILED_WITH_CANONICAL_APPSHELL=NO
```

Essas superfícies permanecem como material histórico/visual do Design Lab até seus gates próprios.

## `/punch`

I2 preserva explicitamente:

```text
PUNCH_ROUTE => OUTSIDE_ADMIN_APPSHELL
SHARED_DESIGN_SYSTEM != SHARED_APPLICATION_SHELL
```

A adoção do AppShell administrativo nunca deve envolver automaticamente a jornada `/punch`.

## RBAC, contexto e dados

A estrutura compartilhada não pode transformar estado visual do shell em autoridade:

```text
UI_VISIBILITY != AUTHORIZATION
APP_CONTEXT != EMPRESA_DO_VINCULO
CLIENT_RBAC_CHECK != SERVER_AUTHORIZATION
```

Quando futuramente integrado à aplicação real, o backend continuará sendo a autoridade para permissões, escopo e dados.

I2 não cria novas permissões, tenants, rotas ou contratos de backend.

## Responsividade

A adoção do AppShell deve preservar H7:

```text
RESPONSIVE != SHRINK_DESKTOP
COMPONENT_SPACE != DEVICE_NAME
RELEASED_SIDEBAR_WIDTH => WORKSPACE
PAGE_LEVEL_HORIZONTAL_OVERFLOW=PROHIBITED
```

A página deve receber o espaço efetivamente disponibilizado pelo shell e responder a ele sem assumir largura fixa da sidebar.

## Acessibilidade

A implementação compartilhada futura deverá concentrar e testar, uma vez, os comportamentos comuns:

```text
SINGLE_MAIN
SKIP_LINK
VISIBLE_FOCUS
ARIA_EXPANDED
HIDDEN_NAV_NOT_TABBABLE
MOBILE_BACKGROUND_INERT
ESCAPE_OWNERSHIP
FOCUS_ENTRY
FOCUS_RETURN
REDUCED_MOTION
```

A página continua responsável pela acessibilidade de seu próprio conteúdo.

## Testes futuros derivados

### Unitários

- contrato expanded/compact/overlay do shell compartilhado;
- persistência somente de preferência visual não sensível;
- `aria-expanded` e accessible name;
- `inert` em mobile;
- retorno de foco;
- ausência de gutter morto após collapse;
- reduced motion.

### Integração

- mesmo AppShell + Dashboard;
- mesmo AppShell + Funcionários;
- mesmo AppShell + onboarding;
- mudança de página preservando preferência do shell;
- mudança de viewport preservando contrato;
- `/punch` fora do shell administrativo.

### Regressão

```text
COPY_PASTE_SHELL_PER_SCREEN................ NO
TWO_CANONICAL_ADMIN_SHELLS................. NO
PAGE_CONTENT_OWNS_GLOBAL_SHELL.............. NO
LEGACY_SHELL_USED_FOR_NEW_SCREEN_WORK....... NO
PUNCH_WRAPPED_BY_ADMIN_SHELL................ NO
APP_CONTEXT_MUTATES_EMPLOYMENT_FIELD........ NO
```

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

## Resultado de I2

```text
I2_APPSHELL_ADOPTION_CONTRACT=COMPLETE
CANONICAL_APPSHELL=ONE
LEGACY_APP_SHELL=SUPERSEDED_FOR_NEW_WORK
SCREEN_RECONCILIATION=NOT_STARTED
IMPLEMENTATION_ARCHITECTURE_LIBRARY=NOT_FROZEN
```

## Próxima decisão

I2 fecha a regra de adoção. O próximo item deve definir como materializar o substrato reutilizável do AppShell dentro do Design Lab sem ainda fazer uma migração em massa das superfícies.

```text
NEXT_OFFICIAL_ITEM=I3_DEFINITION_GATE
```
