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
PHASE_M_CROSS_SCREEN_COHERENCE=COMPLETE_SOURCE_LEVEL
PHASE_N_DESIGN_LAB_VALIDATION=IN_PROGRESS

M1_CROSS_SCREEN_COHERENCE_AUDIT=COMPLETE
M1_OUTPUT=../65_NF01_PHASE_M_M1_CROSS_SCREEN_COHERENCE_AUDIT_2026-08-18.md
M2_CROSS_SCREEN_COHERENCE_RECONCILIATION=COMPLETE
M2_OUTPUT=../66_NF01_PHASE_M_M2_CROSS_SCREEN_COHERENCE_RECONCILIATION_2026-08-18.md
M3_CROSS_SCREEN_POST_RECONCILIATION_ACCEPTANCE=COMPLETE
M3_OUTPUT=../67_NF01_PHASE_M_M3_CROSS_SCREEN_POST_RECONCILIATION_ACCEPTANCE_2026-08-18.md
UNRESOLVED_CROSS_SCREEN_BLOCKING_GAPS=0

N1_DESIGN_LAB_VALIDATION_DEFINITION=COMPLETE
N1_OUTPUT=../68_NF01_PHASE_N_N1_DESIGN_LAB_VALIDATION_DEFINITION_2026-08-18.md
N1_IMPLEMENTATION=VALIDATION_PLAN_ONLY
N2_BROWSER_RESPONSIVE_VISUAL_VALIDATION=NOT_APPROVED
N3_ACCESSIBILITY_INTERACTION_STATE_RBAC_VALIDATION=NOT_APPROVED
N4_PHASE_N_CONSOLIDATED_ACCEPTANCE=NOT_APPROVED

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

NEXT_OFFICIAL_PHASE=N_DESIGN_LAB_VALIDATION
NEXT_OFFICIAL_ITEM=N2_BROWSER_RESPONSIVE_VISUAL_VALIDATION_GATE
N2_APPROVAL_INFERRED=NO
PRODUCTION_CHANGE=NO
NF02_STARTED=NO
PR_MERGE=NOT_AUTHORIZED
```

## Estado atual das superfícies

### Dashboard

`screens/02.01-dashboard.html` permanece reconciliado com a amostra local compartilhada:

- `Funcionários cadastrados = 6`;
- João Souza = matrícula `00124`;
- Maria Silva = matrícula `00123`;
- Lucas Santos = matrícula `00131`;
- Ana Paula = matrícula `00142`;
- unidade demonstrativa = `Galpão principal`;
- origem compartilhada = `fixture:employees-k2`;
- `2 biometrias pendentes` deriva da mesma amostra;
- `Ver funcionários filtrados` navega para `03.01-funcionarios.html?biometric=missing&source=dashboard`.

`Registros hoje` continua uma fixture separada de registros.

### Funcionários

`screens/03.01-funcionarios.html` preserva os contratos fechados em K3/M3:

- query explícita pode aplicar `q`, `biometric` e `function`;
- handoff do Dashboard aplica `biometric=missing`;
- busca e filtros são preservados em `sessionStorage` escopado ao contexto;
- handoff explícito tem precedência sobre estado restaurado;
- retorno do onboarding reutiliza o estado anterior na mesma sessão;
- `FILTER_NO_RESULTS` permanece diferente de `EMPTY_DATASET` e `ERROR`.

### Novo Funcionário

A estrutura funcional permanece a fechada em L3/M3:

- contexto visível `Potiguar Locações / Galpão principal`;
- principal `Administrador Demo / Admin`;
- permissões demonstrativas padrão `users:view users:create biometrics:manage punch:view punch:create`;
- nome visível `Novo Funcionário`, mantendo `V2` somente no nome técnico do arquivo;
- breadcrumb deduplicado em runtime;
- conclusão demo não altera a lista real de Funcionários.

## Fase N — matriz definida em N1

N1 não alterou HTML/CSS/JS. Ele definiu a inspeção que os próximos gates deverão executar.

### N2 — visual/responsivo

```text
CANONICAL_VIEWPORTS=360|768|1024|1440
INTERMEDIATE_VIEWPORTS=480|900|1280
CONTAINER_FIRST_VALIDATION=REQUIRED
ZOOM_200_MANUAL_TEST=REQUIRED
```

Cobertura: AppShell, Dashboard, Funcionários, Novo Funcionário e handoffs cross-screen.

### N3 — acessibilidade/interação/estados/RBAC

```text
KEYBOARD_CRITICAL_JOURNEY=REQUIRED
SCREEN_READER_CRITICAL_JOURNEY=REQUIRED
AUTOMATED_A11Y_SCAN=IF_TOOLING_AVAILABLE
RBAC_VISUAL_MATRIX=REQUIRED
STATE_MATRIX=REQUIRED
```

Se ferramenta necessária não estiver disponível, o resultado deve ser `BLOCKED_TOOLING`; PASS não pode ser inferido.

### N4 — aceite consolidado

N4 somente pode fechar a Fase N com zero BLOCKER/HIGH aberto e evidência explícita dos casos exigidos por N1.

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
↓
67_* M3
↓
68_* N1
```

## Validação ainda não executada

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

O contrato canônico da NF-01 mantém novos testes unitários/de integração como não executados; a Fase N revisa sua cobertura documental, mas não os declara PASS.

## Guardrails

```text
DO_NOT_MERGE_WITHOUT_EXPLICIT_LEANDRO_APPROVAL
DO_NOT_START_NF02
DO_NOT_CHANGE_PRODUCTION_CODE
DO_NOT_CHANGE_BACKEND
DO_NOT_DEPLOY
DO_NOT_DECLARE_LEGAL_COMPLIANCE
```