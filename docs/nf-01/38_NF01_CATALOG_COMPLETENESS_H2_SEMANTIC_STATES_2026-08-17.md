# NF-01 — Catalog Completeness RC — H2 — Estados semânticos globais

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
H2_GLOBAL_SEMANTIC_STATE_COHERENCE=APPROVED_BY_LEANDRO
H2_STATUS=COMPLETE
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H3_RBAC_TENANT_MINIMUM_NECESSARY_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela a coerência transversal dos estados semânticos para a NF-01. Ela não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Problema auditado

A baseline possuía os estados globais `LOADING`, `EMPTY`, `READY`, `SUCCESS`, `WARNING`, `DEGRADED`, `ERROR`, `OFFLINE`, `NO_PERMISSION` e `TELEMETRY_UNAVAILABLE`, além de uma precedência linear histórica. A revisão dos contratos individuais demonstrou que esses estados não pertencem todos à mesma dimensão e podem coexistir quando possuem escopo/fonte distintos.

```text
GLOBAL_STATE != ONE_SINGLE_ENUM_WITH_TOTAL_PRECEDENCE
```

Exemplos válidos:

```text
READY + OFFLINE
READY + DEGRADED
READY + TELEMETRY_UNAVAILABLE
SUCCESS transacional + READY contínuo
```

## Modelo dimensional congelado

```text
ACESSO
→ NO_PERMISSION

RESOLUÇÃO DE CONTEÚDO
→ LOADING | EMPTY | READY | ERROR

CONECTIVIDADE
→ OFFLINE

CONDIÇÃO OPERACIONAL
→ DEGRADED

CONHECIMENTO / TELEMETRIA
→ TELEMETRY_UNAVAILABLE

RESULTADO TRANSACIONAL
→ SUCCESS

ATENÇÃO
→ WARNING
```

Nenhum novo estado de produto é criado por H2; a decisão reorganiza semanticamente os estados já canônicos.

## Identidade de estado

Todo estado relevante deve ser interpretado com tipo, escopo e fonte:

```text
STATE = TYPE + SCOPE + SOURCE
```

Escopos conceituais:

```text
APP
SURFACE
COMPONENT
ACTION
FIELD
```

Guardrail:

```text
LOCAL_ERROR != GLOBAL_APPLICATION_ERROR
LOCAL_STATE => NO_AUTOMATIC_GLOBAL_PROMOTION
```

## Autorização

`NO_PERMISSION` é gate de acesso, não erro operacional nem ausência de dados.

```text
NO_PERMISSION != ERROR
NO_PERMISSION != EMPTY
NO_PERMISSION != DISABLED
AUTHORIZATION_SCOPE => BEFORE_PROTECTED_CONTENT
```

## Resolução de conteúdo

Dentro da mesma consulta e mesmo escopo, os estados primários de resolução são mutuamente exclusivos:

```text
SAME_QUERY_SCOPE:
LOADING != EMPTY
EMPTY != READY
ERROR != EMPTY
ERROR != READY
```

Condições de outras dimensões podem coexistir com conteúdo utilizável.

## READY

```text
READY != SUCCESS
READY != HEALTHY
READY != ONLINE
```

`READY` significa que aquela superfície possui conteúdo/interação utilizável; não declara saúde técnica, conectividade ou sucesso transacional.

## SUCCESS

```text
SUCCESS => CONFIRMED_OUTCOME
SUCCESS != CONTINUOUS_RESOURCE_STATE
```

Sucesso é transacional/temporário e não apaga o estado contínuo do recurso.

## OFFLINE

```text
OFFLINE != ERROR
OFFLINE != SERVER_DOWN
OFFLINE != DATA_MISSING
READY + OFFLINE => POSSIBLE_WHEN_SAFE_CONTINUATION_EXISTS
```

Nenhuma promessa de sincronização futura pode ser inferida sem fila offline durável e contrato correspondente.

## DEGRADED

```text
DEGRADED != DOWN
DEGRADED != ERROR
SAFE_CONTINUATION_AVAILABLE => DEGRADED_MAY_COEXIST_WITH_USABLE_CONTENT
NO_SAFE_CONTINUATION => BLOCKING_STATE
```

## TELEMETRY_UNAVAILABLE

