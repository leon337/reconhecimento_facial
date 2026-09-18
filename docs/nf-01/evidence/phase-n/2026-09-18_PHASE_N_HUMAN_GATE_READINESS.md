# NF-01 — Fase N — Human Gate Readiness

**Data:** 2026-09-18  
**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**PR:** #32 — NF-01 — Produto + Design System  
**Branch:** `docs/nf-01-produto-design-system`  
**Autoridade humana:** LEANDRO

## Estado de prontidão

A linha técnica da Fase N foi executada até o limite permitido pelo contrato N1.

```text
PHASE_N_TECHNICAL_WORK=COMPLETE_TO_TOOLING_LIMIT
HUMAN_GATE_READY=YES
N3_REAL_ORCA_HUMAN_DIRECTED=PASS
PHASE_N_CLOSEOUT=BLOCKED_ON_H1_ONLY
PHASE_O_START_ALLOWED=NO
PR_MERGE_AUTHORIZED=NO
NF02_START_ALLOWED=NO
```

Nenhum PASS manual é inferido a partir de automação.

## Head validado antes deste registro

```text
HEAD=9ec47029d337a467e0617aa8da093a0e8ce63241
PR_STATE=OPEN
PR_MERGED=FALSE
PR_MERGEABLE=TRUE
```

Checks desse head:

```text
NF01_PHASE_N_VALIDATION_RUN=41
NF01_PHASE_N_VALIDATION=SUCCESS

PRODUCTION_VALIDATION_RUN=440
PRODUCTION_VALIDATION=SUCCESS

CI_RUN=587
CI=SUCCESS
```

## Evidência GUI assistida em nuvem

A oficina gráfica em nuvem foi estabilizada com Chromium headed, Xvfb/Openbox, Playwright, xdotool, AT-SPI e Orca.

Última execução focada em Orca:

```text
WORKFLOW=NF01 Phase N Cloud GUI Evidence
RUN_ID=35303797982
RUN_NUMBER=13
HEAD=7b169cf8ec4e1f3f4b9d85bf253cbc174be131fd
CONCLUSION=SUCCESS
ARTIFACT_ID=10530942116
ARTIFACT_DIGEST=sha256:ec18b1ee79f0a4f6ef8e3c62cec080e3baf581a131647f1e1bf580894590e3b0
```

A evidência anterior já confirmou em navegador gráfico:

```text
ZOOM_RATIO≈2.01
DEVICE_PIXEL_RATIO=2
NO_UNINTENDED_HORIZONTAL_OVERFLOW=PASS_ASSISTED
DASHBOARD_TO_EMPLOYEES=PASS_ASSISTED
STEP_LIST_OPEN=PASS_ASSISTED
CONTEXT_DRAWER_OPEN_CLOSE=PASS_ASSISTED
FOCUS_RETURN=PASS_ASSISTED
ERROR_SUMMARY=PASS_ASSISTED
RETURN_TO_EMPLOYEES=PASS_ASSISTED
```

## Resultado da investigação Orca

A infraestrutura AT-SPI consegue localizar e focar elementos reais da página.

Casos observados:

```text
Dashboard link -> grabFocus=true / focused_after=true
Novo funcionário link -> grabFocus=true / focused_after=true
Ver etapas button -> grabFocus=true / focused_after=true
Resumo button -> grabFocus=true / focused_after=true
```

Mesmo após:

- forçar acessibilidade no navegador;
- iniciar Orca com speech habilitado;
- retirar o alerta de tradução do Chrome;
- fixar idioma `pt-BR`;
- transferir foco via F6;
- transferir foco diretamente via AT-SPI;
- gerar pulso nativo Tab → Shift+Tab;

a fala do Orca na sessão hospedada não acompanhou a jornada web.

A última coleta de fala registrou apenas o chrome inicial do navegador, sem os cinco anúncios esperados da jornada.

```text
ORCA_CLOUD_SCREEN_READER_GATE=INCONCLUSIVE
ALL_EXPECTED_ANNOUNCEMENTS_FOUND=FALSE
PASS_MUST_NOT_BE_INFERRED
```

Isto é classificado como limitação da evidência assistida na sessão hospedada, não como defeito confirmado do produto.

## Auditoria do delta técnico

Comparação `04d9e6c...9ec4702`:

```text
AHEAD_BY=9
BEHIND_BY=0
```

Arquivos alterados nesse intervalo:

```text
.github/scripts/nf01-cloud-gui.mjs
.github/scripts/nf01-orca-atspi-focus.py
.github/workflows/nf01-phase-n-cloud-gui.yml
docs/nf-01/evidence/phase-n/2026-09-18_PHASE_N_MINIMAL_HUMAN_GATE.md
```

Logo:

```text
app/**=UNCHANGED_BY_THIS_INTERVAL
templates/**=UNCHANGED_BY_THIS_INTERVAL
static/**=UNCHANGED_BY_THIS_INTERVAL
migrations/**=UNCHANGED_BY_THIS_INTERVAL
backend/routes=UNCHANGED_BY_THIS_INTERVAL
PRODUCTION_PRODUCT_CODE_CHANGE=NO
```

## Testes

Os checks existentes do repositório foram executados e ficaram verdes no head acima.

O limite canônico da NF-01 permanece:

```text
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

A Fase N não redefine esses contratos como PASS.

## Human Gate obrigatório

O resultado humano de leitor de tela foi fechado por evidência real de Orca:

```text
N3_MANUAL_SCREEN_READER_CRITICAL_JOURNEY=PASS
EVIDENCE=docs/nf-01/evidence/phase-n/2026-09-18_N3_REAL_ORCA_HUMAN_DIRECTED_EVIDENCE.md
```

Resta exatamente um resultado humano a registrar.

### H1 — Zoom real 200%

Evidência técnica preparada:
`docs/nf-01/evidence/phase-n/2026-09-18_H1_ZOOM200_TECHNICAL_EVIDENCE.md`

```text
N2_MANUAL_BROWSER_ZOOM_200=PASS|FAIL
```

Usar o roteiro:
`docs/nf-01/evidence/phase-n/2026-09-18_PHASE_N_MINIMAL_HUMAN_GATE.md`

## Regra de saída

Somente se H1 for PASS, mantendo N3=PASS, com `OPEN_BLOCKER=0` e `OPEN_HIGH=0`, N4 poderá ser reconciliado para fechamento da Fase N.

Até a decisão humana:

```text
PHASE_N=IN_PROGRESS_BLOCKED_ON_MANUAL_EVIDENCE
PHASE_O=NOT_STARTED
NF02=NOT_STARTED
MERGE=NO
FINAL_HUMAN_AUTHORITY=LEANDRO
```
