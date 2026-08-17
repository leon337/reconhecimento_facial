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
../52_NF01_DESIGN_LAB_I6_ONBOARDING_V2_APPSHELL_ADOPTION_2026-08-17.md
```

`DECISOES_CONGELADAS.md` permanece inalterado e superior quando aplicável.

## Isolamento

```text
PROTOTYPE_SCOPE=docs/nf-01/prototype/**
PRODUCTION_TEMPLATES_CHANGED=NO
FLASK_ROUTES_CHANGED=NO
BACKEND_CHANGED=NO
NF02_STARTED=NO
MERGE_AUTHORIZED=NO
```

Usar somente dados fictícios no laboratório.

## AppShell compartilhado

```text
assets/app-shell.css
+
assets/app-shell.js
```

A página consumidora fornece metadados e um único `<main id="conteudo" data-app-shell-content>`. O substrato materializa `CollapsibleSidebar + TopHeader + MainWorkspace`, comportamento responsivo, preferência compacta, foco, `inert`, Escape e item ativo.

```text
DESIGN_LAB_JS_COMPOSITION != PRODUCTION_ARCHITECTURE
CANONICAL_APPSHELL=ONE
```

## Estado da Fase I

```text
I1_DESIGN_LAB_APPSHELL=COMPLETE
I2_APPSHELL_ADOPTION_CONTRACT=COMPLETE
I3_SHARED_APPSHELL_SUBSTRATE=COMPLETE
I4_DASHBOARD_SHARED_APPSHELL_ADOPTION=COMPLETE
I5_EMPLOYEES_SHARED_APPSHELL_ADOPTION=COMPLETE
I6_ONBOARDING_V2_SHARED_APPSHELL_ADOPTION=COMPLETE
PRODUCTION_CHANGE=NO
```

Consumidores atuais:

```text
01.01 AppShell referência............. I3
02.01 Dashboard Desktop V3........... I4
03.01 Funcionários Desktop V1........ I5
03.04 Novo Funcionário Desktop V2.... I6
```

Dashboard, Funcionários e Novo Funcionário V2 compartilham o mesmo casco administrativo. O conteúdo específico permanece independente e ainda será reconciliado nas fases J/K/L.

## Limites das adoções

```text
DASHBOARD_CONTENT_REDESIGN_IN_I4=NO
PHASE_J_DASHBOARD_RECONCILIATION=NOT_STARTED

EMPLOYEES_CONTENT_REDESIGN_IN_I5=NO
PHASE_K_EMPLOYEES_RECONCILIATION=NOT_STARTED

ONBOARDING_CONTENT_REDESIGN_IN_I6=NO
PHASE_L_ONBOARDING_RECONCILIATION=NOT_STARTED
```

I6 removeu do Novo Funcionário V2 o casco administrativo local e a dependência de `dashboard-v3.css`, preservando wizard de oito etapas, draft local, validação e `new-employee-v2.js`.

Decisões históricas ainda visíveis no conteúdo do onboarding — rail vertical, painel lateral e organização espacial anterior — continuam substituídas pelo contrato canônico e serão tratadas somente na Fase L.

## Direção canônica

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

## Novo Funcionário — oito etapas

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

## Design System

```text
FONT=Manrope
ICON_FAMILY=Lucide
BASE_UNIT=rem
GRID=fr/minmax
FLUID=clamp
COMPONENT_RESPONSIVE=container queries quando aplicável
PX=exceção técnica
RESPONSIVO != DIMINUIR_TUDO
RESPONSIVO = REORGANIZAR
```

## Validação ainda pendente

```text
BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
INTERMEDIATE_WIDTH_VISUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
SCREEN_READER_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E=NO
```

## Testes futuros

```text
UNITARIO
→ montagem idempotente + active nav + preferência + aria-expanded + inert + foco + reduced motion

INTEGRACAO
→ AppShell + Dashboard + Funcionários + Onboarding V2 + conteúdos independentes preservados

RESPONSIVO
→ 360 / 768 / 1024 / 1440 + intermediários + container resize

ACESSIBILIDADE
→ teclado / foco / screen reader / labels / aria / contraste / reduced motion / zoom 200%
```

O Design Lab funciona como estação de pré-montagem: a peça é auditada aqui antes de qualquer entrada na linha de produção.
