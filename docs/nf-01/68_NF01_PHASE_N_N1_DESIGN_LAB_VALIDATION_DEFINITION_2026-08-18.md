# NF-01 — Fase N — N1 — Definição da validação do Design Lab

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-18  
**Autoridade humana:** LEANDRO

## Gate e estado

```text
N1_DESIGN_LAB_VALIDATION_DEFINITION=APPROVED_BY_LEANDRO
N1_STATUS=COMPLETE
PHASE_N_DESIGN_LAB_VALIDATION=IN_PROGRESS

IMPLEMENTATION=VALIDATION_PLAN_ONLY
DESIGN_LAB_VISUAL_CHANGE_IN_N1=NO
DESIGN_LAB_BEHAVIOR_CHANGE_IN_N1=NO
PRODUCTION_CHANGE=NO
BACKEND_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate foi consumida somente para N1. N2, N3, N4, Fase O, NF-02, produção, deploy e merge permanecem sem autorização inferida.

---

## 1. Objetivo

Transformar os contratos de responsividade, acessibilidade, estados, RBAC e coerência cross-screen já definidos pela NF-01 em uma matriz de homologação executável e auditável.

Linha de montagem da qualidade:

```text
REQUISITO
  ↓
DESIGN
  ↓
ARQUITETURA
  ↓
IMPLEMENTAÇÃO SOURCE-LEVEL
  ↓
N1 DEFINIR A INSPEÇÃO
  ↓
N2 VISUAL / RESPONSIVO / REFLOW
  ↓
N3 ACESSIBILIDADE / INTERAÇÃO / ESTADOS / RBAC
  ↓
N4 CONSOLIDAR EVIDÊNCIAS E ACEITE DA FASE N
  ↓
