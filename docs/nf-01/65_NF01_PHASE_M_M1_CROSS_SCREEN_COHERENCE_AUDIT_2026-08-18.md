# NF-01 — Fase M — M1 — Auditoria de coerência entre telas

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-18  
**Autoridade humana:** LEANDRO

## Gate e estado

```text
M1_CROSS_SCREEN_COHERENCE_AUDIT=APPROVED_BY_LEANDRO
M1_STATUS=COMPLETE
M1_AUDIT_RESULT=GAPS_FOUND
PHASE_M_CROSS_SCREEN_COHERENCE=IN_PROGRESS
IMPLEMENTATION=DOCUMENTAL_AUDIT_ONLY
CROSS_SCREEN_VISUAL_CHANGE_IN_M1=NO
DASHBOARD_SOURCE_CHANGED_IN_M1=NO
EMPLOYEES_SOURCE_CHANGED_IN_M1=NO
ONBOARDING_SOURCE_CHANGED_IN_M1=NO
APPSHELL_CHANGED_IN_M1=NO
PRODUCTION_CHANGE=NO
PHASE_N=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate foi consumida somente para M1. Nenhuma autorização de M2, Fase N, NF-02, produção, deploy ou merge é inferida.

---

## 1. Objetivo

Auditar Dashboard, Funcionários e Novo Funcionário V2 como um único produto, após os fechamentos source-level de J3, K3 e L3.

M1 não redesenha telas. O objetivo é verificar se telas individualmente corretas continuam coerentes quando conectadas em uma jornada única.

A lógica é equivalente a uma linha de montagem:

```text
Dashboard
   ↓
Funcionários
   ↓
Novo funcionário
   ↓
retorno à lista
```

Cada estação pode estar correta isoladamente e ainda assim entregar uma peça incoerente se identidade, contexto, permissões, filtros ou origem dos dados mudarem durante o handoff.

---

## 2. Fontes auditadas

```text
docs/nf-01/09_TEST_AND_ACCEPTANCE_STRATEGY.md
docs/nf-01/12_NF01_CANONICAL_DECISIONS_2026-08-11.md
docs/nf-01/13_NF01_REMAINING_WORK_ROADMAP.md
docs/nf-01/58_NF01_PHASE_J_J3_DASHBOARD_POST_RECONCILIATION_ACCEPTANCE_2026-08-17.md
docs/nf-01/61_NF01_PHASE_K_K3_EMPLOYEES_POST_RECONCILIATION_ACCEPTANCE_2026-08-18.md
docs/nf-01/64_NF01_PHASE_L_L3_ONBOARDING_POST_RECONCILIATION_ACCEPTANCE_2026-08-18.md
docs/nf-01/prototype/assets/app-shell.js
docs/nf-01/prototype/screens/02.01-dashboard.html
docs/nf-01/prototype/screens/03.01-funcionarios.html
docs/nf-01/prototype/assets/employees-v1.js
docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
docs/nf-01/prototype/assets/new-employee-v2.js
```

---

## 3. Resultado executivo

```text
CRITICAL_GAPS=0
HIGH_GAP_THEMES=5
MEDIUM_GAP_THEMES=5
LOW_DEFERRED_OBSERVATIONS=3

PRESERVE_ITEMS=9
RECONCILE_ITEMS=10
DEFER_ITEMS=5

