# NF-01 — Fase N — N3 — Acessibilidade, interação, estados e RBAC

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-18  
**Autoridade humana:** LEANDRO

## Gate e estado

```text
N3_ACCESSIBILITY_INTERACTION_STATE_RBAC_VALIDATION=AUTHORIZED_BY_LEANDRO_CHAIN_N2_TO_N4
N3_STATUS=EXECUTED
N3_AUTOMATED_ACCEPTANCE=PASS_AFTER_TARGETED_FIXES_AND_RETESTS
N3_ACCEPTANCE=BLOCKED_TOOLING
PHASE_N_DESIGN_LAB_VALIDATION=IN_PROGRESS

AUTOMATED_FAIL_FINAL=0
MANUAL_SCREEN_READER_CRITICAL_JOURNEY=BLOCKED_TOOLING
PRODUCTION_CHANGE=NO
BACKEND_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

---

## 1. Cobertura executada

```text
AXE_CORE=EXECUTED
AXE_VIEWPORTS=360|1440
KEYBOARD_STEPPER=EXECUTED
KEYBOARD_CONTEXT_DRAWER=EXECUTED
KEYBOARD_ENTITY_PICKER=EXECUTED_AND_RETESTED
ARIA_TREE_SNAPSHOT=CAPTURED
RBAC_VISUAL_MATRIX=EXECUTED
EMPLOYEE_STATE_MATRIX=EXECUTED
MANUAL_SCREEN_READER=BLOCKED_TOOLING
```

Superfícies axe:

```text
AppShell
Dashboard
Funcionários
Novo Funcionário
```

Critério automatizado:

```text
CRITICAL=0
SERIOUS=0
```

após as correções e retestes focados.

---

## 2. RBAC visual validado

Perfis exercitados:

```text
super_admin
admin
manager
auditor
operator
```

Resultado final:

```text
super_admin -> lista + criar + biometria................ PASS
admin       -> lista + criar + biometria................ PASS
manager     -> lista + criar; biometria oculta.......... PASS
auditor     -> lista leitura; criar/biometria ocultos... PASS
operator    -> NO_PERMISSION; shell/lista admin negados. PASS_SOURCE_VARIANT
```

A validação continua sendo visual do Design Lab; o backend permanece autoridade real.

---

## 3. Estados de Funcionários

Estados exercitados:

```text
LOADING
EMPTY_DATASET
ERROR
OFFLINE
NO_PERMISSION
```

Além do READY e FILTER_NO_RESULTS exercitados pelos fluxos normais.

Resultado:

```text
PERSISTENT_STATE_SURFACES=PASS_AUTOMATED
FILTER_NO_RESULTS != EMPTY_DATASET=PASS_PRESERVED
OFFLINE != ERROR=PASS_PRESERVED
NO_PERMISSION=PASS_AUTOMATED
```

---

## 4. Teclado e semântica do onboarding

```text
VER_ETAPAS_KEYBOARD=PASS
CONTEXT_DRAWER_KEYBOARD_OPEN=PASS
CONTEXT_DRAWER_ESCAPE_CLOSE=PASS
CONTEXT_DRAWER_FOCUS_RETURN=PASS_BY_COMPONENT_BEHAVIOR
ENTITY_PICKER_ARROW_DOWN=PASS_RETEST
ENTITY_PICKER_ESCAPE=PASS_RETEST
ENTITY_PICKER_FOCUS_PRESERVED=PASS_RETEST
ARIA_SNAPSHOT=CAPTURED
```

O primeiro caso de EntityPicker do harness apontou FAIL porque selecionava um combobox gerado numa etapa ainda oculta. O reteste restaurou um draft demonstrativo diretamente na etapa Vínculo e validou os seis EntityPickers visíveis:

```text
visiblePickers=6
expandedAfterArrow=true
expandedAfterEscape=false
focusedAfterEscape=true
RESULT=PASS
```

O falso positivo anterior foi marcado como caso supersedido; não é usado como defeito de produto.

---

## 5. Defeitos reais encontrados e corrigidos em N3

### N3-F1 — `hidden` visualmente ignorado

Sintoma:

- manager/auditor ainda viam ações biométricas;
- auditor/operator ainda podiam ver CTA de criação;
- painéis e etapas marcados `hidden` podiam aparecer.

Causa:

```text
HTML hidden=true
+
author CSS display:flex/grid/inline-flex
→ comportamento visual de hidden sobrescrito
```

Correção:

```text
COMMIT=8ceab55c56f40afb036bdf8eb42a78736d068d2a
DESIGN_LAB_HIDDEN_CONTRACT='[hidden] { display:none !important; }'
```

Após a correção, a matriz RBAC passou nos cinco perfis.

### N3-F2 — contraste de `Conta:` em Funcionários

Axe detectou seis ocorrências:

```text
foreground=#6e7b75
background=#ffffff
ratio=4.41:1
font=12px normal
required=4.5:1
```

Correção:

```text
COMMIT=dbcafef6b8007cd6680705ecc41980355df4f6a8
employee-account -> var(--text-secondary)
```

Reteste:

```text
N3-EMPLOYEES-360-AXE-RETEST=PASS
critical/serious=[]
```

---

## 6. Evidência final

```text
WORKFLOW=NF01 Phase N Validation
RUN_ID=32125796830
RUN_NUMBER=17
HEAD=c1a1db3e9f0c944e522813c475ba29b8758b4ec6
CONCLUSION=SUCCESS
ARTIFACT_ID=9320310859
ARTIFACT_DIGEST=sha256:02d952de8c294d0c5d5cca38c316b79120bade246f7c07eb411a083b9903ecfa
```

Resumo durável:

`docs/nf-01/evidence/phase-n/2026-08-18_N2_N3_AUTOMATED_VALIDATION_SUMMARY.json`

Resumo da matriz base e retestes:

```text
BASE_PASS=55
BASE_FAIL=1_FALSE_POSITIVE_SUPERSEDED
BASE_BLOCKED_TOOLING=2
FOCUSED_RETESTS=2_PASS
FINAL_AUTOMATED_FAIL=0
```

---

## 7. Bloqueio de ferramenta preservado

N1 exige jornada manual com leitor de tela real.

O runner oferece:

```text
axe-core
Chromium accessibility tree / ARIA snapshot
keyboard automation
```

mas não oferece sessão manual real com:

```text
NVDA | JAWS | VoiceOver | Orca
```

Logo:

```text
N3_MANUAL_SCREEN_READER_CRITICAL_JOURNEY=BLOCKED_TOOLING
PASS_MUST_NOT_BE_INFERRED
N3_ACCEPTANCE=BLOCKED_TOOLING
```

---

## 8. Limite dos testes automatizados canônicos

Esta automação é homologação browser/a11y do Design Lab e não altera o contrato:

```text
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

---

## 9. Continuidade automática autorizada

```text
N3 EXECUTED
↓
N4 PHASE_N_CONSOLIDATED_ACCEPTANCE
AUTHORIZED_IN_SAME_HUMAN_GATE_CHAIN
```
