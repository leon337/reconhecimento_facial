# NF-01 — Design Lab

Laboratório visual isolado da NF-01.

```text
CANONICAL_APPSHELL=ONE
CURRENT_APPSHELL_OWNER=assets/app-shell.css+app-shell.js
CURRENT_APPSHELL_VERSION=i8
LEGACY_SHELL_OWNER=assets/legacy-shell.css+legacy-shell.js
DASHBOARD_SHARED_APPSHELL=YES
EMPLOYEES_SHARED_APPSHELL=YES
ONBOARDING_SHARED_APPSHELL=YES

PHASE_I_DESIGN_LAB_APPSHELL=COMPLETE_SOURCE_LEVEL
PHASE_J_DASHBOARD_RECONCILIATION=COMPLETE_SOURCE_LEVEL
PHASE_K_EMPLOYEES_RECONCILIATION=COMPLETE_SOURCE_LEVEL
PHASE_L_ONBOARDING_RECONCILIATION=COMPLETE_SOURCE_LEVEL

PHASE_M_CROSS_SCREEN_COHERENCE=IN_PROGRESS
M1_CROSS_SCREEN_COHERENCE_AUDIT=COMPLETE
M1_OUTPUT=../65_NF01_PHASE_M_M1_CROSS_SCREEN_COHERENCE_AUDIT_2026-08-18.md
M1_AUDIT_RESULT=GAPS_FOUND
M1_HIGH_GAP_THEMES=5
M2_CROSS_SCREEN_COHERENCE_RECONCILIATION=COMPLETE
M2_OUTPUT=../66_NF01_PHASE_M_M2_CROSS_SCREEN_COHERENCE_RECONCILIATION_2026-08-18.md
M2_ACCEPTANCE=PASS_SOURCE_LEVEL
M1_HIGH_GAPS_RECONCILED_SOURCE_LEVEL=5/5

CROSS_SCREEN_SHARED_CONTEXT=Potiguar_Locacoes|Galpao_principal
CROSS_SCREEN_SHARED_PROFILE=Administrador_Demo|admin
CROSS_SCREEN_SHARED_EMPLOYEE_SOURCE=fixture:employees-k2
DASHBOARD_TO_EMPLOYEES_HANDOFF=biometric=missing
EMPLOYEES_LIST_STATE_RESTORE=sessionStorage_context_scoped
ONBOARDING_VISIBLE_NAME=Novo_Funcionario
ONBOARDING_DEMO_MUTATES_EMPLOYEE_LIST=NO

ACTIVE_SURFACE_LEGACY_SHELL_DEPENDENCY=0
HISTORICAL_V1=screens/03.03-novo-funcionario.html
HISTORICAL_V1_PRESERVED=YES
HISTORICAL_V1_MIGRATED=NO

NEXT_OFFICIAL_PHASE=M_CROSS_SCREEN_COHERENCE
NEXT_OFFICIAL_ITEM=M3_CROSS_SCREEN_POST_RECONCILIATION_ACCEPTANCE_GATE
M3_APPROVAL_INFERRED=NO
PRODUCTION_CHANGE=NO
NF02_STARTED=NO
PR_MERGE=NOT_AUTHORIZED
```

## Estado atual das superfícies

### Dashboard

`screens/02.01-dashboard.html` preserva o contrato canônico de J2/J3 e, em M2, foi reconciliado com a amostra local de Funcionários:

- `Funcionários cadastrados = 6` para a mesma amostra local;
- João Souza = matrícula `00124`;
- Maria Silva = matrícula `00123`;
- Lucas Santos = matrícula `00131`;
- Ana Paula = matrícula `00142`;
- unidade demonstrativa das linhas de atividade = `Galpão principal`;
- origem compartilhada = `fixture:employees-k2`;
- `2 biometrias pendentes` continua derivado da mesma amostra;
- `Ver funcionários filtrados` navega para `03.01-funcionarios.html?biometric=missing&source=dashboard`.

`Registros hoje` continua uma fixture separada de registros e não é apresentado como derivação da lista local de Funcionários.

### Funcionários

`screens/03.01-funcionarios.html` continua preservando os contratos fechados em K3. M2 altera somente `assets/employees-v1.js` para integração cruzada:

- query string explícita pode aplicar `q`, `biometric` e `function`;
- handoff do Dashboard aplica `biometric=missing`;
- busca e filtros são preservados em `sessionStorage` escopado ao contexto demonstrativo;
- handoff explícito tem precedência sobre estado restaurado;
- retorno do onboarding reutiliza o estado anterior da lista na mesma sessão;
- `FILTER_NO_RESULTS` permanece diferente de `EMPTY_DATASET` e `ERROR`.

### Novo Funcionário

A estrutura funcional do onboarding permanece a fechada em L3. M2 usa `assets/interactions.js` como pequeno substrato compartilhado do Design Lab para manter:

- contexto visível `Potiguar Locações / Galpão principal`;
- principal `Administrador Demo / Admin`;
- conjunto demonstrativo padrão `users:view users:create biometrics:manage punch:view punch:create`;
- `aria-label` do contexto coerente após montagem do AppShell;
- nome visível `Novo Funcionário`, mantendo `V2` somente como detalhe técnico do arquivo;
- breadcrumb sem o primeiro nível redundante `Gestão`;
- painel de sucesso explícito: a demonstração não altera a lista de Funcionários.

O seletor de perfil do ContextDrawer permanece uma simulação explícita de variante do fluxo; não representa mudança silenciosa do principal real.

## Continuidade

```text
58_* J3
↓
61_* K3
↓
64_* L3
↓
65_* M1
↓
66_* M2
```

O `13_NF01_REMAINING_WORK_ROADMAP.md` ainda precisa ser sincronizado com M1/M2. Até essa correção documental, os checkpoints 65/66 e o corpo do PR representam a continuidade mais recente da Fase M.

## Validação ainda diferida

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

O workflow geral do repositório pode validar sintaxe e regressão existente, mas isso não substitui os testes específicos de aceitação do Design Lab previstos para a Fase N.

## Guardrails

```text
DO_NOT_MERGE_WITHOUT_EXPLICIT_LEANDRO_APPROVAL
DO_NOT_START_NF02
DO_NOT_CHANGE_PRODUCTION_CODE
DO_NOT_CHANGE_BACKEND
DO_NOT_DEPLOY
DO_NOT_DECLARE_LEGAL_COMPLIANCE
```
