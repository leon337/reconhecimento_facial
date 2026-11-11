# NF-01 — Catalog Completeness RC — H8 — Temporalidade, concorrência e stale responses

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
H8_TEMPORAL_CONCURRENCY_STALE_RESPONSE_COHERENCE=APPROVED_BY_LEANDRO
H8_STATUS=COMPLETE
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H9_COMPONENT_SURFACE_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela a coerência transversal de temporalidade, concorrência, revisões e descarte de respostas obsoletas para a NF-01. Não autoriza implementação visual, produção, NF-02 ou merge.

## Princípio central

```text
RESPONSE_ARRIVAL_ORDER != STATE_AUTHORITY
LATEST_RESPONSE != LATEST_USER_INTENT
CURRENT_LOGICAL_CONTEXT => WINS
ASYNC_RESULT => MUST_MATCH_RELEVANT_CURRENT_CONTEXT
```

A autoridade de aplicação de uma resposta assíncrona vem de sua correspondência com o contexto lógico atual, não da ordem em que a rede entrega respostas.

## Identidade de contexto

Conforme a operação, a coerência pode depender de identidade lógica como:

```text
QUERY_IDENTITY
ENTITY_ID
AUTHORIZED_SCOPE
DRAFT_ID
REVISION
SESSION_ID
CAPTURE_ID
OPERATION_ID
```

H8 não exige que todas as operações usem todos esses identificadores e não congela uma biblioteca cliente específica.

```text
SPECIFIC_FRONTEND_LIBRARY_FROZEN=NO
BEHAVIORAL_CONCURRENCY_CORRECTNESS=REQUIRED
```

## Requests e cancelamento

```text
CLIENT_ABORT != GUARANTEED_NO_RESPONSE
ABORT_PREVIOUS_REQUEST => OPTIONAL_OPTIMIZATION
STALE_RESPONSE_GUARD => REQUIRED_CORRECTNESS
```

Cancelar um request pode economizar trabalho, mas não substitui a validação de contexto antes de aplicar seu resultado.

## Search / Filter / Sort / Pagination

```text
QUERY_CONTEXT = SEARCH + FILTERS + SORT + PAGINATION_OR_CURSOR + AUTHORIZED_SCOPE
STALE_QUERY_RESPONSE => NO_ROWS_OVERRIDE
STALE_QUERY_RESPONSE => NO_TOTALS_OVERRIDE
STALE_QUERY_RESPONSE => NO_PAGINATION_OVERRIDE
STALE_QUERY_RESPONSE => NO_EMPTY_OVERRIDE
STALE_QUERY_RESPONSE => NO_ERROR_OVERRIDE
STALE_QUERY_RESPONSE => NO_SELECTION_OVERRIDE
```

Um resultado obsoleto também não pode promover um estado operacional antigo sobre o estado atual.

```text
STALE_RESULT => MUST_NOT_OVERRIDE_CURRENT_OPERATIONAL_STATE
```

## EntityPicker e validação remota

```text
ENTITY_PICKER_STALE_RESPONSE => MUST_NOT_OVERRIDE_CURRENT_QUERY
VALIDATION_RESULT => MUST_MATCH_CURRENT_FIELD_VALUE_OR_REVISION
STALE_VALIDATION_RESPONSE => MUST_NOT_REINTRODUCE_ERROR
HIGHLIGHTED_OPTION != COMMITTED_SELECTION
```

## Entidade e DetailDrawer

```text
STALE_ENTITY_RESPONSE => NO_CROSS_ENTITY_RENDER
STALE_ENTITY_RESPONSE => NO_WRONG_TITLE_STATUS_ACTIONS_OR_FIELDS
```

Resposta de uma entidade anteriormente aberta não pode ser aplicada a outra entidade atualmente selecionada.

## Escopo e autorização

```text
SCOPE_CHANGE => REVALIDATE_DATA
OLD_SCOPE_RESPONSE => MUST_NOT_RENDER_IN_CURRENT_SCOPE
AUTHORIZATION_AT_REQUEST_TIME != AUTOMATIC_RENDER_AUTHORIZATION_LATER
RESULT => CURRENT_AUTH_SCOPE_REVALIDATION_OR_DISCARD_WHEN_APPLICABLE
```

Isto também é uma fronteira de privacidade: dados de empresa, unidade, usuário ou sessão anterior não podem aparecer em um novo escopo por resposta tardia.

## Draft, revision e autosave

A NF-01 preserva o modelo canônico de draft com identidade/revisão conceitual.

```text
OLDER_REVISION_ACK => MUST_NOT_ROLL_BACK_CURRENT_REVISION
STALE_REVISION => CONFLICT
CONCURRENT_EDIT => NO_SILENT_OVERWRITE
UNRESOLVED_CONFLICT => AUTOSAVE_PAUSED
UNRESOLVED_CONFLICT => NO_AUTOSAVE_WRITE_LOOP
CONCURRENT_VERSION_CONFLICT => NO_SILENT_AUTO_MERGE
```

Duas abas ou dois administradores não usam `last-write-wins` silencioso. Dados locais conflitantes devem ser preservados temporariamente para resolução explícita, e conclusão permanece bloqueada enquanto o conflito relevante não for resolvido.

## Conflito

```text
CONFLICT != NETWORK_ERROR
CONFLICT != VALIDATION_ERROR
STALE_WRITE_BASE => CONFLICT => RECONCILE
CONFLICT => NO_SILENT_OVERWRITE
```

H8 não congela estratégia técnica universal de merge ou versionamento.

## Tempo e timestamps