```text
TELEMETRY_UNAVAILABLE != HEALTHY
TELEMETRY_UNAVAILABLE != TARGET_DOWN
TELEMETRY_UNAVAILABLE != TARGET_DEGRADED
TELEMETRY_UNAVAILABLE != SUCCESS
```

Ausência de telemetria representa desconhecimento do estado do alvo. Se a perda da própria telemetria afetar a operação, essa perda pode ser classificada separadamente como degradação; ela não prova degradação do alvo monitorado.

## WARNING e NOT_IMPLEMENTED

```text
WARNING != ERROR
WARNING != VALIDATION_ERROR
WARNING != NEEDS_REVIEW
NOT_IMPLEMENTED != ERROR
NOT_IMPLEMENTED != DEGRADED_BY_DEFAULT
```

Uma capacidade futura nunca operacional não produz incidente/degradação por padrão.

## Arbitragem de apresentação

A precedência linear global deixa de ser o modelo canônico. A apresentação passa a considerar fatos, escopo, dimensões semânticas e impacto.

```text
FACTS
  ↓
SCOPE
  ↓
SEMANTIC DIMENSIONS
  ↓
IMPACT EVALUATION
  ↓
PRESENTATION ARBITRATION
```

Regras:

```text
AUTHORIZATION => BEFORE_PROTECTED_RENDERING
BLOCKING_STATE => DOMINATES_SAME_SCOPE
PERSISTENT_DEGRADATION => MAY_COEXIST_WITH_USABLE_CONTENT
OFFLINE => MAY_COEXIST_WITH_VALID_CONTENT
TRANSIENT_SUCCESS => DOES_NOT_ERASE_CONTINUOUS_STATE
LOCAL_STATE => NO_AUTOMATIC_GLOBAL_PROMOTION
```

## Testes futuros

Unitários:
- classificação por dimensão;
- exigência de escopo/fonte;
- exclusividade de `LOADING/EMPTY/READY/ERROR` na mesma consulta;
- `SUCCESS` apenas com outcome confirmado;
- `TELEMETRY_UNAVAILABLE` sem falso healthy/down/degraded.

Integração:
- `READY + OFFLINE`;
- `READY + DEGRADED`;
- `READY + TELEMETRY_UNAVAILABLE`;
- `NO_PERMISSION` antes de conteúdo protegido;
- `SUCCESS + READY`;
- erro local sem promover toda a aplicação para erro.

Regressão:

```text
TELEMETRY_UNAVAILABLE -> HEALTHY........ NO
OFFLINE -> SERVER_DOWN................... NO
READY -> HEALTHY........................ NO
UNKNOWN_OUTCOME -> SUCCESS............... NO
EMPTY -> ERROR........................... NO
NO_PERMISSION -> EMPTY................... NO
```

## Contrato congelado

```text
H2_GLOBAL_SEMANTIC_STATE_COHERENCE

single global precedence model............... NO
state dimensions............................. YES
state scope required......................... YES
state source required........................ YES

NO_PERMISSION = ERROR........................ NO
NO_PERMISSION = EMPTY........................ NO

LOADING / EMPTY / READY / ERROR
mutually exclusive in same query scope....... YES

READY = SUCCESS.............................. NO
READY = HEALTHY.............................. NO
READY = ONLINE............................... NO

SUCCESS => CONFIRMED_OUTCOME................. YES
SUCCESS = continuous resource state.......... NO

OFFLINE = ERROR............................... NO
OFFLINE = SERVER_DOWN........................ NO
READY + OFFLINE.............................. POSSIBLE

DEGRADED = DOWN............................... NO
DEGRADED = ERROR.............................. NO

TELEMETRY_UNAVAILABLE = HEALTHY.............. NO
TELEMETRY_UNAVAILABLE = TARGET_DOWN.......... NO
TELEMETRY_UNAVAILABLE = TARGET_DEGRADED...... NO

WARNING = ERROR............................... NO
NOT_IMPLEMENTED = ERROR...................... NO
NOT_IMPLEMENTED = DEGRADED by default........ NO

local state automatically becomes global..... NO
authorization before protected rendering..... YES
blocking state dominates same scope........... YES
persistent degradation may coexist........... YES
transient success does not erase state........ YES
```

## Estado final

```text
H2_GLOBAL_SEMANTIC_STATE_COHERENCE=COMPLETE
NEXT_OFFICIAL_ITEM=H3_RBAC_TENANT_MINIMUM_NECESSARY_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```