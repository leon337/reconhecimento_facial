# NF-01 — Fase N — Relatório de validação GUI assistida em nuvem

Data: 2026-09-17
Missão: CPP-NF-01-PRODUTO-DESIGN-SYSTEM
PR: #32 — NF-01 — Produto + Design System
Branch: `docs/nf-01-produto-design-system`
MCF: 1.1 / Classe C
Autoridade humana final: LEANDRO

## 1. Objetivo

Reduzir dependência do notebook local para a conclusão da Fase N, executando em runner hospedado uma sessão gráfica real com Chromium, Xvfb/Openbox, Playwright, `xdotool`, AT-SPI e Orca.

Este relatório registra **evidência assistida em nuvem**. Ele **não converte** os testes manuais exigidos por N1 em PASS e **não autoriza** Fase O, merge ou NF-02.

## 2. Execução canônica desta coleta

```text
WORKFLOW=NF01 Phase N Cloud GUI Evidence
RUN_ID=35270816751
RUN_NUMBER=7
VALIDATION_HEAD=f3fdf7e27dc936e8bb881aa8a536d019c905018e
WORKFLOW_CONCLUSION=SUCCESS
ARTIFACT_ID=10518349769
ARTIFACT_FILES=16
ARTIFACT_SIZE_BYTES=2754131
ARTIFACT_DIGEST=sha256:2834b3e1bbceda4c81244ea92b4a2495325bb76523735178f4cfe7e6ebde37e9
```

Ambiente do runner:

```text
OS=Ubuntu 24.04.5 LTS
BROWSER=Chrome for Testing / Chromium headed
DISPLAY=Xvfb :99
WINDOW_MANAGER=Openbox
BROWSER_CONTROL=Playwright persistent context
ZOOM_INPUT=OS-level Ctrl+plus via xdotool
ACCESSIBILITY_BUS=AT-SPI
SCREEN_READER=Orca
```

## 3. Evidência de zoom real de navegador

O workflow aplicou zoom por atalho do navegador em Chromium **headed**, não apenas emulação de viewport.

Todas as superfícies medidas registraram:

```text
outerWidth=1920
innerWidth=956
clientWidth=948
scrollWidth=948
devicePixelRatio=2
zoomRatio=2.01
horizontalOverflow=false
zoom200Signal=true
```

Superfícies cobertas:

```text
01.01-app-shell.html=EVIDENCE_CAPTURED
02.01-dashboard.html=EVIDENCE_CAPTURED
03.01-funcionarios.html=EVIDENCE_CAPTURED
03.01-funcionarios.html?biometric=missing&source=dashboard=EVIDENCE_CAPTURED
03.04-novo-funcionario-v2.html=EVIDENCE_CAPTURED
RETURN_TO_03.01-funcionarios.html=EVIDENCE_CAPTURED
```

Resultado técnico assistido:

```text
ZOOM_200_SIGNAL_ALL_SURFACES=PASS_ASSISTED
UNINTENDED_HORIZONTAL_PAGE_OVERFLOW=NOT_DETECTED
MANUAL_ZOOM_ACCEPTANCE=NOT_CLAIMED
```

## 4. Evidência visual e de interação assistida

Foram preservadas capturas de 1920x1040 para os estados principais, incluindo Dashboard, AppShell, Funcionários, Novo Funcionário, handoff filtrado, lista de etapas aberta, ContextDrawer aberto e ErrorSummary visível.

Resultados de interação:

```text
DASHBOARD_TO_EMPLOYEES=PASS_ASSISTED
  focusConfirmed=true

STEP_LIST_OPEN=PASS_ASSISTED
  ariaExpanded=true
  hidden=false
  boundingBox=768x161

CONTEXT_DRAWER_OPEN_CLOSE=PASS_ASSISTED
  hidden=false
  ariaHidden=false
  rect=325.039x474.5
  right=948.5
  viewport_clientWidth=948
  focusReturned=true

ERROR_SUMMARY=PASS_ASSISTED
  text="Revise as informações desta etapa. Selecione uma opção para continuar."
  boundingBox=768x90.796875

RETURN_TO_EMPLOYEES=PASS_ASSISTED
```

A coleta visual foi refinada para trazer estados relevantes à área visível antes da captura, evitando evidência ambígua.