M2_IMPLEMENTATION_SCOPE_REQUIRED=YES
PRODUCTION_READY=NO
```

As três superfícies preservam o AppShell e os contratos locais fechados em J/K/L, mas a auditoria encontrou incoerências quando as fixtures e o principal demonstrativo são tratados como parte da mesma sessão.

---

# 4. Matriz de coerência Current × Cross-screen

| Área | Dashboard | Funcionários | Novo Funcionário V2 | Resultado M1 |
|---|---|---|---|---|
| AppShell | compartilhado | compartilhado | compartilhado | PRESERVE |
| item ativo | `dashboard` | `employees` | `employees` | PRESERVE |
| empresa do header | Potiguar Locações | Potiguar Locações | Potiguar Locações | PRESERVE |
| contexto do header | Galpão principal | Galpão principal | Contexto administrativo genérico | RECONCILE |
| perfil demonstrativo | Admin explícito | Admin explícito | perfil genérico | RECONCILE |
| permissões demo | conjunto completo do Admin | conjunto completo do Admin | apenas `users:create biometrics:manage` | RECONCILE |
| CTA Funcionários → Novo | — | link real para `03.04` | retorno à lista existente | PRESERVE/PARTIAL |
| Dashboard → Funcionários | botão demonstrativo | superfície existe | — | RECONCILE |
| identidade João Souza | matrícula 00123 | matrícula 00124 | — | RECONCILE HIGH |
| identidade Maria Silva | matrícula 00124 | matrícula 00123 | — | RECONCILE HIGH |
| unidade Ana Paula | Obra 02 | Galpão principal | — | RECONCILE HIGH |
| total de funcionários | 24, origem apresentada como fixture Funcionários | 6 na amostra local | — | RECONCILE HIGH |
| biometrias pendentes | 2 | 2 derivadas da amostra | — | PRESERVE_WITH_SOURCE_FIX |
| filtro de biometria | atenção “Ver funcionários” | filtro `missing` existe | — | RECONCILE HANDOFF |
| rascunho | — | — | localStorage isolado | PRESERVE |
| produção/backend | não usados | não usados | não usados | PRESERVE |

---

# 5. Gaps HIGH

## M1-H1 — identidade das mesmas pessoas diverge entre telas

Dashboard apresenta:

```text
João Souza   -> matrícula 00123
Maria Silva  -> matrícula 00124
```

Funcionários apresenta:

```text
Maria Silva  -> matrícula 00123
João Souza   -> matrícula 00124
```

Isso é uma colisão de identidade demonstrativa. Mesmo sendo fixture, o mesmo nome dentro da mesma experiência não pode trocar de matrícula entre telas.

Decisão M1:

```text
ONE_DEMO_PERSON_IDENTITY=REQUIRED
NAME_REGISTRATION_PAIR=STABLE_ACROSS_SCREENS
M2_MUST_RECONCILE=YES
```

## M1-H2 — unidade e escopo operacional não permanecem coerentes

Dashboard e Funcionários declaram no AppShell:

```text
Potiguar Locações
Galpão principal · contexto demonstrativo
```

Porém:

- Dashboard simplifica algumas linhas para `Galpão`;
- Ana Paula aparece em `Obra 02` no Dashboard e `Galpão principal` em Funcionários;
- Novo Funcionário mantém a empresa, mas troca o subtítulo do AppShell por `Contexto administrativo · demonstração`.

O teste canônico exige que o contexto do header não altere o formulário, mas isso não autoriza o contexto da sessão a desaparecer durante a navegação.

Decisão M1:

```text
APP_CONTEXT_MUST_PERSIST_ACROSS_NAVIGATION=YES
TARGET_EMPLOYEE_COMPANY_UNIT_MAY_DIFFER_FROM_APP_CONTEXT=YES
THE_TWO_CONTEXTS_MUST_BE_DISTINGUISHABLE=YES
```

## M1-H3 — origem de dados do Dashboard conflita com a amostra de Funcionários

Dashboard mostra:

```text
Funcionários cadastrados = 24
Origem: fixture Funcionários
```

Funcionários usa uma coleção local de seis fixtures e calcula:

```text
total na amostra = 6
```

Há duas possibilidades válidas, mas o estado atual não declara qual delas é verdadeira:

```text
A) ambas as telas compartilham a mesma fixture;
B) Dashboard usa uma fixture agregada independente.
```

Se A, 24 × 6 está incoerente. Se B, `Origem: fixture Funcionários` é ambígua.

Decisão M1:

```text
CROSS_SCREEN_FIXTURE_PROVENANCE_MUST_BE_UNAMBIGUOUS=YES
M2_MUST_CHOOSE_SHARED_OR_EXPLICITLY_INDEPENDENT_SOURCE=YES
```

## M1-H4 — Dashboard possui ação para uma superfície existente, mas não realiza o handoff

Em `Atenção necessária`, o Dashboard possui `Ver funcionários` para biometrias pendentes. A tela Funcionários já existe e possui filtro local de biometria.

Entretanto, a ação é um `<button>` demonstrativo sem navegação para `03.01-funcionarios.html` e sem transferência do filtro `missing`.

Decisão M1:

```text
EXISTING_TARGET_SURFACE_SHOULD_USE_REAL_DESIGN_LAB_NAVIGATION=YES
DASHBOARD_ATTENTION_TO_EMPLOYEES=RECONCILE
FILTER_HANDOFF_CONTRACT=REQUIRED
```

## M1-H5 — principal demonstrativo muda silenciosamente entre telas

Dashboard e Funcionários representam o mesmo principal demonstrativo como Admin e expõem o conjunto completo de permissões da fixture administrativa.

Novo Funcionário:

```text
profile label = Perfil fictício
data-demo-permissions = users:create biometrics:manage
```

A tela possui perfis locais para testar estados, mas a entrada normal vinda de Funcionários não deve parecer uma troca silenciosa de identidade/permissão.

Decisão M1:

```text
DEMO_SESSION_PRINCIPAL=ONE_BY_DEFAULT
ROLE_AND_PERMISSION_CONTEXT_MUST_PERSIST=YES
LOCAL_TEST_VARIANTS_MAY_OVERRIDE_ONLY_WHEN_EXPLICITLY_LABELED=YES
```

---

# 6. Gaps MEDIUM

## M1-M1 — nomenclatura técnica `V2` ainda aparece para o usuário

Funcionários chama a ação de `Novo funcionário`, mas o breadcrumb do onboarding mostra `Novo funcionário V2` e o `<title>` também expõe a versão.

`V2` pode continuar no nome do arquivo e na documentação técnica, mas não precisa fazer parte da arquitetura de informação apresentada ao usuário.

## M1-M2 — breadcrumb do onboarding possui dois ancestrais apontando para a mesma tela

Atualmente:

```text
Gestão -> 03.01-funcionarios.html
Funcionários -> 03.01-funcionarios.html
Novo funcionário V2
```

Isso não representa uma hierarquia real. M2 deve manter `Gestão` como agrupador não clicável ou apontá-lo para uma superfície real futura, sem dois links consecutivos para o mesmo destino.

## M1-M3 — filtros/pesquisa de Funcionários não possuem contrato de restauração após onboarding

A estratégia canônica prevê preservação de filtros/pesquisa conforme a navegação definida.

Hoje, Funcionários mantém filtros somente no estado do DOM. Ao entrar em Novo Funcionário e retornar, a lista reinicia no estado padrão.

M2 deve decidir explicitamente entre:

```text
URL query/state
sessionStorage
ou retorno sem preservação, se documentado como decisão
```

A opção recomendada para o Design Lab é URL/session state simples, sem backend.

## M1-M4 — ações biométricas de funcionário existente ainda não possuem superfície de destino

Funcionários oferece `Cadastrar`/`Recadastrar` biometria por pessoa. Essas ações são permission-aware, mas não existe ainda uma tela canônica de biometria de funcionário existente.

M2 não deve reaproveitar silenciosamente o onboarding de novo funcionário como se fosse edição de pessoa existente.

Enquanto não houver superfície legítima:

```text
NO_FAKE_NAVIGATION=YES
DEMO_ACTION_MUST_EXPLAIN_LIMIT=YES
```

## M1-M5 — conclusão demonstrativa do onboarding não possui contrato de efeito na lista

O onboarding informa corretamente que não envia dados ao backend, mas o fluxo de retorno à lista ainda não explicita se a fixture de Funcionários deve ou não mudar.

Para NF-01, não é necessário criar persistência real. M2 deve apenas tornar o contrato inequívoco:

```text
DEMO_COMPLETION_MUTATES_EMPLOYEE_FIXTURE=NO
ou
SHARED_LOCAL_DEMO_FIXTURE=EXPLICIT
```

Recomendação M1: manter `NO` para evitar transformar a NF-01 em uma implementação de persistência paralela.

---

# 7. Observações LOW / diferidas

```text
M1-D1 Registros continua sem superfície Design Lab real -> deferir até existir target legítimo
M1-D2 Saúde/Eventos/Configurações continuam placeholders -> fora da tríade M1
M1-D3 validação visual 360/768/1024/1440, zoom 200 e screen reader -> Fase N
```

O link para `/punch` pode continuar sendo apresentado como fluxo independente, desde que nunca seja confundido com conteúdo interno do AppShell.

---

# 8. O que M1 preserva

```text
shared AppShell
sidebar compact preference contract
Dashboard canonical KPI/state model
Employees collection/state/RBAC model
Employees -> New Employee real link
Onboarding eight-stage workflow
HorizontalStepper
ContextDrawer
StickyFormActions
NEEDS_REVIEW / ERROR hardening
Design Lab isolation
```

M1 não reabre J3, K3 ou L3. Os gaps são de **integração entre superfícies**, não regressões que invalidem os fechamentos locais.

---

# 9. Proposta de escopo M2

```text
M2_CROSS_SCREEN_COHERENCE_RECONCILIATION

