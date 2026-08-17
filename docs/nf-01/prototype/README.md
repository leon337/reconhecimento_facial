# NF-01 — Design Lab

Laboratório visual isolado para materializar e auditar a NF-01 antes da NF-02.

## Fonte canônica

```text
../12_NF01_CANONICAL_DECISIONS_2026-08-11.md
../13_NF01_REMAINING_WORK_ROADMAP.md
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

## AppShell

```text
CANONICAL_APPSHELL=ONE
SHARED_APPSHELL=assets/app-shell.css+assets/app-shell.js
DESIGN_LAB_JS_COMPOSITION != PRODUCTION_ARCHITECTURE
```

Consumidores:

```text
01.01 referência AppShell............. I3
02.01 Dashboard...................... I4
03.01 Funcionários................... I5
03.04 Novo Funcionário V2............ I6
```

Dashboard, Funcionários e Novo Funcionário V2 compartilham o mesmo casco administrativo no Design Lab. As fases J/K/L continuam não iniciadas; I4/I5/I6 não redesenharam o conteúdo das respectivas telas.

I6 preservou wizard de oito etapas, draft, validação e `new-employee-v2.js`, removeu Sidebar/TopHeader locais e eliminou a dependência de `dashboard-v3.css` do onboarding V2.

Decisões históricas internas do wizard, como rail vertical e painel lateral, continuam visíveis somente como material a reconciliar na Fase L.

```text
NEXT_OFFICIAL_ITEM=I7_DEFINITION_GATE
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

O Design Lab funciona como estação de pré-montagem antes de qualquer alteração de produção.
