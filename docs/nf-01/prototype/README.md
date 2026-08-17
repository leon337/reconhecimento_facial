# NF-01 — Design Lab

Laboratório visual isolado para materializar e auditar a NF-01 antes da NF-02.

## Fonte canônica

Antes de alterar qualquer tela do laboratório, ler:

```text
../12_NF01_CANONICAL_DECISIONS_2026-08-11.md
../05_DESIGN_SYSTEM.md
../06_COMPONENT_CATALOG.md
../07_WIREFRAMES.md
../08_RESPONSIVE_ACCESSIBILITY.md
../09_TEST_AND_ACCEPTANCE_STRATEGY.md
../46_NF01_CATALOG_COMPLETENESS_H10_CLOSEOUT_2026-08-17.md
../47_NF01_DESIGN_LAB_I1_APPSHELL_2026-08-17.md
../48_NF01_DESIGN_LAB_I2_APPSHELL_ADOPTION_CONTRACT_2026-08-17.md
../49_NF01_DESIGN_LAB_I3_SHARED_APPSHELL_SUBSTRATE_2026-08-17.md
../50_NF01_DESIGN_LAB_I4_DASHBOARD_APPSHELL_ADOPTION_2026-08-17.md
../51_NF01_DESIGN_LAB_I5_EMPLOYEES_APPSHELL_ADOPTION_2026-08-17.md
```

`DECISOES_CONGELADAS.md` permanece inalterado e superior quando aplicável.

## Regra de isolamento

```text
PROTOTYPE_SCOPE=docs/nf-01/prototype/**
PRODUCTION_TEMPLATES_CHANGED=NO
FLASK_ROUTES_CHANGED=NO
BACKEND_CHANGED=NO
NF02_STARTED=NO
MERGE_AUTHORIZED=NO
```

Durante auditoria, usar somente dados fictícios. Não inserir dados pessoais reais no Design Lab.

## Estrutura atual

```text
prototype/
├── index.html
├── README.md
├── NEW_EMPLOYEE_V2_UX_SPEC.md
├── assets/
│   ├── app-shell.css
│   ├── app-shell.js
│   ├── dashboard-v3.css
│   ├── employees-v1.css
│   └── employees-v1.js
├── components/
└── screens/
    ├── 01.01-app-shell.html
    ├── 02.01-dashboard.html
    ├── 03.01-funcionarios.html
    ├── 03.03-novo-funcionario.html
    └── 03.04-novo-funcionario-v2.html
```

Os antigos `app-shell-i1.css` e `app-shell-i1.js` foram substituídos pelo substrato compartilhado I3 e não devem voltar a ser usados em novas telas.

## Como abrir localmente

```bash
python3 -m http.server 4173 -d docs/nf-01/prototype
```

Depois:

```text
http://localhost:4173/
```

## Fase I — AppShell

```text
I1_DESIGN_LAB_APPSHELL=COMPLETE
I2_APPSHELL_ADOPTION_CONTRACT=COMPLETE
I3_SHARED_APPSHELL_SUBSTRATE=COMPLETE
I4_DASHBOARD_SHARED_APPSHELL_ADOPTION=COMPLETE
I5_EMPLOYEES_SHARED_APPSHELL_ADOPTION=COMPLETE
CANONICAL_APPSHELL=ONE
FIRST_INCREMENTAL_CONSUMER=screens/02.01-dashboard.html
SECOND_INCREMENTAL_CONSUMER=screens/03.01-funcionarios.html
PRODUCTION_CHANGE=NO
```

### I1 — baseline visual

I1 materializou `CollapsibleSidebar + TopHeader + MainWorkspace`, com desktop expandido/compacto, overlay mobile, foco, `inert`, Escape, reduced motion, skip link e um único `main`.

### I2 — contrato de adoção

```text
CANONICAL_APPSHELL=ONE
PAGE_CONTENT != SHELL_IMPLEMENTATION
SHARED_APPSHELL_STRUCTURE=REQUIRED
SHARED_APPSHELL_BEHAVIOR=REQUIRED
COPY_PASTE_SHELL_PER_SCREEN=PROHIBITED
LEGACY_APP_SHELL=SUPERSEDED_FOR_NEW_WORK
```

### I3 — substrato reutilizável

```text
assets/app-shell.css
+
assets/app-shell.js
```

A página consumidora fornece metadados e um único `<main id="conteudo" data-app-shell-content>`. O bootstrap compartilhado materializa Sidebar, TopHeader, workspace, comportamento responsivo, preferência compacta, foco, `inert`, Escape e item ativo.

```text
DESIGN_LAB_JS_COMPOSITION != PRODUCTION_ARCHITECTURE
```

### I4 — Dashboard

`screens/02.01-dashboard.html` tornou-se o primeiro consumidor real do AppShell compartilhado, sem iniciar a Fase J.

