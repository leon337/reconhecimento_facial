# NF-01 — Component Review E1 — EmptyState

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
E1_EMPTY_STATE=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_E_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=E2_ERROR_STATE_COMPONENT_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `EmptyState` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`EmptyState` comunica ausência confirmada de conteúdo após resolução válida do contexto/dataset autorizado.

```text
QUERY / CONTEXTO
      ↓
resultado válido
      ↓
0 itens
      ↓
classificar motivo
      ↓
EmptyState
```

```text
EMPTY_STATE != DATA_ENGINE
LOADING != EMPTY
ERROR != EMPTY
NO_PERMISSION != EMPTY
NO_RESULTS != EMPTY_DATASET
EMPTY != SUCCESS
```

## Situações válidas

```text
EMPTY_DATASET
NO_RESULTS
NO_ITEMS_IN_CONTEXT
NOT_CONFIGURED  # somente quando ausência legítima de configuração, não falha
```

Situações explicitamente fora do contrato de `EmptyState`:

```text
LOADING
ERROR
OFFLINE
NO_PERMISSION como substituição automática
TELEMETRY_UNAVAILABLE
```

## Anatomia congelada

```text
TITLE............................... REQUIRED
DESCRIPTION......................... RECOMMENDED
ICON_OR_ILLUSTRATION................ OPTIONAL
PRIMARY_ACTION...................... OPTIONAL
SECONDARY_ACTION.................... EXCEPTIONAL
CONTEXT............................. REQUIRED_WHEN_NEEDED_TO_EXPLAIN_CAUSE
```

O ícone/ilustração é apenas reforço visual; não carrega significado exclusivo. Ícones decorativos devem ser `aria-hidden`.

## Regras semânticas

- `EMPTY_DATASET` significa que o conjunto autorizado realmente não possui entidades naquele escopo.
- `NO_RESULTS` significa que a busca/filtros atuais retornaram zero, sem afirmar que o dataset base está vazio.
- `NO_ITEMS_IN_CONTEXT` representa ausência legítima em período/contexto específico, sem inferir automaticamente sucesso.
- `NOT_CONFIGURED` pode usar `EmptyState` quando a configuração de fato não existe e isso não representa falha.
- Ausência de fonte/telemetria nunca pode ser convertida em mensagem positiva de vazio.
- `NO_SOURCE` não autoriza frases como “Nenhuma falha detectada”.
- Estado vazio confirmado só pode ser apresentado após request/contexto resolvido.
- `ERROR_RESPONSE != EMPTY_RESPONSE`.
- Resposta antiga de zero resultados não pode sobrescrever o estado de uma query mais recente.

## Search / FilterBar

`NO_RESULTS` deve preservar a causa visível da consulta atual.

```text
SEARCH + FILTERS + ZERO_RESULTS
```

Ações de limpeza permanecem semanticamente distintas:

```text
SEARCH_CLEAR != FILTER_CLEAR
```

Se houver ação para limpar ambos, ela deve ser explicitamente nomeada como tal.

## CTA / RBAC

CTA é opcional e só aparece quando realmente ajuda a resolver o estado.

```text
PERMISSION
    ↓
AVAILABLE_ACTIONS
    ↓
EmptyState
```

Ações proibidas por RBAC não devem ser mostradas como disabled por padrão. A classificação de vazio ocorre somente depois de tenant/RBAC/scope terem sido aplicados; o texto não pode revelar entidades fora do escopo autorizado.

## Integrações

- `DataTable`: `EmptyState` apresenta ausência confirmada sem transformar tabela em erro.
- `Pagination`: com total zero, controles de navegação devem ser omitidos.
- `Skeleton`: request não resolvido usa loading/skeleton, nunca empty confirmado.
- `ErrorState`: falha de API usa `ErrorState`, nunca mensagem de inexistência de dados.

## Responsividade e acessibilidade

A composição deve reorganizar-se em 360/768/1024/1440+ sem reduzir tipografia abaixo dos tokens apenas para caber. O estado precisa continuar compreensível sem imagem. `EmptyState` não é `alert` urgente por padrão. A ordem semântica deve ser título → descrição/contexto → ação. Ações reais devem ser navegáveis por teclado e ter foco visível.

## Anti-padrões proibidos

```text
LOADING -> "Nenhum resultado"................ PROHIBITED
ERROR -> "Nenhum resultado".................. PROHIBITED
NO_PERMISSION -> "Nenhum cadastro"........... PROHIBITED
NO_RESULTS -> "Nenhum cadastro existente".... PROHIBITED
NO_SOURCE -> "Nenhuma falha detectada"........ PROHIBITED
CTA sem permissão............................. PROHIBITED
CTA sem utilidade............................. PROHIBITED
mensagem genérica "Nada aqui"................ PROHIBITED
ícone como única informação................... PROHIBITED
paginação "1 de 0"............................ PROHIBITED
empty confirmado durante request.............. PROHIBITED
stale zero-result sobrescrever query atual..... PROHIBITED
EMPTY => SUCCESS............................... PROHIBITED
```

## Testes futuros

### Unitários

```text
EMPTY_DATASET
NO_RESULTS
NO_ITEMS_IN_CONTEXT
NOT_CONFIGURED
com CTA / sem CTA
ícone opcional
contexto textual
RBAC da ação
```

### Integração

```text
EmptyState + Search
EmptyState + FilterBar
EmptyState + DataTable
EmptyState + Pagination
EmptyState + RBAC
EmptyState + Skeleton
EmptyState + ErrorState
```

### Regressão semântica

```text
LOADING != EMPTY
ERROR != EMPTY
NO_PERMISSION != EMPTY
NO_RESULTS != EMPTY_DATASET
EMPTY != SUCCESS
STALE_ZERO_RESULT_MUST_NOT_OVERRIDE_CURRENT_QUERY
```

### Responsividade / A11Y

```text
360 / 768 / 1024 / 1440+
zoom 200%
screen reader
teclado nas ações
ordem semântica
ícone decorativo
```

---

```text
E1_EMPTY_STATE=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PHASE_E_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=E2_ERROR_STATE_COMPONENT_REVIEW
```