FASE O EVIDÊNCIAS / FECHAMENTO NF-01
```

N1 não executa a inspeção; define exatamente o que deverá ser observado, como classificar o resultado e quais evidências serão aceitas.

---

## 2. Fontes canônicas da matriz

```text
docs/nf-01/04_ROLES_PERMISSIONS_AND_STATES.md
docs/nf-01/05_DESIGN_SYSTEM.md
docs/nf-01/06_COMPONENT_CATALOG.md
docs/nf-01/07_WIREFRAMES.md
docs/nf-01/08_RESPONSIVE_ACCESSIBILITY.md
docs/nf-01/09_TEST_AND_ACCEPTANCE_STRATEGY.md
docs/nf-01/12_NF01_CANONICAL_DECISIONS_2026-08-11.md
docs/nf-01/13_NF01_REMAINING_WORK_ROADMAP.md
docs/nf-01/58_*_J3_*.md
docs/nf-01/61_*_K3_*.md
docs/nf-01/64_*_L3_*.md
docs/nf-01/67_*_M3_*.md
```

Princípios obrigatórios preservados:

```text
RESPONSIVO != DIMINUIR_TUDO
RESPONSIVO = REORGANIZAR + REDISTRIBUIR + LIMITAR + EXPANDIR + COLAPSAR
READING_ORDER = FOCUS_ORDER = TASK_LOGIC
PERMISSAO_BACKEND -> NAVEGACAO_VISIVEL -> ACAO_VISIVEL -> AUTORIZACAO_BACKEND
FALSE_GREEN=PROHIBITED
PRODUCTION_HOMOLOGATION=SEPARATE
```

---

## 3. Escopo de superfícies

### Ativas — obrigatórias

```text
N-S1  docs/nf-01/prototype/screens/01.01-app-shell.html
N-S2  docs/nf-01/prototype/screens/02.01-dashboard.html
N-S3  docs/nf-01/prototype/screens/03.01-funcionarios.html
N-S4  docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
```

### Suporte — obrigatórias quando o caso depende delas

```text
N-S5  docs/nf-01/prototype/index.html
N-S6  docs/nf-01/prototype/components/catalog.html
N-S7  assets/app-shell.css + app-shell.js
N-S8  assets/interactions.js
N-S9  assets/employees-v1.js
N-S10 assets/new-employee-v2.css + new-employee-v2.js
N-S11 assets/dashboard-v3.css
```

### Histórica

```text
03.03-novo-funcionario.html=REFERENCE_ONLY
```

A V1 histórica não entra na homologação visual principal. O que precisa ser preservado é sua quarentena: ela não pode contaminar as superfícies ativas nem reintroduzir shell legado.

### Fora da execução da Fase N

```text
PRODUCTION_E2E=OUT_OF_SCOPE
REAL_BACKEND_RBAC=OUT_OF_SCOPE
REAL_EMPLOYEE_PERSISTENCE=OUT_OF_SCOPE
REAL_BIOMETRIC_STORAGE=OUT_OF_SCOPE
PONTO_TO_ATTENDANCE_EVENT_MIGRATION=OUT_OF_SCOPE
NF02=OUT_OF_SCOPE
DEPLOY=OUT_OF_SCOPE
```

---

## 4. Matriz visual e responsiva — N2

### Viewports mínimos canônicos

```text
360
768
1024
1440
```

Esses valores são alvos de teste, não layouts rígidos.

### Larguras intermediárias definidas por N1

```text
480
900
1280
```

Além delas, qualquer breakpoint estrutural descoberto durante a inspeção deverá receber teste imediatamente abaixo e acima do ponto de mudança quando houver risco de perda de legibilidade ou funcionalidade.

### Container-first

Componentes reutilizáveis também devem ser inspecionados quando recebem espaço diferente do viewport:

```text
container estreito
container médio
container largo
```

Aplicável especialmente a:

```text
MetricCard
employee table/card transformation
ResponsiveFormGrid
HorizontalStepper
ContextDrawer
StickyFormActions
EntityPicker
```

### Zoom / reflow

```text
ZOOM_200_MANUAL_TEST=REQUIRED_IN_N2
```

Critérios:

- conteúdo essencial permanece acessível;
- sem clipping que impeça leitura/ação;
- sem overflow horizontal indevido da página;
- overlays e ações continuam alcançáveis;
- ordem lógica não muda por CSS.

### Checklist visual por superfície

Cada superfície ativa deve validar:

```text
NO_UNINTENDED_HORIZONTAL_OVERFLOW
NO_TEXT_CLIPPING
NO_OVERLAP_BLOCKING_ACTION
NO_DEAD_SPACE_FROM_COLLAPSED_SIDEBAR
PRIMARY_ACTION_REMAINS_REACHABLE
FOCUS_INDICATOR_NOT_VISUALLY_CLIPPED
TOUCH_TARGETS_COMFORTABLE
STATE_COPY_READABLE
DEMO_NOTICE_VISIBLE_WHEN_REQUIRED
```

### AppShell

```text
wide desktop -> expanded/compact behavior coherent
~1024 -> compact behavior coherent
~768 -> overlay expansion without hover dependency
~360 -> sidebar not permanent column
content recovers freed width
mobile overlay does not leave inaccessible page state
```

### Dashboard

```text
KPI grid redistributes without shrinking into illegibility
activity list keeps essential information
attention panel remains usable
no false-green copy appears
handoff CTA remains reachable
```

### Funcionários

```text
summary cards remain legible
search + filters remain operable
wide table preserves essential columns
table-to-card transformation occurs without intermediate broken range
FILTER_NO_RESULTS visually distinct from EMPTY_DATASET
row actions remain reachable without horizontal trap
```

### Novo Funcionário

```text
HorizontalStepper remains understandable
360 -> Etapa X de 8 + Ver etapas
ContextDrawer overlay usable
form 1-3 columns according to real space
StickyFormActions remain reachable
keyboard/virtual-keyboard safe area does not hide primary action
ErrorSummary remains visible/reachable
EntityPicker popover/list does not overflow viewport
```

---

## 5. Acessibilidade e interação — N3

### Ordem e foco

```text
READING_ORDER = FOCUS_ORDER = TASK_LOGIC
VISIBLE_FOCUS=REQUIRED
```

Validar manualmente:

- navegação completa sem mouse;
- foco não entra em elemento oculto/inert;
- foco retorna ao trigger após drawer/modal;
- troca de etapa move foco ao heading previsto;
- ErrorSummary recebe foco quando necessário;
- primeiro erro é alcançável e associado;
- abrir overlay não cria escape de foco indevido;
- fechar overlay não perde a origem.

### Teclado obrigatório

```text
AppShell/sidebar
HorizontalStepper
Ver etapas
search
filters
row actions
ContextDrawer
EntityPicker
wizard navigation
StickyFormActions
critical recovery actions
CameraPanel demo controls when present
```

EntityPicker:

```text
Tab   entra/sai
↑ ↓   percorre
Enter seleciona
Esc   fecha
texto pesquisa
```

### Semântica

Verificar:

```text
labels persistentes
aria-current
aria-expanded
aria-controls
aria-describedby
landmarks
accessible names
required/optional semantics
state text not color-only
reduced motion contract
```

### Screen reader

```text
SCREEN_READER_MANUAL_TEST=REQUIRED_IN_N3
```

Cobertura mínima da jornada crítica:

```text
Dashboard
→ atenção biometria pendente
→ Funcionários filtrados
→ Novo funcionário
→ navegar etapas
→ abrir/fechar ContextDrawer
→ provocar erro de etapa
→ ouvir ErrorSummary
→ retornar à lista
```

Se a ferramenta necessária não estiver disponível na sessão de N3:

```text
RESULT=BLOCKED_TOOLING
PASS_MUST_NOT_BE_INFERRED
```

### Scan automatizado de acessibilidade

```text
AUTOMATED_A11Y_SCAN=PLANNED_FOR_N3_IF_TOOLING_AVAILABLE
```

Regra de aceite:

```text
CRITICAL=0
SERIOUS=0
```

Ocorrências moderadas/menores devem ser registradas, classificadas e encaminhadas; não podem ser silenciosamente ignoradas.

---

## 6. Estados obrigatórios — N3

### Dashboard

```text
MetricCard:
LOADING | EMPTY | ERROR | OFFLINE | NO_PERMISSION | TELEMETRY_UNAVAILABLE | READY/WARNING