## 5. Leitor de tela — resultado da nuvem

O barramento AT-SPI e o Orca iniciaram no runner. Porém, as asserções de fala esperadas para a jornada crítica **não foram produzidas** pela sessão assistida:

```text
Dashboard=false
Funcionários=false
Novo Funcionário=false
Resumo e controles do Design Lab=false
Revise as informações desta etapa=false
ALL_EXPECTED_ANNOUNCEMENTS_FOUND=false
```

O debug do Orca mostrou a aplicação Chromium e a árvore de acessibilidade ativas, mas o foco assistivo permaneceu no chrome do navegador/endereço em vez de percorrer a jornada web como um usuário real de leitor de tela.

Portanto:

```text
N3_CLOUD_ORCA_ASSISTED=INCONCLUSIVE_FOR_MANUAL_GATE
N3_MANUAL_SCREEN_READER_CRITICAL_JOURNEY=STILL_REQUIRED
PASS_MUST_NOT_BE_INFERRED
```

## 6. Relação com o contrato N1

N1 exige validação manual de zoom 200% e jornada crítica com leitor de tela. O contrato também proíbe falso verde quando a ferramenta ou a evidência manual requerida não estiver disponível.

Consequentemente, mesmo com a coleta de nuvem bem-sucedida:

```text
N2_CLOUD_GUI_EVIDENCE=COMPLETE_ASSISTED
N2_MANUAL_BROWSER_ZOOM_200=AWAITING_MANUAL_ACCEPTANCE
N3_CLOUD_ACCESSIBILITY_EVIDENCE=PARTIAL_ASSISTED
N3_MANUAL_SCREEN_READER_CRITICAL_JOURNEY=BLOCKED_PENDING_MANUAL_EVIDENCE
PHASE_N_DESIGN_LAB_VALIDATION=IN_PROGRESS_BLOCKED_ON_MANUAL_EVIDENCE
PHASE_O_START_ALLOWED=NO
PR_MERGE_AUTHORIZED=NO
NF_02_START_ALLOWED=NO
```

## 7. Alterações de infraestrutura de validação realizadas

A sequência de estabilização da oficina de testes na nuvem incluiu:

```text
9fbf9a4  add cloud GUI evidence workflow
1dac02d  harden cloud GUI runner lifecycle
26f5829  fix cloud driver module resolution
ab6e55a  add cloud headed GUI driver
b685faa  let Playwright own headed browser lifecycle
5eaf231  deliver cloud keyboard input to active window
03a2d8b  separate assisted keyboard evidence from manual gate
f3fdf7e  strengthen visual evidence captures
```

Principais correções do laboratório:

- Openbox adicionado para gerenciamento confiável das janelas no Xvfb.
- limpeza de processos endurecida para impedir `kill 0`/derrubada do runner.
- resolução de módulos Node corrigida.
- removida dependência frágil de conexão CDP em porta separada.
- Playwright passou a ser o único dono do ciclo de vida do navegador gráfico.
- zoom real de navegador permaneceu em nível de sistema operacional.
- interações automatizadas foram rotuladas explicitamente como `PASS_ASSISTED`.
- screenshots foram reposicionados para mostrar estados abertos e mensagens de erro.

## 8. Invariantes preservados

```text
app/**=UNCHANGED_BY_THIS_MISSION
templates/**=UNCHANGED_BY_THIS_MISSION
static/**=UNCHANGED_BY_THIS_MISSION
migrations/**=UNCHANGED_BY_THIS_MISSION
PRODUCTION_DEPLOY=NO
NF02=NOT_STARTED
PHASE_O=NOT_STARTED
MERGE=NO
FINAL_HUMAN_GATE=LEANDRO
```

## 9. Próximo gate mínimo

Para fechar corretamente a Fase N, ainda é necessário produzir/aceitar as duas evidências manuais exigidas pelo contrato:

1. inspeção manual do navegador em zoom 200% nas superfícies canônicas, podendo usar o pacote de screenshots e métricas desta execução como apoio;
2. jornada crítica real com leitor de tela, confirmando conteúdo, papéis, estados, mensagens e retorno de foco.

Até isso ocorrer, o estado correto continua sendo **Fase N aberta por evidência manual pendente**.