```text
DASHBOARD_SHARED_APPSHELL=YES
DASHBOARD_LOCAL_SIDEBAR=REMOVED
DASHBOARD_LOCAL_TOPHEADER=REMOVED
DASHBOARD_CONTENT_REDESIGN_IN_I4=NO
PHASE_J_DASHBOARD_RECONCILIATION=NOT_STARTED
```

`dashboard-v3.css` preserva somente o conteúdo do Dashboard. `components.css` e `interactions.js` mantêm compatibilidade histórica para telas ainda não migradas.

### I5 — Funcionários

`screens/03.01-funcionarios.html` tornou-se o segundo consumidor real do mesmo substrato, sem iniciar a Fase K.

```text
EMPLOYEES_SHARED_APPSHELL=YES
EMPLOYEES_LOCAL_SIDEBAR=REMOVED
EMPLOYEES_LOCAL_TOPHEADER=REMOVED
EMPLOYEES_CONTENT_REDESIGN_IN_I5=NO
PHASE_K_EMPLOYEES_RECONCILIATION=NOT_STARTED
```

Foram preservados:

```text
Breadcrumb
PageHeader
summary cards
Search
filtros
DataTable
Pagination
EmptyState
employees-v1.js
Toast/interações demonstrativas
```

`employees-v1.css` agora contém apenas estilos do conteúdo de Funcionários; as regras locais do shell foram removidas. A busca e os filtros permanecem locais e demonstrativos.

## Estado visual

```text
AppShell I3...................... substrato compartilhado + referência canônica
Dashboard Desktop V3........... consumidor compartilhado I4; conteúdo preservado
Funcionários Desktop V1........ consumidor compartilhado I5; conteúdo preservado
Novo Funcionário Desktop V1.... referência histórica
Novo Funcionário Desktop V2.... contrato funcional preservado; shell ainda não migrado
```

## Direções substituídas

```text
sidebar permanentemente expandida........ SUPERSEDED
shell copiado por tela.................... SUPERSEDED
classes .i1-* como API permanente......... SUPERSEDED
stepper vertical do onboarding............ SUPERSEDED
painel contextual direito permanente...... SUPERSEDED
larguras fixas em px como regra geral..... SUPERSEDED
emoji como iconografia de produção......... SUPERSEDED
```

## Direção atual

```text
Shared AppShell substrate
+
CollapsibleSidebar
+
TopHeader
+
Breadcrumb / PageHeader fornecidos pela página
+
HorizontalStepper quando houver wizard
+
MainWorkspace amplo
+
ContextDrawer sob demanda
+
StickyFormActions no onboarding
```

`/punch` permanece fora do AppShell administrativo.

## Novo Funcionário — contrato preservado

O wizard continua com oito etapas:

```text
0 Tipo de relação
1 Dados pessoais
2 Endereço
3 Vínculo
4 Pagamento
5 Acesso ao sistema
6 Biometria
7 Revisão e conclusão
```

Regras principais permanecem: `HorizontalStepper` icon-first; `NEEDS_REVIEW`; `ContextDrawer` sob demanda; `StickyFormActions`; autosave/draft/conflito/retomada; EntityPicker com catálogo mestre/ID; biometria separada da foto administrativa; conclusão futura transacional/idempotente; `OUTCOME_UNKNOWN` exige reconciliação; contexto do header não é empresa contratante.

## Design System atual

```text
FONT=Manrope
ICON_FAMILY=Lucide
BASE_UNIT=rem
GRID=fr/minmax
FLUID=clamp
COMPONENT_RESPONSIVE=container queries quando aplicável
VIEWPORT_UNITS=limitadas e contextuais
PX=exceção técnica
```

```text
RESPONSIVO != DIMINUIR_TUDO
RESPONSIVO = REORGANIZAR
```

## Auditoria obrigatória

- coerência com o registro canônico;
- uma única implementação viva do AppShell;
- exatamente um `main` por consumidor;
- ausência de shell duplicado após montagem repetida;
- conteúdo de cada consumidor preservado;
- 360/768/1024/1440 + larguras intermediárias;
- zoom 200%;
- keyboard-only;
- screen reader;
- reduced motion;
- mobile keyboard safe;
- estados de erro/loading/conflict/offline;
- ausência de dados ou estados apresentados como reais sem fonte.

## Testes futuros

```text
UNITARIO
→ montagem idempotente + active nav + preferência + aria-expanded + inert + foco + reduced motion

INTEGRACAO
→ AppShell + Dashboard + Funcionários + conteúdos independentes preservados

RESPONSIVO
→ 360 / 768 / 1024 / 1440 + intermediários + container resize

ACESSIBILIDADE
→ teclado / foco / screen reader / labels / aria / contraste / reduced motion / zoom 200%
```

O Design Lab funciona como estação de pré-montagem: a peça é auditada aqui antes de qualquer entrada na linha de produção.
