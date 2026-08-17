# NF-01 — Catalog Completeness RC — H4 — Estados operacionais

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
H4_OPERATIONAL_STATE_COHERENCE=APPROVED_BY_LEANDRO
H4_STATUS=COMPLETE
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H5_MUTATION_UNKNOWN_OUTCOME_IDEMPOTENCY_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela a coerência transversal de `loading`, `empty`, `error`, `degraded` e `offline` para a NF-01. Ela não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Princípio

A apresentação operacional deriva do estado atual da requisição, da existência de conteúdo utilizável anterior, da conectividade, do escopo da falha e da possibilidade real de continuação segura.

```text
OPERATIONAL_PRESENTATION
=
CURRENT_REQUEST
+
USABLE_PRIOR_DATA
+
CONNECTIVITY
+
FAILURE_SCOPE
+
SAFE_CONTINUATION
```

## Carregamento inicial e refresh

```text
INITIAL_LOAD + NO_USABLE_DATA => LOADING
BACKGROUND_REFRESH + USABLE_PRIOR_DATA => PRESERVE_CONTENT
INITIAL_LOAD != BACKGROUND_REFRESH
```

`Skeleton` é uma representação visual possível de `LOADING` quando a estrutura final é previsível. Refresh em background não apaga conteúdo válido apenas para reapresentar skeleton.

## EmptyState

`EmptyState` só existe depois de consulta válida, autorizada e resolvida com zero itens.

```text
SUCCESS + AUTHORIZED_ZERO_ITEMS => EMPTY
LOADING != EMPTY
ERROR != EMPTY
OFFLINE != EMPTY
NO_PERMISSION != EMPTY
UNRESOLVED_REQUEST != EMPTY
ERROR_RESPONSE != EMPTY_RESPONSE
```

## Falha sem dados e falha de refresh

Sem conteúdo utilizável anterior, falha de leitura produz estado bloqueante apropriado.

```text
NO_USABLE_PRIOR_DATA + REQUEST_FAILED => BLOCKING_ERROR_STATE
```

Com conteúdo válido anterior, falha de refresh preserva o conteúdo e comunica degradação/atualidade sem fabricar ausência de dados.

```text
REFRESH_ERROR != NO_USABLE_DATA
REFRESH_FAILURE + USABLE_PRIOR_DATA => PRESERVE_CONTENT
FAILED_REFRESH => PRESERVE_LAST_CONFIRMED_TIMESTAMP
STALE_DATA != CURRENT_DATA
```

Falha parcial permanece localizada quando a tarefa principal ainda é utilizável.

```text
PARTIAL_FAILURE => LOCALIZE_FAILURE
LOCAL_FAILURE => NO_AUTOMATIC_GLOBAL_PROMOTION
```

## Degraded

`DEGRADED` descreve capacidade conhecida parcialmente prejudicada quando ainda existe continuação segura.

```text
DEGRADED != DOWN
DEGRADED != ERROR
SAFE_CONTINUATION_AVAILABLE => DEGRADED_MAY_COEXIST_WITH_USABLE_CONTENT
NO_SAFE_CONTINUATION => BLOCKING_STATE
```

Fallback só pode ser anunciado quando realmente existe e é autorizado pela capacidade, permissão e política atuais.

## Offline

`OFFLINE` é condição de conectividade, não sinônimo de erro ou queda do servidor.

```text
OFFLINE != ERROR
OFFLINE != SERVER_DOWN
OFFLINE != DATA_MISSING
READY + OFFLINE => POSSIBLE
```

Com dados anteriores utilizáveis, o conteúdo permanece visível e a condição offline é comunicada. Sem dados e quando a operação exige conectividade, a apresentação é bloqueante e específica de offline.

```text
OFFLINE + USABLE_PRIOR_DATA => PRESERVE_CONTENT
OFFLINE + NO_USABLE_DATA + ONLINE_REQUIRED => BLOCKING_OFFLINE_STATE
```

Não há promessa de sincronização futura sem fila durável real e semântica de reconciliação.

```text
NO_CONFIRMED_DURABLE_QUEUE => NO_SYNC_PROMISE
```

## Atualidade

`STALE` permanece qualificador de atualidade, não novo estado primário global.

```text
STALE != PRIMARY_CONTENT_RESOLUTION_STATE
FAILED_REFRESH => NO_FAKE_LAST_UPDATED
PAGE_RENDER_TIME != DATA_UPDATE_TIME
```

