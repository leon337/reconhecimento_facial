# NF-01 — Component Review F3 — EventTimeline

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
F3_EVENT_TIMELINE=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_F_COMPONENT_REVIEW=COMPLETE
NEXT_OFFICIAL_ITEM=G1_CAMERA_PANEL_COMPONENT_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `EventTimeline` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`EventTimeline` apresenta eventos canônicos de uma entidade ou contexto em ordem temporal compreensível. O componente não cria, deduz, reconstrói ou calcula eventos.

```text
CANONICAL_EVENTS
      ↓
AUTHORIZED_SCOPE
      ↓
TEMPORAL_ORDER
      ↓
EventTimeline
```

```text
EVENT_TIMELINE != EVENT_ENGINE
EVENT_TIMELINE != STATE_ENGINE
EVENT_TIMELINE != AUDIT_ENGINE
EVENT_TIMELINE != PAYROLL_ENGINE
CURRENT_STATE != EVENT_HISTORY
NO_CANONICAL_EVENT => NO_INVENTED_TIMELINE_ITEM
TEMPORAL_PROXIMITY != CAUSALITY
```

A proximidade temporal entre eventos não autoriza a UI a afirmar relação causal sem dado canônico do domínio.

## Identidade e ordenação

Cada evento deve possuir identidade estável e informação temporal canônica.

```text
EVENT_ID........................ REQUIRED_STABLE_ID
TIMESTAMP....................... REQUIRED_CANONICAL_TIME
TYPE............................ REQUIRED_DOMAIN_TYPE
SUBJECT......................... REQUIRED_WHEN_APPLICABLE
AUTHORIZED_PAYLOAD.............. OPTIONAL_BY_EVENT
EVENT_ID != LIST_INDEX
CLIENT_CLOCK != CANONICAL_TIMESTAMP
OCCURRED_AT != RECORDED_AT
SAME_TIMESTAMP => STABLE_TIE_BREAKER
TIMELINE_ORDER => EXPLICIT_AND_STABLE
```

A timeline pode ser ASC ou DESC conforme o contexto, mas a direção deve ser explícita e estável. Quando dois eventos compartilham timestamp, o desempate deve vir de sequência/ID/chave canônica do domínio, nunca da ordem acidental da resposta.

## Anatomia do evento

```text
TIMESTAMP........................ REQUIRED
TITLE............................ REQUIRED
DESCRIPTION...................... OPTIONAL
ACTOR_OR_SOURCE.................. OPTIONAL_WHEN_KNOWN
STATUS_BADGE..................... OPTIONAL_WHEN_SEMANTIC
DETAIL_ACTION.................... OPTIONAL
```

Ator só é exibido quando conhecido de forma confiável.

```text
NO_ACTOR_DATA => NO_INVENTED_ACTOR
SYSTEM_ACTOR != HUMAN_ACTOR
```

## Histórico, correções e auditoria

`EventTimeline` pode apresentar histórico operacional e, quando autorizado, informações provenientes de auditoria. Isso não transforma a apresentação em mecanismo de auditoria nem autoriza declarar trilha legalmente completa.

```text
DISPLAYED_TIMELINE != LEGALLY_COMPLETE_AUDIT_TRAIL
UI_HISTORY_REWRITE_BY_INFERENCE............. PROHIBITED
ORIGINAL_EVENT + CORRECTION_EVENT........... PRESERVE_WHEN_DOMAIN_SUPPLIES_RELATION
```

Correções devem ser representadas conforme a semântica canônica fornecida pelo domínio; a UI não deve apagar ou reescrever silenciosamente o passado por inferência.

## RBAC, privacidade e mínimo necessário

```text
TENANT_RBAC_ENTITY_SCOPE
        ↓
AUTHORIZED_EVENTS
        ↓
AUTHORIZED_EVENT_FIELDS
        ↓
EventTimeline
```

```text
FETCH_ALL_EVENTS_THEN_HIDE.................. PROHIBITED
MINIMUM_NECESSARY_EVENT_DATA................ REQUIRED
UNNECESSARY_PII_OR_INTERNAL_DIAGNOSTICS..... PROHIBITED
BIOMETRIC_DETAIL............................ PROHIBITED_UNLESS_EXPLICITLY_NECESSARY_AND_AUTHORIZED
```

IP, user-agent, request-id, device-id, payload técnico, geolocalização precisa ou dados biométricos não são exibidos apenas porque existem no backend.

## Estados de carregamento, vazio e erro

```text
INITIAL_LOADING => SKELETON
AUTHORIZED_ZERO_EVENTS => EMPTY_STATE
LOAD_FAILURE => ERROR_STATE
LOADING != EMPTY
ERROR != EMPTY
```

Falha de API nunca deve ser apresentada como ausência de eventos.

## Histórico extenso, paginação e atualização incremental

