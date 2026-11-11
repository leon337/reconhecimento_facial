# NF-01 — Component Review D4 — Pagination

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
D4_PAGINATION=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_D_COMPONENT_REVIEW=COMPLETE
NEXT_OFFICIAL_ITEM=E1_EMPTY_STATE_COMPONENT_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `Pagination` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`Pagination` comunica posição e permite navegar por partes do conjunto produzido pela consulta atual.

```text
Search + FilterBar + Sort
          ↓
      QUERY STATE
          ↓
       DataTable
          ↓
      Pagination
```

```text
PAGINATION != SEARCH_ENGINE
PAGINATION != FILTER_ENGINE
PAGINATION != SORT_ENGINE
PAGINATION != AUTHORIZATION_ENGINE
PAGINATION != DATASET_ENGINE
```

`DataTable` e `Pagination` consomem metadados do mesmo estado canônico de consulta; `Pagination` não manipula a tabela diretamente.

## Contrato congelado

```text
previous / next............................. REQUIRED_BASELINE
current position............................ REQUIRED
page numbers................................. OPTIONAL_WHEN_APPLICABLE
ellipsis.................................... OPTIONAL_WHEN_APPLICABLE
first / last buttons........................ OPTIONAL
page size................................... OPTIONAL
free numeric page size...................... PROHIBITED

CURRENT_PAGE_ONLY_BY_COLOR.................. PROHIBITED
ARIA_CURRENT................................ REQUIRED_WHEN_PAGE_BASED

NEW_SEARCH => PAGE_1........................ REQUIRED
FILTER_CHANGE => PAGE_1..................... REQUIRED
SORT_CHANGE => PAGE_1....................... REQUIRED
PAGE_SIZE_CHANGE => PAGE_1.................. REQUIRED
PAGE_CHANGE_PRESERVES_QUERY_CONTEXT......... REQUIRED

TOTAL_COUNT => SAME_AUTHORIZED_QUERY_SCOPE.. REQUIRED
GLOBAL_COUNT_LEAK........................... PROHIBITED
PAGE_SELECTION == ALL_RESULTS_SELECTION..... FALSE

INVALID_PAGE_AS_NO_RESULTS.................. PROHIBITED
CANONICAL_PAGE_RECOVERY..................... REQUIRED
MUTATION_CAN_INVALIDATE_CURRENT_PAGE........ TRUE

PAGE_BASED_PRESENTATION..................... PRIMARY_BASELINE
CURSOR_BASED_COMPATIBILITY.................. REQUIRED_ARCHITECTURAL_OPENNESS
PAGINATION == OFFSET_ONLY_ENGINE............ FALSE

STALE_RESPONSE_OVERRIDES_CURRENT_PAGE....... PROHIBITED
ZERO_RESULTS_NAV_CONTROLS................... OMIT
SINGLE_PAGE_NAV_CONTROLS.................... GENERALLY_OMIT

DESKTOP_FULL_PAGINATION..................... SUPPORTED
MOBILE_SIMPLIFIED_REPRESENTATION............ SUPPORTED
TINY_TOUCH_TARGETS_TO_FIT................... PROHIBITED

PAGINATION_STATE_RESTORABLE................. WHEN_APPLICABLE
BACK_RESTORES_QUERY_AND_PAGE_CONTEXT........ WHEN_APPLICABLE
KEYBOARD_AND_SCREEN_READER.................. REQUIRED
```

## Estado canônico da consulta

```text
QueryState
├── search
├── filters
├── sort
├── page
└── pageSize
        ↓
Query layer
        ↓
Result
├── rows
├── authorized total quando disponível
├── current page/cursor
└── pagination metadata
```

Mudança apenas de página preserva `Search`, `FilterBar` e `Sort`. Mudanças que alteram o conjunto ou sua ordenação — nova busca, filtro, sort ou page size — reiniciam em página 1.

## Contagem, RBAC e privacidade

O total exibido deve corresponder ao mesmo tenant, RBAC, busca, filtros e demais restrições da consulta que produziu as linhas visíveis.

```text
TENANT + RBAC + SEARCH + FILTERS + SORT
                ↓
       AUTHORIZED_RESULT_SET
                ↓
          TOTAL / PAGE DATA
```