## Retry e recuperação

H4 congela retry de leitura somente quando seguro. Semântica de retry de mutações é responsabilidade de H5.

```text
READ_RETRY => MAY_BE_AVAILABLE_WHEN_SAFE
MUTATION_RETRY_SEMANTICS => H5
RETRY_STARTED != RECOVERED
TIMER_EXPIRY != RECOVERED
VERIFIED_RECOVERY => REMOVE_PERSISTENT_DEGRADATION
```

## Concorrência operacional

Mudança de query/escopo invalida apresentações obsoletas.

```text
STALE_OPERATIONAL_STATE => MUST_NOT_OVERRIDE_CURRENT_QUERY
OFFLINE_PRESENTATION => DEPENDS_ON_USABLE_PRIOR_DATA_AND_REQUIRED_CAPABILITY
```

## Não duplicação de feedback

Uma mesma condição persistente não deve ser simultaneamente repetida por banner, ErrorState e Toast.

```text
ONE_CONDITION => ONE_PRIMARY_PERSISTENT_PRESENTATION
TOAST => SECONDARY_TRANSIENT_FEEDBACK_ONLY
```

## Matriz congelada

```text
pending + sem dados................ Skeleton/Loading
pending refresh + dados............ manter conteúdo + updating
success + itens.................... Ready
success + zero..................... EmptyState
failure + sem dados................ ErrorState
failure refresh + dados............ conteúdo + DegradationBanner
offline + dados.................... conteúdo + indicação offline/degradada
offline + sem dados + online req... estado bloqueante offline
degraded + fallback seguro......... DegradationBanner + continuidade
degraded + sem continuidade........ estado bloqueante
```

## Testes futuros

Unitários:
- classificador de primeira carga, refresh, zero, falha, offline e degraded;
- `EmptyState` apenas após zero autorizado confirmado;
- preservação de `LastUpdated` após refresh falho;
- ausência de promessa de sync sem fila durável.

Integração:
- `DataTable` carregada -> refresh -> falha, preservando linhas;
- offline com e sem conteúdo prévio;
- falha parcial localizada;
- recuperação verificada removendo banner persistente;
- stale response não alterando query atual.

Regressão:

```text
ERROR_RESPONSE -> EMPTY.............. NO
OFFLINE -> EMPTY..................... NO
REFRESH_FAILURE_WIPES_DATA........... NO
FAILED_REFRESH_UPDATES_LASTUPDATED... NO
RETRY_STARTED_EQUALS_RECOVERED....... NO
OFFLINE_PROMISES_NONEXISTENT_SYNC.... NO
LOCAL_ERROR_BECOMES_GLOBAL........... NO
```

## Contrato congelado

```text
H4_OPERATIONAL_STATE_COHERENCE
INITIAL_LOAD + no usable data -> LOADING.......... YES
BACKGROUND_REFRESH + usable data -> preserve...... YES
LOADING = EMPTY.................................... NO
ERROR = EMPTY...................................... NO
OFFLINE = EMPTY.................................... NO
NO_PERMISSION = EMPTY.............................. NO
SUCCESS + zero authorized items -> EMPTY........... YES
refresh failure = no usable data................... NO
refresh failure wipes valid data................... NO
failed refresh changes LastUpdated................. NO
PARTIAL_FAILURE -> LOCALIZE......................... YES
DEGRADED requires safe continuation................ YES
DEGRADED = DOWN..................................... NO
no safe continuation -> blocking................... YES
OFFLINE = ERROR..................................... NO
OFFLINE = SERVER_DOWN............................... NO
READY + OFFLINE..................................... POSSIBLE
offline + prior data -> preserve.................... YES
offline + no data + online required -> blocking..... YES
no durable queue -> no sync promise................. YES
STALE = new global primary state.................... NO
STALE = freshness qualifier......................... YES
READ retry when safe................................ YES
mutation retry semantics handled by H5.............. YES
retry started = recovered........................... NO
verified recovery required.......................... YES
one condition -> duplicate banner/error/toast....... NO
stale operational response wins current query....... NO
IMPLEMENTATION...................................... NO
PRODUCTION_CHANGE................................... NO
```

## Estado final H4

```text
H4_OPERATIONAL_STATE_COHERENCE=APPROVED_BY_LEANDRO
H4_STATUS=COMPLETE
NEXT_OFFICIAL_ITEM=H5_MUTATION_UNKNOWN_OUTCOME_IDEMPOTENCY_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```