Activity:
LOADING | EMPTY | ERROR | OFFLINE | NO_PERMISSION | READY

Attention:
WARNING / explicit no-source policy
FALSE_GREEN=PROHIBITED
```

### Funcionários

```text
LOADING
EMPTY_DATASET
READY
FILTER_NO_RESULTS
ERROR
OFFLINE
NO_PERMISSION
```

Validar que:

```text
FILTER_NO_RESULTS != EMPTY_DATASET
EMPTY_DATASET != ERROR
OFFLINE != ERROR
NO_PERMISSION removes restricted content/affordances
```

### Novo Funcionário

Runtime:

```text
READY
PERMISSION_ERROR
OFFLINE
CONFLICT
SAVE_ERROR
SUBMIT_OUTCOME_UNKNOWN
```

Etapas:

```text
FUTURE
CURRENT
VALID/COMPLETED
ERROR
NEEDS_REVIEW
```

Conditional data:

```text
VISIBLE_ACTIVE
HIDDEN_RETAINED
CLEARED
```

Verificar que dado `HIDDEN_RETAINED` não aparece como payload ativo.

### Toast

Toast pode ser suplementar para sucesso transitório, mas não pode ser a única superfície para:

```text
CONFLICT
PERMISSION_ERROR
OFFLINE_PERSISTENT
SUBMIT_OUTCOME_UNKNOWN
CRITICAL_ERROR
```

---

## 7. Matriz RBAC visual — N3

O backend continua autoridade; esta matriz valida apenas affordances do Design Lab.

| Perfil | Funcionários | Criar funcionário | Biometria | Consultar registros | Shell admin |
|---|---|---|---|---|---|
| `super_admin` | ver | ação | ação | ação/futuro UI | sim |
| `admin` | ver | ação | ação | ação/futuro UI | sim |
| `manager` | ver | ação | ocultar | ação/futuro UI | sim |
| `auditor` | ver | ocultar | ocultar | ação/futuro UI | sim, leitura |
| `operator` | ocultar | ocultar | ocultar | ocultar | não |

Casos mínimos:

```text
manager -> consegue iniciar criação, não recebe CTA biométrico proibido
auditor -> lista em leitura, sem mutações
operator -> não recebe superfície admin por punch:create
403/unexpected -> NO_PERMISSION sem vazamento
forbidden action -> hidden, not disabled substitute
```

---

## 8. Fluxos cross-screen — N2/N3

### N-F1 — Dashboard → Funcionários

```text
Dashboard
→ Ver funcionários filtrados
→ 03.01-funcionarios.html?biometric=missing&source=dashboard
→ biometric=missing aplicado
→ 2 resultados da amostra compartilhada
```

### N-F2 — estado de lista

```text
Funcionários
→ aplicar busca/filtro
→ entrar em Novo funcionário
→ retornar
→ estado anterior reutilizado na mesma sessão
```

### N-F3 — query explícita

```text
estado salvo em sessionStorage
+
query explícita recebida
→ query explícita prevalece
```

### N-F4 — contexto/principal

```text
Dashboard
→ Funcionários
→ Novo funcionário
```

Deve preservar visualmente:

```text
Potiguar Locações
Galpão principal
Administrador Demo
Admin
```

O override do ContextDrawer deve permanecer explicitamente demonstrativo.

### N-F5 — conclusão demo

Concluir o onboarding no Design Lab:

```text
MUST_NOT_MUTATE_REAL_EMPLOYEE_LIST
MUST_NOT_CLAIM_BACKEND_PERSISTENCE
MUST_EXPLAIN_DEMO_RESULT
```

---

## 9. Contrato de evidência

Cada caso executado em N2/N3 deverá gerar um registro com:

```text
CASE_ID
SURFACE
VIEWPORT_OR_CONTAINER
ZOOM
PROFILE
STATE
PRECONDITION
ACTION
EXPECTED
ACTUAL
RESULT=PASS|FAIL|BLOCKED_TOOLING|NOT_APPLICABLE
SEVERITY_IF_FAIL
EVIDENCE_REF
FOLLOW_UP_REF
```

Diretório reservado para evidências futuras:

```text
docs/nf-01/evidence/phase-n/
```

N1 não cria screenshots nem declara evidência que ainda não existe.

Convenção sugerida:

```text
N2-<surface>-<viewport>-<case>.<ext>
N3-<surface>-<profile>-<case>.<ext>
```

---

## 10. Classificação de falhas

### BLOCKER

- fluxo primário impossível;
- ação necessária inacessível por teclado;
- vazamento de conteúdo/ação por RBAC;
- perda silenciosa de dados do draft;
- navegação cross-screen principal quebrada;
- overlay prende o usuário sem saída;
- overflow/clipping impede concluir tarefa;
- false-green em estado operacional.

### HIGH

- quebra visual severa sem impedir 100% da tarefa;
- foco retorna ao lugar errado e causa perda de contexto;
- estado crítico não persistente/sem recuperação;
- stepper/drawer/entity picker inacessível em parte relevante;
- discrepância de contexto/principal entre telas.

### MEDIUM

- inconsistência de espaçamento/reflow com workaround simples;
- texto secundário cortado sem perda da ação;
- semântica acessível incompleta de baixa exposição;
- regressão de microcopy/feedback não crítica.

### LOW

- refinamento cosmético sem impacto de tarefa, segurança ou entendimento.

---

## 11. Regra de gate da Fase N

N2/N3 não podem produzir falso verde.

Para fechar N4:

```text
OPEN_BLOCKER=0
OPEN_HIGH=0
BROWSER_VISUAL_MATRIX_360_768_1024_1440=PASS
INTERMEDIATE_WIDTH_VISUAL_TEST=PASS
ZOOM_200_MANUAL_TEST=PASS
KEYBOARD_CRITICAL_JOURNEY=PASS
SCREEN_READER_CRITICAL_JOURNEY=PASS_OR_EXPLICIT_BLOCKED_WITHOUT_CLOSEOUT
RBAC_VISUAL_MATRIX=PASS
CROSS_SCREEN_CRITICAL_FLOWS=PASS
FALSE_GREEN_CHECK=PASS
SILENT_DATA_LOSS_CHECK=PASS
```

Se o scan automatizado de acessibilidade for executável:

```text
ACCESSIBILITY_CRITICAL=0
ACCESSIBILITY_SERIOUS=0
```

Se uma ferramenta necessária estiver indisponível, o caso fica `BLOCKED_TOOLING`; N4 não pode convertê-lo em PASS por inferência.

---

## 12. Testes unitários e de integração — limite canônico da NF-01

O contrato canônico de `09_TEST_AND_ACCEPTANCE_STRATEGY.md` permanece:

```text
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