Não é permitido mostrar total global seguido de linhas reduzidas por permissão.

## Página inválida e mutações

Uma página solicitada que não existe não pode ser apresentada como um `NO_RESULTS` válido. A camada de consulta deve recuperar/canonicalizar para uma página válida conforme o contrato da API.

Mutações podem reduzir o total e invalidar a página atual. Se a última linha da última página desaparecer e a página deixar de existir, o estado deve ser reconciliado para uma página válida.

## Estratégias de paginação

A apresentação principal das telas administrativas da NF-01 pode ser baseada em páginas, mas o Design System não fica acoplado a offset como única estratégia.

```text
PAGE_BASED
?page=4&pageSize=20

CURSOR_BASED
?after=abc123
```

Quando o backend não conhece o total exato, a UI não deve inventar `Página X de Y`.

## Concorrência

```text
request page 2 lento
request page 3 rápido
page 3 responde
page 2 responde depois
        ↓
PAGE_2_RESPONSE_MUST_NOT_OVERRIDE_PAGE_3
```

O estado de consulta mais recente vence.

## Loading, foco e viewport

Durante mudança de página, linhas antigas não podem ser apresentadas como se pertencessem à nova página sem indicação clara de atualização.

A implementação futura deve testar estratégia previsível de foco/viewport após troca de página, evitando tanto permanecer no final de uma lista já substituída quanto roubar foco arbitrariamente.

## Responsividade

Desktop pode exibir resumo, números, anterior e próxima. Mobile pode simplificar para anterior + posição atual + próxima, preservando orientação e alvos de toque adequados.

```text
DESKTOP:  ‹ Anterior  1 … 4 [5] 6 … 22  Próxima ›
MOBILE:   [‹]  Página 5 de 22  [›]
```

Reorganizar é permitido; comprimir controles até perder legibilidade ou alvo de toque é proibido.

## Acessibilidade

- região de navegação com nome acessível equivalente a `Paginação`;
- página atual comunicada semanticamente, por exemplo `aria-current="page"`;
- `Anterior` e `Próxima` com nomes acessíveis e estado disabled real quando indisponíveis;
- números com contexto equivalente a `Ir para página 3`;
- teclado e `focus-visible` obrigatórios;
- posição atual não depende apenas de cor;
- controles touch mantêm alvo adequado.

## Anti-padrões congelados

- total global fora do RBAC;
- manter página alta após mudança de Search/Filter/Sort/page size;
- mudar página apagando Search/Filter/Sort;
- página inválida tratada como ausência real de resultados;
- resposta assíncrona antiga substituindo a página atual;
- seleção da página interpretada como seleção de todo o dataset;
- dezenas de números espremidos em mobile;
- setas sem nome acessível;
- posição atual comunicada só por cor;
- inventar total quando a estratégia não o conhece;
- paginação dividindo dataset bruto no navegador como regra geral.

## Testes futuros

### Unitários

- primeira, intermediária e última página;
- previous/next e disabled;
- current page;
- ellipsis;
- page size quando configurado;
- metadados de página inválida;
- single page;
- zero results.

### Integração

- Pagination + Search;
- Pagination + FilterBar;
- Pagination + Sort;
- Pagination + DataTable;
- Pagination + URL/restauração;
- Pagination + Detail → Back;
- Pagination + RBAC count;
- Pagination + bulk selection.

### Regressão de estado

```text
NEW_SEARCH => PAGE_1
FILTER_CHANGE => PAGE_1
SORT_CHANGE => PAGE_1
PAGE_SIZE_CHANGE => PAGE_1
PAGE_CHANGE => PRESERVE_SEARCH_FILTER_SORT
```

### Concorrência

Resposta de página antiga nunca pode substituir o estado de página mais recente.

### Responsividade / A11y / Segurança

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- teclado e screen reader;
- `aria-current` e accessible names;
- touch targets;
- foco após page change;
- authorized total/rows/tenant scope;
- seleção limitada ao escopo explicitamente comunicado.

## Resultado

```text
D4_PAGINATION=FROZEN
PHASE_D_COMPONENT_REVIEW=COMPLETE
NEXT=E1_EMPTY_STATE_COMPONENT_REVIEW
```