PRIMARY_TARGETS
├── docs/nf-01/prototype/screens/02.01-dashboard.html
├── docs/nf-01/prototype/screens/03.01-funcionarios.html
├── docs/nf-01/prototype/assets/employees-v1.js
├── docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
└── docs/nf-01/prototype/assets/new-employee-v2.js

OPTIONAL_SHARED_DESIGN_LAB_SUBSTRATE
└── pequeno módulo compartilhado de contexto/fixtures somente se reduzir duplicação
```

Objetivos M2:

```text
1. estabilizar identidades e matrículas das fixtures compartilhadas;
2. estabilizar nomenclatura de unidades/contexto;
3. declarar fonte agregada vs coleção local sem ambiguidade;
4. tornar Dashboard -> Funcionários um handoff real quando a superfície já existe;
5. transportar/aplicar filtro de biometria pendente no handoff;
6. preservar principal/contexto demonstrativo por padrão;
7. distinguir app context de empresa/unidade escolhida para o novo vínculo;
8. remover `V2` da linguagem de usuário, mantendo versão técnica interna;
9. corrigir breadcrumb duplicado;
10. definir restauração de filtros no retorno do onboarding;
11. tornar explícito que conclusão demo não altera a lista, salvo decisão diferente aprovada;
12. manter ações sem destino real como demonstrações claramente limitadas.
```

Não faz parte de M2 sem novo gate ampliado:

```text
backend
produção
persistência real de funcionário
câmera/biometria real
novo detalhe de funcionário completo
Registros real
Saúde real
NF-02
```

---

# 10. Testes futuros derivados de M1

## Unitários

- registry de fixture não permite matrícula diferente para a mesma pessoa;
- origem agregada do Dashboard é distinguível da coleção de Funcionários;
- parser de handoff aplica `biometric=missing` sem converter erro em empty;
- principal demonstrativo não perde permissões na navegação normal;
- override de perfil de teste é explícito e reversível;
- restauração de filtros não mistura estado de outra sessão/contexto.

## Integração

```text
Dashboard
→ Ver funcionários com biometria pendente
→ Funcionários
→ filtro biometria=missing aplicado
→ 2 fixtures coerentes
```

```text
Funcionários com busca/filtro
→ Novo funcionário
→ Salvar e sair / voltar
→ Funcionários
→ estado de lista restaurado conforme contrato aprovado
```

```text
Admin no Dashboard
→ Funcionários
→ Novo funcionário
→ mesmo app context + mesmo principal demo
```

```text
app context = Galpão principal
novo vínculo = outra unidade permitida
→ header continua representando app context
→ formulário mostra target do vínculo separadamente
```

Esses testes foram derivados, não executados em M1.

---

# 11. Limites do aceite M1

```text
M1_AUDIT_COMPLETE != CROSS_SCREEN_RECONCILED
M1_AUDIT_COMPLETE != FULL_VISUAL_ACCEPTANCE
M1_AUDIT_COMPLETE != AUTOMATED_TEST_PASS
M1_AUDIT_COMPLETE != PRODUCTION_READY

NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
INTERMEDIATE_WIDTH_VISUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
SCREEN_READER_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
```

---

# 12. Próximo gate

```text
NEXT_OFFICIAL_PHASE=M_CROSS_SCREEN_COHERENCE
NEXT_OFFICIAL_ITEM=M2_CROSS_SCREEN_COHERENCE_RECONCILIATION_GATE
M2_APPROVAL_INFERRED=NO
```

M2 deve implementar somente a reconciliação cruzada aprovada após HUMAN_GATE de LEANDRO.

---

# 13. Invariantes

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
