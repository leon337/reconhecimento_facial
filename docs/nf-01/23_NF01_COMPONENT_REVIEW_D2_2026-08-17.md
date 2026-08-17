# NF-01 — Component Review D2 — FilterBar

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Componente:** `D2 — FilterBar`  
**Data:** 2026-08-17  
**HUMAN_GATE:** `APPROVED_BY_LEANDRO`  
**Status:** `FROZEN_INDIVIDUALLY`  
**Implementação:** `NO`  
**Produção:** `UNCHANGED`

## Contrato congelado

`FilterBar` representa critérios estruturados e permanece separado de `Search` e do motor de filtros.

```text
SEARCH != FILTER_BAR
FILTER_BAR != FILTER_ENGINE
DRAFT_FILTERS != APPLIED_FILTERS
```

Regras aprovadas:

- filtros aplicados permanecem visíveis e descobríveis;
- modos `IMMEDIATE` e `EXPLICIT` são suportados conforme o contexto;
- no modo explícito, `Cancel` descarta o draft e preserva o estado aplicado;
- `Limpar filtros` não apaga a busca textual;
- filtros podem ser removidos individualmente com nome acessível;
- contagem de filtros representa critérios compreensíveis pelo usuário, não cláusulas internas;
- filtros dependentes usam invalidation/review sem limpeza silenciosa indiscriminada;
- RBAC/tenant/scope precedem dimensões, opções, contagens e resultados;
- opção proibida normalmente não é exibida; indisponibilidade temporária pode ser `disabled` quando justificada;
- `FILTER_OPTIONS_ERROR != RESULTS_ERROR`;
- mudança de filtros aplicados reinicia paginação para a primeira página;
- estado pode ser restaurável/sincronizável com URL quando a arquitetura da tela justificar;
- `NO_RESULTS != EMPTY_DATASET` e os filtros ativos permanecem visíveis no estado sem resultados;
- mobile reorganiza a experiência em vez de comprimir controles;
- `FilterBar` integra-se posteriormente a `Search`, `DataTable`, `Pagination` e superfícies de overlay já previstas.

## Guardrails

```text
APPLIED_FILTERS_MUST_REMAIN_DISCOVERABLE
DRAFT_FILTERS != APPLIED_FILTERS
SEARCH_CLEAR != FILTER_CLEAR
FILTER_CHANGE => PAGE_1
EMPTY_DATASET != NO_RESULTS
PROHIBITED != TEMPORARILY_UNAVAILABLE
FILTER_DIMENSIONS_OPTIONS_COUNTS_RESULTS => SAME_AUTHORIZED_SCOPE
NO_UNAUTHORIZED_OPTION_OR_COUNT_LEAK
NO_SILENT_DEPENDENCY_CLEARING
FILTER_OPTIONS_ERROR != RESULTS_ERROR
```

## Testes futuros obrigatórios

- unitários: sem filtros, múltiplos filtros, draft/applied, apply/cancel, clear, remoção, contador e dependências;
- integração: `FilterBar + Search`, `DataTable`, `Pagination`, URL, RBAC, dependent filters e `EmptyState`;
- regressão semântica dos guardrails acima;
- responsividade: 360 / 768 / 1024 / 1440+ e zoom 200%;
- acessibilidade: teclado, screen reader, focus-visible, nomes acessíveis e ordem DOM;
- segurança/privacidade: tenant isolation, RBAC, opções e contagens no escopo autorizado.

## Gate

```text
D2_FILTER_BAR=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NEXT_OFFICIAL_ITEM=D3_DATA_TABLE_COMPONENT_REVIEW
```
