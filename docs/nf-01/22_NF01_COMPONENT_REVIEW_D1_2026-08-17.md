# NF-01 — Revisão individual D1 Search

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Componente:** `Search`  
**Gate humano:** LEANDRO  
**Status:** `FROZEN_INDIVIDUALLY`  
**Implementação visual:** não iniciada  
**Código de produção:** inalterado

---

## HUMAN_GATE

```text
D1_SEARCH=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
APPROVAL_DATE=2026-08-17
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
```

## Propósito

`Search` localiza registros por termo textual dentro do conjunto de dados que o usuário já está autorizado a consultar.

```text
SEARCH = termo livre
FILTER = condição estruturada
SEARCH_COMPONENT != SEARCH_ENGINE
```

## Contrato congelado

- `Search` e `FilterBar` são conceitos distintos.
- label acessível é obrigatória; placeholder não substitui label.
- ícone de busca é decorativo quando não é ação; se acionável, deve ser botão acessível.
- ação de limpar usa `IconButton` com nome acessível como `Limpar busca`.
- modos `INSTANT` e `EXPLICIT` são permitidos conforme custo/latência da consulta.
- busca assíncrona instantânea usa debounce apropriado; o valor exato fica para implementação/testes.
- resposta de consulta antiga nunca pode sobrescrever a query mais recente.
- estados previstos: `IDLE`, `TYPING`, `LOADING`, `RESULTS`, `NO_RESULTS`, `ERROR`, `OFFLINE`.
- `EMPTY_DATASET != ZERO_SEARCH_RESULTS`.
- nova busca reinicia a paginação do novo conjunto, normalmente na primeira página.
- busca e filtros podem coexistir, mas permanecem visual e semanticamente distinguíveis.
- estado de busca deve ser restaurável quando a jornada exigir, inclusive lista → detalhe → voltar e, quando apropriado, URL sincronizável.
- semântica de matching pertence ao domínio/backend; o componente não inventa regras por tela.
- escopo organizacional, tenant e RBAC são aplicados antes da consulta e também governam contagens, sugestões e paginação.
- resultados fora do escopo não podem ser descobertos por mensagens, contagens ou autocomplete.
- autocomplete remoto não faz parte do contrato base obrigatório.
- comprimento mínimo de query não possui valor universal; pode ser configurado pelo domínio.
- loading não pode apresentar resultados antigos como se fossem resposta atual sem indicação clara.
- `Escape` não limpa silenciosamente uma busca já executada.
- queries potencialmente sensíveis devem respeitar minimização/redaction em telemetria e logs.

## Guardrails

```text
SEARCH != FILTER_BAR
SEARCH_COMPONENT != SEARCH_ENGINE
EMPTY_DATASET != ZERO_SEARCH_RESULTS
STALE_RESPONSE_MUST_NOT_OVERRIDE_CURRENT_QUERY
NEW_SEARCH => PAGE_1
RBAC_SCOPE_BEFORE_QUERY
NO_GLOBAL_RESULT_THEN_HIDE
NO_UNAUTHORIZED_COUNT_LEAK
PLACEHOLDER != ACCESSIBLE_LABEL
```

## Testes futuros

### Unitários

- estados IDLE/TYPING/LOADING/RESULTS/NO_RESULTS/ERROR/OFFLINE;
- clear;
- Enter;
- query state;
- `minQueryLength` quando configurado.

### Integração

- Search + API;
- Search + FilterBar;
- Search + DataTable;
- Search + Pagination;
- Search + EmptyState;
- Search + RBAC/tenant scope;
- Search + URL/restauração;
- lista → detalhe → voltar preservando busca quando aplicável.

### Concorrência

- query A lenta;
- query B rápida;
- B vence;
- resposta tardia de A é descartada.

### Responsividade / acessibilidade

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- teclado;
- screen reader;
- focus-visible;
- clear IconButton acessível.

### Segurança / privacidade

- isolamento organizacional/tenant;
- RBAC antes da busca;
- contagem dentro do escopo;
- nenhuma confirmação de existência fora do escopo;
- redaction/minimização de queries sensíveis.

## Próximo item

```text
NEXT_OFFICIAL_ITEM=D2_FILTER_BAR_COMPONENT_REVIEW
VISUAL_IMPLEMENTATION=NOT_YET
```

Este checkpoint não autoriza NF-02, produção, backend, deploy ou merge.