```text
RESPONSE_RECEIVED_AT != DATA_UPDATED_AT
PAGE_RENDER_TIME != DATA_UPDATE_TIME
CLIENT_CLOCK != CANONICAL_TIMESTAMP
LATE_RESPONSE_RECEIVED_NOW => MUST_NOT_FABRICATE_NEWER_DATA_TIMESTAMP
```

O relógio do cliente pode apoiar UX local, timeout e animação, mas não define sozinho ordem canônica de eventos, hora de ponto, vigência, versão ou recência autoritativa.

## EventTimeline e polling

```text
OCCURRED_AT != RECORDED_AT
POLL_RESPONSE_ORDER != EVENT_TEMPORAL_ORDER
OLDER_POLL_RESULT => MUST_NOT_REPLACE_NEWER_CANONICAL_SET
EVENT_ID => DEDUPLICATION
SAME_TIMESTAMP => STABLE_TIE_BREAKER
OLD_EVENT != STALE_RESPONSE
```

Um evento antigo cronologicamente pode continuar sendo um fato canônico; `stale response` se refere à obsolescência do contexto/resultado recebido, não à idade do evento.

## PunchResult e CameraPanel

```text
STALE_PUNCH_RESULT => MUST_NOT_OVERRIDE_CURRENT_SESSION
CAPTURE_RESULT => MUST_MATCH_ACTIVE_CAPTURE_IDENTITY
OLD_CAPTURE_RESULT => MUST_NOT_CROSS_SESSION_BOUNDARY
NEXT_USER => NO_PREVIOUS_USER_TRANSIENT_DATA
```

Resultado atrasado de uma pessoa/captura não pode ser renderizado para outra sessão/pessoa.

## Navegação, history e sessão

```text
ROUTE_CONTEXT_CHANGED => OLD_SURFACE_RESULT_NOT_APPLIED_TO_CURRENT_SURFACE
HISTORY_ENTRY => RESTORE_ASSOCIATED_UI_STATE
ASYNC_RESULTS => MUST_MATCH_RESTORED_CONTEXT
AUTH_SESSION_CHANGE => PREVIOUS_AUTH_ASYNC_RESULTS_REQUIRE_REVALIDATION_OR_DISCARD
```

Nenhuma resposta anterior deve provocar flash de conteúdo protegido após mudança de autenticação ou autorização.

## Relação com H5

```text
IDEMPOTENCY != CONCURRENCY_CONTROL
STALE_UI_CONTEXT != SAFE_TO_IGNORE_BACKEND_EFFECT
```

H8 governa qual resultado pode atualizar a superfície atual. H5 continua governando side effects, `UNKNOWN_OUTCOME`, reconciliação e retry. Uma mutação que ficou obsoleta para a UI pode ainda exigir reconciliação do efeito backend.

## Testes futuros obrigatórios

### Unitários

- comparação de query/context identity;
- revision mais antiga não substitui mais nova;
- validação remota obsoleta não reintroduz erro;
- entity/capture/session identity;
- descarte seguro de estados `loading/empty/error/ready` obsoletos;
- ordenação/tie-breaker temporal determinístico.

### Integração

Inverter deliberadamente a ordem das respostas:

```text
A iniciado
B iniciado
B retorna
A retorna
```

para:

- Search;
- FilterBar/Sort/Pagination;
- EntityPicker;
- validação remota;
- DetailDrawer;
- mudança de scope;
- autosave;
- polling/EventTimeline;
- CameraPanel;
- PunchResult.

Também testar:

- duas abas;
- dois administradores;
- conflito de revision;
- refresh/back/forward;
- sessão expirada e reautenticada.

### Regressão

```text
RESPONSE_ARRIVAL_ORDER_AS_AUTHORITY=NO
STALE_QUERY_OVERRIDES_CURRENT_DATA=NO
STALE_QUERY_OVERRIDES_EMPTY_OR_ERROR=NO
STALE_VALIDATION_REINTRODUCES_ERROR=NO
STALE_ENTITY_CROSSES_ENTITY=NO
OLD_SCOPE_DATA_FLASH=NO
OLDER_REVISION_OVERWRITES_NEWER=NO
SILENT_LAST_WRITE_WINS=NO
AUTOSAVE_CONTINUES_DURING_UNRESOLVED_CONFLICT=NO
SILENT_AUTO_MERGE=NO
CLIENT_CLOCK_AS_CANONICAL_DOMAIN_TIME=NO
OLDER_POLL_REPLACES_NEWER_SET=NO
STALE_PUNCH_RESULT_CROSSES_SESSION=NO
STALE_CAPTURE_RESULT_CROSSES_SESSION=NO
OLD_ROUTE_RESULT_OVERRIDES_CURRENT_ROUTE=NO
PREVIOUS_AUTH_RESULT_FLASHES_PROTECTED_DATA=NO
```

## Invariantes preservados

```text
app/**=UNCHANGED
templates/**=UNCHANGED
static/**=UNCHANGED
migrations/**=UNCHANGED
backend/routes=UNCHANGED
DECISOES_CONGELADAS.md=UNCHANGED
NF02=NOT_STARTED
AI=NOT_IMPLEMENTED
OBSERVABILITY_BACKEND=NOT_IMPLEMENTED
DEPLOY=NO
PR32_MERGE=NOT_AUTHORIZED
```

## Continuidade

```text
H1=COMPLETE_WITH_GAP
H1A=COMPLETE
H2=COMPLETE
H3=COMPLETE
H4=COMPLETE
H5=COMPLETE
H6=COMPLETE
H7=COMPLETE
H8=COMPLETE
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H9_COMPONENT_SURFACE_COHERENCE
VISUAL_IMPLEMENTATION=NOT_YET
```