```text
EVENT_TIMELINE != LOAD_ALL_HISTORY
CURSOR_OR_PAGINATION........................ SUPPORTED
DEDUPLICATION => STABLE_EVENT_ID
NEW_EVENT => MUST_NOT_STEAL_SCROLL_CONTEXT
POLLING_SAME_EVENTS => NO_DUPLICATION
STALE_EVENT_RESPONSE_MUST_NOT_OVERRIDE_CURRENT_SET
```

Históricos grandes devem permitir carregamento incremental. Eventos recebidos novamente por polling são deduplicados pela identidade estável, não por texto/timestamp aparente. Novo evento não deve deslocar arbitrariamente o usuário que está lendo histórico anterior.

## Integração com componentes

```text
DetailDrawer + EventTimeline................ SUPPORTED
StatusBadge + EventTimeline................. SUPPORTED
Skeleton + EventTimeline.................... SUPPORTED
EmptyState + EventTimeline.................. SUPPORTED
ErrorState + EventTimeline.................. SUPPORTED
NESTED_DETAIL_DRAWER_FROM_TIMELINE.......... PROHIBITED_BY_DEFAULT
EVENT_TIMELINE != HISTORY_ENGINE
EVENT_TIMELINE != STATUS_ENGINE
```

A superfície usada para detalhe de um evento depende do contexto. Dentro de `DetailDrawer`, abrir outro `DetailDrawer` em cascata é proibido por padrão.

## Registros de ponto

A timeline pode representar eventos de ponto em sequência temporal, mas não calcula jornada, folha ou causalidade.

```text
EVENT_SEQUENCE != PAYROLL_CALCULATION
EVENT_TIMELINE != WORKED_HOURS_ENGINE
```

Qualquer cálculo trabalhista permanece responsabilidade do domínio.

## Acessibilidade e responsividade

O baseline é vertical e responsivo.

```text
SEMANTIC_LIST_OR_ORDERED_LIST............... REQUIRED
TEXTUAL_TIMESTAMP........................... REQUIRED
TIME_SEMANTICS.............................. REQUIRED
COLOR_ONLY_MEANING.......................... PROHIBITED
KEYBOARD_ACCESS_FOR_ACTIONS................. REQUIRED
FOCUS_VISIBLE............................... REQUIRED
VERTICAL_RESPONSIVE_BASELINE................ REQUIRED
MATERIAL_NEW_EVENT_ANNOUNCEMENT............. CONTEXTUAL
POLLING_ANNOUNCEMENT_STORM.................. PROHIBITED
```

## Contrato congelado

```text
F3_EVENT_TIMELINE

histórico temporal........................... YES
criação/inferência de eventos................ NO
canonical events............................. YES
invented events.............................. NO
temporal proximity = causality............... NO
stable EVENT_ID.............................. YES
EVENT_ID = list index........................ NO
canonical timestamp.......................... YES
client clock as source....................... NO
OCCURRED_AT = RECORDED_AT.................... NO
stable tie-breaker........................... YES
ASC / DESC................................... YES explicit
actor/source................................. YES when known
invented actor............................... NO
SYSTEM_ACTOR = HUMAN_ACTOR................... NO
operational history.......................... YES
audit presentation........................... YES
declare complete legal audit trail........... NO
silent history rewrite....................... NO
RBAC before events........................... YES
fetch-all-then-hide.......................... NO
minimum necessary event data................. YES
Skeleton / EmptyState / ErrorState............ YES
load entire history baseline................. NO
cursor/pagination............................. YES
deduplicate by stable event identity.......... YES
new event steals scroll....................... NO
DetailDrawer integration..................... YES
nested DetailDrawer by default............... NO
vertical responsive baseline................. YES
semantic list/time............................ YES
polling announcement storm................... NO
```

## Testes futuros obrigatórios

### Unitários

- evento único e múltiplos eventos;
- ASC / DESC;
- timestamp e ator;
- evento sem ator;
- same-timestamp tie-break;
- loading / empty / error.

### Integração

- `EventTimeline + DetailDrawer`;
- `EventTimeline + StatusBadge`;
- `EventTimeline + Skeleton`;
- `EventTimeline + EmptyState`;
- `EventTimeline + ErrorState`;
- cursor/paginação;
- RBAC.

### Concorrência e atualização incremental

- polling recebe evento repetido sem duplicar;
- novo evento não rouba posição de leitura;
- resposta obsoleta não substitui o conjunto atual.

### Segurança

- isolamento por tenant;
- RBAC de eventos e campos;
- mínimo necessário;
- ausência de biometria e diagnóstico interno não autorizado.

### Responsivo e acessibilidade

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- teclado e screen reader;
- timestamps semânticos;
- atualizações sem tempestade de anúncios.

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
F1_DETAIL_DRAWER=FROZEN_INDIVIDUALLY
F2_CONFIRMATION_MODAL=FROZEN_INDIVIDUALLY
F3_EVENT_TIMELINE=FROZEN_INDIVIDUALLY
PHASE_F_COMPONENT_REVIEW=COMPLETE
NEXT_OFFICIAL_ITEM=G1_CAMERA_PANEL_COMPONENT_REVIEW
```