Portanto N1 **não** redefine esses itens como testes que precisam ser implementados e executados dentro da NF-01.

Na Fase N será validado:

```text
UNIT_TEST_CONTRACT_COVERAGE=REVIEWED
INTEGRATION_TEST_CONTRACT_COVERAGE=REVIEWED
EXISTING_REPOSITORY_CI=OBSERVED_SEPARATELY
```

Não será declarado:

```text
NEW_DESIGN_UNIT_TESTS=PASS
NEW_DESIGN_INTEGRATION_TESTS=PASS
PRODUCTION_E2E=PASS
```

Os testes futuros especificados em J/K/L/M e no documento 09 continuam requisitos da implementação posterior.

---

## 13. Decomposição aprovada da Fase N

```text
N1_DESIGN_LAB_VALIDATION_DEFINITION=COMPLETE

N2_BROWSER_RESPONSIVE_VISUAL_VALIDATION=NEXT_GATE_NOT_APPROVED
  - 360/768/1024/1440
  - 480/900/1280 intermediários
  - container-first
  - zoom/reflow 200%
  - cross-screen visual/handoff

N3_ACCESSIBILITY_INTERACTION_STATE_RBAC_VALIDATION=NOT_APPROVED
  - keyboard
  - focus
  - screen reader
  - a11y scan if tooling available
  - states
  - RBAC
  - critical cross-screen interaction

N4_PHASE_N_CONSOLIDATED_ACCEPTANCE=NOT_APPROVED
  - consolidate evidence
  - classify residual failures
  - close Phase N only if gate criteria met
```

---

## 14. Próximo gate

```text
NEXT_OFFICIAL_PHASE=N_DESIGN_LAB_VALIDATION
NEXT_OFFICIAL_ITEM=N2_BROWSER_RESPONSIVE_VISUAL_VALIDATION_GATE
N2_APPROVAL_INFERRED=NO
```

---

## 15. Invariantes

```text
app/**=UNCHANGED
templates/**=UNCHANGED
static/**=UNCHANGED
migrations/**=UNCHANGED
DECISOES_CONGELADAS.md=UNCHANGED
backend/routes=UNCHANGED
NF02=NOT_STARTED
Ponto_to_AttendanceEvent=NOT_EXECUTED
AI=NOT_IMPLEMENTED
OBSERVABILITY_BACKEND=NOT_IMPLEMENTED
DEPLOY=NO
PRODUCTION_HOMOLOGATION=NO
LEGAL_CONFORMITY_DECLARED=NO
FINAL_HUMAN_GATE=NOT_READY
PR_MERGE=BLOCKED_UNTIL_EXPLICIT_APPROVAL
```
