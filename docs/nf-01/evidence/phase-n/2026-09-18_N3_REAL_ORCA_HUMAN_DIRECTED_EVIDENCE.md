# NF-01 — Fase N — N3 Real Orca Human-Directed Evidence

**Data da sessão:** 2026-09-17  
**Data da formalização:** 2026-09-18  
**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**PR:** #32 — NF-01 — Produto + Design System  
**Branch:** `docs/nf-01-produto-design-system`

## Classificação da evidência

```text
EXECUTION_TYPE=HUMAN_DIRECTED_REAL_ORCA_SESSION
PLATFORM=LINUX_X11
SCREEN_READER=ORCA_REAL
BROWSER=BRAVE
SYNTHETIC_SCREEN_READER=NO
CLOUD_ASSISTED=NO
MANUAL_ACCEPTANCE_INFERRED=NO
```

A sessão foi conduzida no notebook real, com Orca ativo e fala registrada no log de depuração. O log bruto não é versionado no repositório devido ao tamanho, mas sua integridade é registrada abaixo.

```text
RAW_LOG=/home/leo/reconhecimento_facial/docs/nf-01/evidence/phase-n/manual-2026-09-17/N3-orca-debug.log
RAW_LOG_SIZE=24719489 bytes
RAW_LOG_SHA256=9364b7771c03193acf7d140f52708e61babaea60f1e69a558ef9a6a7bc05f66b
```

## Resultado consolidado

```text
N3_MANUAL_SCREEN_READER_CRITICAL_JOURNEY=PASS
PASS_BASIS=REAL_ORCA_HUMAN_DIRECTED_EVIDENCE
```

A conclusão acima não deriva dos workers sintéticos em nuvem. Ela deriva da sessão real descrita neste documento e dos anúncios efetivamente registrados pelo Orca.

---

## N3-001 — Dashboard → atenção de biometria pendente

```text
CASE_ID=N3-001
SURFACE=Dashboard
VIEWPORT_OR_CONTAINER=REAL_DESKTOP_BROWSER
ZOOM=NOT_APPLICABLE
PROFILE=ORCA_REAL_LOCAL_X11
STATE=DASHBOARD_ATTENTION
PRECONDITION=Dashboard carregado com Orca ativo
ACTION=Navegar até a atenção de biometria pendente
EXPECTED=Leitor de tela anuncia o estado e a ação filtrada
ACTUAL=Orca anunciou "2 biometrias pendentes" e "Ver funcionários filtrados link"
RESULT=PASS
SEVERITY_IF_FAIL=HIGH
EVIDENCE_REF=RAW_LOG@16:29:12.489734-16:29:12.501218
FOLLOW_UP_REF=NONE
```

Trecho observado:

```text
16:29:12.489734 - SPEECH OUTPUT: '2 biometrias pendentes.'
16:29:12.501218 - SPEECH OUTPUT: 'Ver funcionários filtrados link.'
```

## N3-002 — Dashboard → Funcionários filtrados

```text
CASE_ID=N3-002
SURFACE=Dashboard→Funcionários
VIEWPORT_OR_CONTAINER=REAL_DESKTOP_BROWSER
ZOOM=NOT_APPLICABLE
PROFILE=ORCA_REAL_LOCAL_X11
STATE=FILTERED_EMPLOYEES
PRECONDITION=Ação "Ver funcionários filtrados" disponível
ACTION=Ativar a ação e aguardar navegação
EXPECTED=Página Funcionários carrega e é anunciada
ACTUAL=Orca anunciou carregamento de "Funcionários Canônico K2 — NF-01 Design Lab"
RESULT=PASS
SEVERITY_IF_FAIL=HIGH
EVIDENCE_REF=RAW_LOG@16:29:29.244055
FOLLOW_UP_REF=NONE
```

## N3-003 — Funcionários → Novo funcionário

```text
CASE_ID=N3-003
SURFACE=Funcionários
VIEWPORT_OR_CONTAINER=REAL_DESKTOP_BROWSER
ZOOM=NOT_APPLICABLE
PROFILE=ORCA_REAL_LOCAL_X11
STATE=EMPLOYEE_LIST
PRECONDITION=Lista de funcionários carregada
ACTION=Navegar e ativar "Novo funcionário"
EXPECTED=Link possui nome acessível e onboarding carrega
ACTUAL=Orca anunciou "Novo funcionário link" e depois "Finished loading Novo Funcionário — NF-01 Design Lab"
RESULT=PASS
SEVERITY_IF_FAIL=HIGH
EVIDENCE_REF=RAW_LOG@16:30:31.798336;RAW_LOG@16:30:58.570651
FOLLOW_UP_REF=NONE
```

## N3-004 — Stepper / Ver etapas / oito etapas

```text
CASE_ID=N3-004
SURFACE=Novo Funcionário
VIEWPORT_OR_CONTAINER=REAL_DESKTOP_BROWSER
ZOOM=NOT_APPLICABLE
PROFILE=ORCA_REAL_LOCAL_X11
STATE=STEPPER_EXPANDED
PRECONDITION=Onboarding carregado
ACTION=Abrir "Ver etapas" e percorrer a lista
EXPECTED=Controle é anunciado e as oito etapas possuem nomes compreensíveis
ACTUAL=Orca anunciou "Ver etapas", "Etapa 1 de 8" e todas as etapas 1 a 8
RESULT=PASS
SEVERITY_IF_FAIL=HIGH
EVIDENCE_REF=RAW_LOG@16:33:19.565773-16:33:25.154745
FOLLOW_UP_REF=NONE
```

