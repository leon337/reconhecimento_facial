# NF-01 — Fase N — H1 Zoom 200% — Evidência Técnica Local

**Data da execução:** 2026-09-18  
**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**PR:** #32  
**Branch:** `docs/nf-01-produto-design-system`

## Classificação

```text
EXECUTION_TYPE=AGENT_LOCAL_REAL_BROWSER_TECHNICAL_EVIDENCE
BROWSER=BRAVE
DISPLAY=REAL_LINUX_X11
ZOOM=200_PERCENT_CONFIRMED
DEVICE_PIXEL_RATIO=2
MANUAL_ACCEPTANCE_CLAIMED=NO
```

Esta evidência mede reflow, overflow, foco e estados de interação em navegador gráfico real. Ela reduz o H1 humano a uma inspeção final visual; não substitui a assinatura humana exigida pelo contrato N1.

## Superfícies

| Superfície | DPR | clientWidth | scrollWidth | Overflow horizontal |
|---|---:|---:|---:|---|
| AppShell | 2 | 952 | 952 | false |
| Dashboard | 2 | 952 | 952 | false |
| Funcionários | 2 | 952 | 952 | false |
| Novo Funcionário | 2 | 952 | 952 | false |

```text
H1_TECHNICAL_ZOOM_200=PASS
H1_TECHNICAL_HORIZONTAL_OVERFLOW=PASS
H1_MANUAL_BROWSER_ZOOM_200=AWAITING_HUMAN_ACCEPTANCE
```

## Novo Funcionário — estados críticos

### Stepper

```text
expanded=true
hidden=false
buttons=8
withinHorizontal=true
```

### ContextDrawer

```text
hidden=false
ariaHidden=false
withinViewport=true
closeControlWithinViewport=true
```

### Retorno de foco

```text
drawer_close_focus.hidden=true
drawer_close_focus.focusReturned=true
```

### ErrorSummary

```text
hidden=false
text="Revise as informações desta etapa. Selecione uma opção para continuar."
withinHorizontal=true
activeIsSummary=true
```

### Ações inferiores

As ações permaneceram visíveis no fluxo e horizontalmente contidas. Após rolagem programática para o fim do formulário, permaneceram alcançáveis dentro do viewport.

## Arquivos locais e integridade

Diretório local:

```text
/home/leo/reconhecimento_facial/docs/nf-01/evidence/phase-n/agent-local-2026-09-18/
```

Hashes principais:

```text
H1-cdp-app-shell-zoom200.png
sha256=c43a017d59910629273ce2b40a5d7b69ee21855ead7880cc1a1f263a0dbddad3

H1-cdp-dashboard-zoom200.png
sha256=41c3096c8b08fee4c1f40d314cf423bc3baf64a42a046110e2bc520476455c63

H1-cdp-funcionarios-zoom200.png
sha256=1541c72a426780c3d32be00b68a906b67438e6a1540d674675c558a66a05b0b6

H1-cdp-novo-funcionario-zoom200.png
sha256=96a11422cda5f237ffbb1959fb8fe76fc828ac4a1e94c9a36e959251316018ab

H1-state-step-list-zoom200.png
sha256=b0a5257116c2e4f01363909c5333aa893fba6577a5ca09a6b1b197c2411a46e6

H1-state-context-drawer-zoom200.png
sha256=dba210fb2a0679e3c2b3e77b9e3fca3920696c7823a78d308249bb2d3ff8d86c

H1-state-error-summary-zoom200.png
sha256=c54b3f1caa9f1402fcad53b46a84042d7891305555d93bc00945d9a5cf526618

H1-cdp-metrics.json
sha256=aad6128b8b0d6a919e71818255c1a11c3ff6b9001a10cf7e59314291a1eca6f2

H1-interaction-metrics.json
sha256=5bf3ae84223e19bb88c0ad0ebe9c45453193cb208c3f9fd427ec18c7f295ee2c
```

## Resultado

```text
H1_TECHNICAL_EVIDENCE=COMPLETE
H1_TECHNICAL_RESULT=PASS
H1_HUMAN_GATE=READY
H1_MANUAL_BROWSER_ZOOM_200=NOT_YET_SIGNED
```

O único passo restante do H1 é a confirmação humana final de que o conjunto visual em 200% permanece utilizável, sem corte funcional, sobreposição bloqueante ou perda de ação essencial.

## Estado da Fase N

```text
N3_MANUAL_SCREEN_READER_CRITICAL_JOURNEY=PASS
N2_MANUAL_BROWSER_ZOOM_200=AWAITING_HUMAN_ACCEPTANCE
PHASE_N_CLOSEOUT=BLOCKED_ON_H1_ONLY
PHASE_O_START_ALLOWED=NO
PR_MERGE_AUTHORIZED=NO
NF02_START_ALLOWED=NO
```
