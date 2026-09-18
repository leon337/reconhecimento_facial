# NF-01 — Fase N — N2 — Validação browser, visual e responsiva

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-18  
**Autoridade humana:** LEANDRO

## Gate e estado

```text
N2_BROWSER_RESPONSIVE_VISUAL_VALIDATION=AUTHORIZED_BY_LEANDRO_CHAIN_N2_TO_N4
N2_STATUS=EXECUTED
N2_AUTOMATED_ACCEPTANCE=PASS_AFTER_TARGETED_FIXES
N2_ACCEPTANCE=BLOCKED_TOOLING
PHASE_N_DESIGN_LAB_VALIDATION=IN_PROGRESS

AUTOMATED_BROWSER_FAIL_FINAL=0
MANUAL_BROWSER_ZOOM_200=BLOCKED_TOOLING
PRODUCTION_CHANGE=NO
BACKEND_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A autorização humana cobriu N2 → N3 → N4 em sequência, sem HUMAN_GATE intermediário. Isso não autoriza produção, backend, NF-02, deploy ou merge.

---

## 1. Matriz executada

Superfícies:

```text
01.01 AppShell
02.01 Dashboard
03.01 Funcionários
03.04 Novo Funcionário
```

Viewports:

```text
CANONICAL=360|768|1024|1440
INTERMEDIATE=480|900|1280
```

Também foi executado reflow equivalente a 200% em Chromium headless:

```text
1440 physical / 720 CSS @ deviceScaleFactor=2
```

O controle real de zoom da UI do navegador em 200% não é operável no runner headless e permanece `BLOCKED_TOOLING`.

---

## 2. Evidência automatizada

Workflow dedicado:

```text
WORKFLOW=NF01 Phase N Validation
RUN_ID=32125796830
RUN_NUMBER=17
HEAD=c1a1db3e9f0c944e522813c475ba29b8758b4ec6
CONCLUSION=SUCCESS
ARTIFACT_ID=9320310859
ARTIFACT=nf01-phase-n-evidence
ARTIFACT_DIGEST=sha256:02d952de8c294d0c5d5cca38c316b79120bade246f7c07eb411a083b9903ecfa
```

Resumo durável:

`docs/nf-01/evidence/phase-n/2026-08-18_N2_N3_AUTOMATED_VALIDATION_SUMMARY.json`

---

## 3. Resultados N2

```text
ALL_ACTIVE_SURFACES_RENDERED=PASS
CANONICAL_VIEWPORTS_REFLOW=PASS_AUTOMATED
INTERMEDIATE_VIEWPORTS_REFLOW=PASS_AUTOMATED
NO_UNINTENDED_GLOBAL_HORIZONTAL_OVERFLOW=PASS_AUTOMATED
ONBOARDING_360_MOBILE_STEPPER=PASS
DASHBOARD_TO_EMPLOYEES_HANDOFF=PASS
EMPLOYEE_LIST_STATE_RESTORE=PASS
ZOOM_200_EQUIVALENT_REFLOW=PASS_AUTOMATED
MANUAL_BROWSER_ZOOM_200=BLOCKED_TOOLING
```

O handoff confirmado:

```text
Dashboard
→ biometrias pendentes
→ 03.01-funcionarios.html?biometric=missing&source=dashboard
→ filtro biometric=missing
→ 2 resultados da amostra compartilhada
```

O retorno Funcionários → Novo Funcionário → Funcionários preservou a busca local da mesma sessão.

---

## 4. Defeito BLOCKER encontrado e corrigido durante N2

Primeiro browser run mostrou Dashboard, Funcionários e onboarding quase vazios, exibindo apenas `Admin · perfil fictício`.

Causa raiz:

```text
interactions.js
→ querySelectorAll('[data-app-shell-profile-role]') global
→ <body> também possui o atributo como metadado
→ body.textContent = 'Admin · perfil fictício'
→ todo o conteúdo da página era destruído
```

Correção mínima:

```text
COMMIT=9816c44daf00cfdbcdf2c3548b1fa9fd00b1ed38
VISIBLE_SHELL_SYNC_SCOPE=[data-app-shell-root]
BODY_METADATA_PRESERVED=YES
```

A correção ficou restrita ao Design Lab compartilhado.

---

## 5. Limite de aceite de N2

N1 determinou explicitamente que `BLOCKED_TOOLING` não pode virar PASS por inferência.

Logo:

```text
N2_AUTOMATED_MATRIX=PASS
N2_MANUAL_BROWSER_ZOOM_200=BLOCKED_TOOLING
N2_ACCEPTANCE=BLOCKED_TOOLING
```

N2 foi executada integralmente até o limite das ferramentas disponíveis, mas não é declarada homologação visual manual completa.

---

## 6. Invariantes

```text
app/**=UNCHANGED
templates/**=UNCHANGED
static/**=UNCHANGED
migrations/**=UNCHANGED
DECISOES_CONGELADAS.md=UNCHANGED
backend/routes=UNCHANGED
NF02=NOT_STARTED
DEPLOY=NO
PRODUCTION_HOMOLOGATION=NO
PR_MERGE=NOT_AUTHORIZED
```

---

## 7. Continuidade automática autorizada

```text
N2 EXECUTED
↓
N3 ACCESSIBILITY_INTERACTION_STATE_RBAC_VALIDATION
AUTHORIZED_IN_SAME_HUMAN_GATE_CHAIN
```
