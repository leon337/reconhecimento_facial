# NF-01 — Fase M — M2 — Reconciliação de coerência entre telas

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-18  
**Autoridade humana:** LEANDRO

## Gate e estado

```text
M2_CROSS_SCREEN_COHERENCE_RECONCILIATION=APPROVED_BY_LEANDRO
M2_STATUS=COMPLETE
M2_ACCEPTANCE=PASS_SOURCE_LEVEL
PHASE_M_CROSS_SCREEN_COHERENCE=IN_PROGRESS
M1_HIGH_GAPS_RECONCILED_SOURCE_LEVEL=5/5

IMPLEMENTATION=DESIGN_LAB_ONLY
DASHBOARD_HTML_CHANGED_IN_M2=YES
EMPLOYEES_HTML_CHANGED_IN_M2=NO
EMPLOYEES_JS_CHANGED_IN_M2=YES
ONBOARDING_HTML_CHANGED_IN_M2=NO
ONBOARDING_JS_CHANGED_IN_M2=NO
SHARED_INTERACTIONS_CHANGED_IN_M2=YES
APPSHELL_CHANGED_IN_M2=NO
PRODUCTION_CHANGE=NO
PHASE_N=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate foi consumida somente para M2. Nenhuma autorização de M3, Fase N, NF-02, produção, deploy ou merge é inferida.

---

## 1. Objetivo

Implementar a reconciliação cruzada derivada de M1 sem reabrir os fechamentos locais de Dashboard, Funcionários ou Novo Funcionário.

Linha de montagem reconciliada:

```text
Dashboard
   ↓ handoff real + filtro
Funcionários
   ↓ preserva estado da lista
Novo funcionário
   ↓ retorno à mesma sessão de lista
Funcionários
```

---

## 2. Arquivos alterados

```text
docs/nf-01/prototype/screens/02.01-dashboard.html
docs/nf-01/prototype/assets/employees-v1.js
docs/nf-01/prototype/assets/interactions.js
```

Nenhum arquivo de produção, backend, AppShell, migrations ou NF-02 foi alterado.

---

## 3. Resultado dos cinco temas HIGH de M1

```text
M1-H1 identidade das fixtures divergia entre telas................. CLOSED_SOURCE_LEVEL
M1-H2 contexto/unidade não permanecia coerente...................... CLOSED_SOURCE_LEVEL
M1-H3 proveniência das fixtures era ambígua......................... CLOSED_SOURCE_LEVEL
M1-H4 Dashboard -> Funcionários não realizava handoff real.......... CLOSED_SOURCE_LEVEL
M1-H5 principal/permissões mudavam silenciosamente no onboarding.... CLOSED_SOURCE_LEVEL
```

### M1-H1 — identidade compartilhada

Dashboard agora usa as mesmas matrículas da lista de Funcionários:

```text
Maria Silva  -> 00123
João Souza   -> 00124
Lucas Santos -> 00131
Ana Paula    -> 00142
```

M2 não cria backend de fixture nem novo cadastro mestre. A coerência é explicitamente de Design Lab.

### M1-H2 — contexto operacional

O contexto demonstrativo compartilhado é:

```text
EMPRESA=Potiguar Locações
APP_CONTEXT=Galpão principal · contexto demonstrativo
PROFILE=Administrador Demo
ROLE=Admin · perfil fictício
```

As quatro linhas de atividade do Dashboard usam `Galpão principal` para não confundir unidade base da fixture com alocação temporária não modelada nesta amostra.

`interactions.js` também normaliza o contexto visível e o `aria-label` do seletor de contexto quando a tela já montou o AppShell, caso do onboarding.

### M1-H3 — proveniência

Dashboard deixou de apresentar `24` como se viesse da coleção local de Funcionários.

Contrato M2:

```text
DASHBOARD_EMPLOYEE_COUNT=6
DASHBOARD_EMPLOYEE_SOURCE=fixture:employees-k2
EMPLOYEES_DATASET_COUNT=6
EMPLOYEES_DATASET_SOURCE=fixture:employees-k2
DASHBOARD_BIOMETRIC_PENDING=2
EMPLOYEES_BIOMETRIC_PENDING=2_DERIVED_FROM_SAME_SAMPLE
```

`Registros hoje=37` continua sendo fixture independente de registros e permanece explicitamente identificado como tal.

### M1-H4 — handoff Dashboard -> Funcionários

A atenção de biometria pendente agora é navegação real dentro do Design Lab:

```text
03.01-funcionarios.html?biometric=missing&source=dashboard
```

`employees-v1.js` lê o handoff e aplica o filtro `missing` antes de renderizar o resultado.

O fluxo esperado é:

```text
Dashboard
→ 2 biometrias pendentes
→ Ver funcionários filtrados
→ Funcionários
→ biometric=missing
→ 2 fixtures demonstrativas
```

### M1-H5 — principal e permissões

`interactions.js` define uma sessão demonstrativa compartilhada para as três superfícies:

```text
PROFILE=Administrador Demo
ROLE=Admin · perfil fictício
PERMISSIONS=users:view users:create biometrics:manage punch:view punch:create
```

No onboarding, essa sessão é aplicada ao `data-demo-permissions` antes da inicialização de `new-employee-v2.js`. O seletor de perfil do ContextDrawer permanece como **override explícito de teste**, não como mudança silenciosa de principal.

---

## 4. Temas MEDIUM reconciliados

```text
M1-M1 linguagem visível `V2`................................ RECONCILED_AT_RUNTIME
M1-M2 breadcrumb redundante do onboarding.................... RECONCILED_AT_RUNTIME
M1-M3 restauração de filtros no retorno...................... RECONCILED_SOURCE_LEVEL
M1-M4 ações sem destino real................................ PRESERVED_AS_EXPLICIT_DEMO
M1-M5 efeito da conclusão demo sobre Funcionários............ EXPLICIT_NO_LIST_MUTATION
```

### Linguagem e breadcrumb

O nome técnico do arquivo continua `03.04-novo-funcionario-v2.html`, mas `interactions.js` normaliza a linguagem visível para `Novo Funcionário` e remove o primeiro nível redundante `Gestão` do breadcrumb do onboarding.

### Estado da lista

Funcionários mantém busca/filtros em `sessionStorage` com chave escopada ao contexto demonstrativo:

```text
cpp:nf01:employees:list-state:v1:potiguar-locacoes:galpao-principal
```

Um handoff explícito por query string possui precedência sobre estado restaurado. Ao voltar do onboarding, o estado anterior da lista é reutilizado na mesma sessão.

### Conclusão demonstrativa

O painel de sucesso do onboarding agora declara em runtime que a demonstração **não altera a lista de Funcionários**. Persistência real continua fora da NF-01.

---

## 5. Verificação source-level

```text
DASHBOARD_EMPLOYEE_COUNT_MATCHES_EMPLOYEES_SAMPLE=PASS
JOAO_REGISTRATION_MATCH=PASS
MARIA_REGISTRATION_MATCH=PASS
LUCAS_REGISTRATION_MATCH=PASS
ANA_REGISTRATION_MATCH=PASS
DASHBOARD_ACTIVITY_UNIT=GALPAO_PRINCIPAL
SHARED_EMPLOYEE_SOURCE=fixture:employees-k2
DASHBOARD_TO_EMPLOYEES_REAL_HREF=PASS
HANDOFF_BIOMETRIC_QUERY=missing
EMPLOYEES_QUERY_PARSER=PASS_SOURCE_LEVEL
EMPLOYEES_SESSION_FILTER_RESTORE=PASS_SOURCE_LEVEL
ONBOARDING_SHARED_CONTEXT_SYNC=PASS_SOURCE_LEVEL
ONBOARDING_SHARED_PRINCIPAL_SYNC=PASS_SOURCE_LEVEL
ONBOARDING_VISIBLE_V2_REMOVAL=PASS_RUNTIME_CONTRACT
ONBOARDING_BREADCRUMB_DEDUP=PASS_RUNTIME_CONTRACT
ONBOARDING_DEMO_LIST_MUTATION=EXPLICIT_NO
```

O job principal `tests` do CI do commit de implementação M2 concluiu com sucesso, incluindo `Verificar sintaxe` e `Executar testes`. Isso não equivale aos testes específicos de Design Lab, que permanecem diferidos.

---

## 6. Limites

```text
M2_PASS_SOURCE_LEVEL != FULL_CROSS_SCREEN_ACCEPTANCE
M2_PASS_SOURCE_LEVEL != FULL_VISUAL_ACCEPTANCE
M2_PASS_SOURCE_LEVEL != PRODUCTION_READY

BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
INTERMEDIATE_WIDTH_VISUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
SCREEN_READER_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

Ainda permanecem fora da NF-01:

```text
REAL_EMPLOYEE_PERSISTENCE=NO
REMOTE_ENTITY_PICKER=NO
REAL_BIOMETRIC_CAPTURE_OR_STORAGE=NO
RUNTIME_BACKEND_RBAC=NO
REAL_RECORDS_SURFACE=NO
REAL_HEALTH_SURFACE=NO
```

---

## 7. Testes futuros derivados/preservados

### Unitários

- handoff `biometric=missing` aplica somente filtro permitido;
- query explícita prevalece sobre sessão restaurada;
- estado de filtro é escopado ao contexto;
- mesma pessoa não possui matrículas divergentes entre fixtures compartilhadas;
- principal demonstrativo não perde permissões na navegação normal;
- override do ContextDrawer é explícito e reversível.

### Integração

```text
Dashboard
→ Ver funcionários filtrados
→ Funcionários
→ biometric=missing
→ 2 resultados
```

```text
Funcionários com filtros
→ Novo funcionário
→ Salvar e sair / Voltar
→ Funcionários
→ estado anterior restaurado
```

```text
Admin no Dashboard
→ Funcionários
→ Novo funcionário
→ mesmo app context
→ mesmo principal demonstrativo
```

Esses testes específicos foram definidos, não executados em M2.

---

## 8. Próximo gate

```text
NEXT_OFFICIAL_PHASE=M_CROSS_SCREEN_COHERENCE
NEXT_OFFICIAL_ITEM=M3_CROSS_SCREEN_POST_RECONCILIATION_ACCEPTANCE_GATE
M3_APPROVAL_INFERRED=NO
```

M3 deve reauditar o resultado cruzado e decidir se a Fase M pode ser encerrada em base source-level.

---

## 9. Continuidade documental

O checkpoint 65 registrou M1 e este checkpoint 66 registra M2. O `13_NF01_REMAINING_WORK_ROADMAP.md` ainda precisa ser sincronizado com M1/M2; enquanto isso, checkpoint 66 + corpo do PR são a continuidade mais recente da Fase M. Essa dívida documental não altera o source do Design Lab, mas deve ser eliminada no próximo gate.

---

## 10. Invariantes

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
