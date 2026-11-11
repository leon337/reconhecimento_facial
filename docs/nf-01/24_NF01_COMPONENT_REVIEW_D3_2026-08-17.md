# NF-01 — Revisão individual D3 — DataTable

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Componente:** `D3 — DataTable`  
**HUMAN_GATE:** LEANDRO — APROVADO em 2026-08-17  
**Status:** `FROZEN_INDIVIDUALLY`  
**Implementação visual:** `NO`  
**Produção:** `UNCHANGED`

## Contrato congelado

```text
D3_DATA_TABLE

structured comparable data................ ✅
spreadsheet/editable grid.................. ❌

Search engine.............................. ❌
Filter engine.............................. ❌
Sort engine................................ ❌

real table semantics....................... ✅
clear primary identity..................... ✅
ROW_ID = ROW_INDEX.......................... ❌

sorting optional per column................ ✅
global dataset sort when paginated......... ✅
SORT_CHANGE => PAGE_1....................... ✅
stale response overrides current query..... ❌

StatusBadge integration.................... ✅
LastUpdated/date contracts................. ✅

row actions................................ ✅
icon soup................................... ❌
RBAC before actions........................ ✅

row click default.......................... ❌
explicit link/action....................... ✅

selection optional......................... ✅
checkbox without bulk action............... ❌
page selection = all results............... ❌
query change revalidates selection......... ✅

RBAC before columns/data................... ✅
display:none as security................... ❌

EMPTY_DATASET != NO_RESULTS................ ✅
Skeleton/ErrorState/EmptyState integration. ✅

desktop table.............................. ✅
mobile responsive representation........... ✅
shrink typography to fit.................. ❌
horizontal scroll.......................... ✅ when justified
hide critical column silently.............. ❌

virtualization baseline.................... ❌
inline editing baseline.................... ❌
row expansion baseline..................... ❌
```

## Guardrails congelados

```text
DATATABLE != SPREADSHEET
DATATABLE != SORT_ENGINE
ROW_ID != ROW_INDEX
SORT_CHANGE => PAGE_1
STALE_RESPONSE_MUST_NOT_OVERRIDE_CURRENT_QUERY_STATE
QUERY_SCOPE_CHANGE => REVALIDATE_SELECTION
PAGE_SELECTION != ALL_RESULTS_SELECTION
PERMISSION => AUTHORIZED_COLUMNS => AUTHORIZED_DATA
PERMISSION => ACTION_CATALOG => RENDER
NO_DATA != ZERO
EMPTY_DATASET != NO_RESULTS
MINIMUM_NECESSARY_DATA
```

## Testes futuros obrigatórios

```text
UNIT:
- headers / rows / cells
- stable row key
- sortable vs non-sortable
- asc / desc
- selection
- row actions
- loading / empty / error integration

INTEGRATION:
- DataTable + Search
- DataTable + FilterBar
- DataTable + Pagination
- DataTable + StatusBadge
- DataTable + RBAC
- DataTable + DetailDrawer
- DataTable + Skeleton / EmptyState / ErrorState

CONCURRENCY:
- stale search/sort/filter responses never override current query state

SECURITY:
- tenant isolation
- authorized columns
- authorized actions
- authorized counts
- bulk action permissions
- minimum necessary data

A11Y / RESPONSIVE:
- 360 / 768 / 1024 / 1440+
- zoom 200%
- keyboard
- screen reader
- header/cell relationships
- aria-sort
- contextual checkbox labels
- contextual row action labels
```

## Próxima ação

```text
NEXT_OFFICIAL_ITEM=D4_PAGINATION_COMPONENT_REVIEW
VISUAL_IMPLEMENTATION=NOT_YET
```

Nenhuma autorização de merge foi concedida por esta aprovação.