Trecho condensado:

```text
Etapa 1 de 8.
Etapa 1: Tipo de relação, atual
Etapa 2: Dados pessoais, futura
Etapa 3: Endereço, futura
Etapa 4: Vínculo, futura
Etapa 5: Pagamento, futura
Etapa 6: Acesso ao sistema, futura
Etapa 7: Biometria, futura
Etapa 8: Revisão e conclusão, futura
```

## N3-005 — ContextDrawer

```text
CASE_ID=N3-005
SURFACE=Novo Funcionário
VIEWPORT_OR_CONTAINER=REAL_DESKTOP_BROWSER
ZOOM=NOT_APPLICABLE
PROFILE=ORCA_REAL_LOCAL_X11
STATE=CONTEXT_DRAWER_OPEN
PRECONDITION=Botão "Resumo" focável
ACTION=Abrir ContextDrawer
EXPECTED=Drawer e ação de fechar são anunciados
ACTUAL=Orca anunciou "complementary content Resumo e controles do Design Lab" e "Fechar resumo push button"
RESULT=PASS
SEVERITY_IF_FAIL=HIGH
EVIDENCE_REF=RAW_LOG@16:36:24.415026-16:36:24.421575
FOLLOW_UP_REF=NONE
```

## N3-006 — Fechar drawer / retorno de foco

```text
CASE_ID=N3-006
SURFACE=Novo Funcionário
VIEWPORT_OR_CONTAINER=REAL_DESKTOP_BROWSER
ZOOM=NOT_APPLICABLE
PROFILE=ORCA_REAL_LOCAL_X11
STATE=CONTEXT_DRAWER_CLOSED
PRECONDITION=ContextDrawer aberto
ACTION=Fechar drawer e retornar ao trigger
EXPECTED=Foco retorna a "Resumo"
ACTUAL=Após fechar, Orca voltou a anunciar "Resumo collapsed push button"
RESULT=PASS
SEVERITY_IF_FAIL=HIGH
EVIDENCE_REF=RAW_LOG@16:36:34.855793
FOLLOW_UP_REF=NONE
```

## N3-007 — Erro da etapa / ErrorSummary

```text
CASE_ID=N3-007
SURFACE=Novo Funcionário
VIEWPORT_OR_CONTAINER=REAL_DESKTOP_BROWSER
ZOOM=NOT_APPLICABLE
PROFILE=ORCA_REAL_LOCAL_X11
STATE=STEP_VALIDATION_ERROR
PRECONDITION=Etapa 1 sem seleção obrigatória
ACTION=Acionar continuidade sem preencher a seleção
EXPECTED=Resumo de erros e ação corretiva são anunciados
ACTUAL=Orca anunciou "Revise as informações desta etapa", "Há 1 problema(s)..." e "Selecione uma opção para continuar"
RESULT=PASS
SEVERITY_IF_FAIL=HIGH
EVIDENCE_REF=RAW_LOG@16:34:15.425223-16:34:31.485439
FOLLOW_UP_REF=NONE
```

## N3-008 — Retorno à lista

```text
CASE_ID=N3-008
SURFACE=Novo Funcionário→Funcionários
VIEWPORT_OR_CONTAINER=REAL_DESKTOP_BROWSER
ZOOM=NOT_APPLICABLE
PROFILE=ORCA_REAL_LOCAL_X11
STATE=RETURN_TO_EMPLOYEES
PRECONDITION=Onboarding ativo após validação
ACTION=Retornar à lista de funcionários
EXPECTED=Página Funcionários carrega e é anunciada
ACTUAL=Orca anunciou "Finished loading Funcionários Canônico K2 — NF-01 Design Lab"
RESULT=PASS
SEVERITY_IF_FAIL=HIGH
EVIDENCE_REF=RAW_LOG@16:37:11.837956
FOLLOW_UP_REF=NONE
```

---

## Evidência cloud complementar

Workers cloud com Chromium e Firefox foram usados apenas para reduzir risco e validar foco/interações assistidas. Eles **não são a base do PASS manual**.

A execução Firefox/Orca cloud #6 chegou até:

```text
Dashboard attention
→ Novo funcionário
→ Ver etapas
→ Resumo
→ Fechar resumo
→ Continuar
→ ErrorSummary
```

mas permaneceu inconclusiva para fala do Orca hospedado e falhou no retorno final por timeout. Portanto:

```text
CLOUD_ORCA_SCREEN_READER_GATE=INCONCLUSIVE
CLOUD_MANUAL_ACCEPTANCE_CLAIMED=NO
```

## Estado resultante

```text
N3_MANUAL_SCREEN_READER_CRITICAL_JOURNEY=PASS
N3_BLOCKED_TOOLING_HIGH=CLEARED_BY_REAL_ORCA_EVIDENCE
N2_MANUAL_BROWSER_ZOOM_200=STILL_REQUIRES_FINAL_HUMAN_GATE
PHASE_N_CLOSEOUT=BLOCKED_ON_N2_HUMAN_GATE
PHASE_O_START_ALLOWED=NO
PR_MERGE_AUTHORIZED=NO
NF02_START_ALLOWED=NO
```
