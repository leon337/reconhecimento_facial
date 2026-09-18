# NF-01 — Gate humano mínimo da Fase N

Data: 2026-09-18
Missão: CPP-NF-01-PRODUTO-DESIGN-SYSTEM
PR: #32
Branch: `docs/nf-01-produto-design-system`
Autoridade humana: LEANDRO

## Objetivo

Reduzir o fechamento manual da Fase N a duas validações humanas objetivas, preservando a regra canônica `FALSE_GREEN=PROHIBITED`.

As evidências automatizadas e assistidas já cobrem responsividade, reflow, teclado, foco, RBAC, estados, cross-screen, axe, zoom headed e regressão. Este gate não repete essas matrizes.

## Caso H1 — Zoom real de navegador a 200%

Superfícies:
- AppShell
- Dashboard
- Funcionários
- Novo Funcionário

Pré-condição:
- navegador gráfico real;
- zoom do navegador em 200%.

Confirmar visualmente:
1. conteúdo essencial permanece legível e acessível;
2. não há clipping que impeça leitura ou ação;
3. não há overflow horizontal indevido da página;
4. overlays e ações principais continuam alcançáveis;
5. foco visível não fica cortado;
6. ContextDrawer, Ver etapas e ErrorSummary continuam utilizáveis.

Resultado permitido:

```text
N2_MANUAL_BROWSER_ZOOM_200=PASS|FAIL
```

Se FAIL, registrar superfície, sintoma e severidade.

## Caso H2 — Jornada crítica com leitor de tela real

Jornada mínima:

```text
Dashboard
→ atenção de biometria pendente
→ Funcionários filtrados
→ Novo funcionário
→ Ver etapas
→ abrir/fechar ContextDrawer
→ provocar erro de etapa
→ ouvir ErrorSummary
→ retornar a Funcionários
```

Confirmar:
1. títulos e nomes acessíveis fazem sentido;
2. foco acompanha a tarefa;
3. elementos ocultos não recebem foco;
4. drawer é anunciado e Esc devolve o foco ao trigger;
5. erro de etapa é anunciado;
6. ErrorSummary é compreensível;
7. retorno à lista mantém contexto suficiente para continuidade.

Resultado permitido:

```text
N3_MANUAL_SCREEN_READER_CRITICAL_JOURNEY=PASS|FAIL
```

## Critério de fechamento

A Fase N só pode avançar quando:

```text
N2_MANUAL_BROWSER_ZOOM_200=PASS
N3_MANUAL_SCREEN_READER_CRITICAL_JOURNEY=PASS
OPEN_BLOCKER=0
OPEN_HIGH=0
```

Até lá:

```text
PHASE_N=IN_PROGRESS_BLOCKED_ON_MANUAL_EVIDENCE
PHASE_O_START_ALLOWED=NO
PR_MERGE_AUTHORIZED=NO
NF02_START_ALLOWED=NO
```

## Evidência de apoio já disponível

A oficina de testes em nuvem produziu:
- Chromium headed;
- zoom medido em ~2.01;
- ausência de overflow horizontal nas superfícies medidas;
- screenshots dos estados principais;
- interações assistidas de teclado e foco;
- axe sem critical/serious nos checks canônicos;
- CI, Production Validation e NF01 Phase N Validation verdes.

Esses dados apoiam a inspeção humana, mas não substituem H1/H2.
