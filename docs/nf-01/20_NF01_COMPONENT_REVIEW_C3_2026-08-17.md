# NF-01 — Revisão individual C3 — HealthCard

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Componente:** `C3 — HealthCard`  
**Gate humano:** `APPROVED_BY_LEANDRO`  
**Estado:** `FROZEN_INDIVIDUALLY`

---

## Decisão

LEANDRO aprovou explicitamente o contrato individual de `HealthCard` apresentado pelo MESTRE.

```text
C3_HEALTH_CARD=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02_STARTED=NO
```

## Contrato congelado

O `HealthCard` apresenta saúde operacional/técnica de uma entidade com estado canônico e evidências mínimas. Ele **não é o motor que calcula saúde**.

```text
HEALTH_CARD != HEALTH_ENGINE
```

Anatomia canônica:

```text
ENTITY.............. obrigatório
STATUS.............. obrigatório quando conhecido
SUMMARY............. opcional
SIGNALS............. 0–3 evidências principais
LAST_UPDATED........ obrigatório quando saúde é temporal
SOURCE_STATE........ obrigatório conceitualmente
ACTION.............. opcional
```

Estados suportados:

```text
OPERATIONAL
DEGRADED
ERROR / DOWN
OFFLINE
TELEMETRY_UNAVAILABLE
UNKNOWN
```

Guardrails semânticos congelados:

```text
NO_SOURCE -> SUCCESS...................... PROIBIDO
TELEMETRY_UNAVAILABLE -> HEALTHY.......... PROIBIDO
CHECK_ERROR -> TARGET_DOWN................ PROIBIDO
OFFLINE = ERROR........................... PROIBIDO
BRAND_GREEN = HEALTHY..................... PROIBIDO
HEALTH_CARD_DECIDES_HEALTH................ PROIBIDO
HEALTH_CARD_DECIDES_STALE................. PROIBIDO
METRIC_WITHOUT_SOURCE..................... PROIBIDO
```

Regras aprovadas:

- `OPERATIONAL` exige evidência atual suficiente segundo regra externa;
- `DEGRADED` significa funcionamento com capacidade reduzida ou indicador fora do esperado;
- `ERROR/DOWN` exige evidência concreta de falha do alvo;
- `OFFLINE` exige evidência conhecida de perda de comunicação;
- `TELEMETRY_UNAVAILABLE` significa incapacidade de observar o estado, não falha do alvo;
- `UNKNOWN` é estado legítimo quando faltam dados suficientes;
- falha da consulta de health não pode ser convertida automaticamente em falha do serviço monitorado;
- dados antigos não podem continuar aparentando saúde atual; regra externa decide stale/TTL;
- evidências devem ser resumidas a 0–3 sinais; detalhe adicional segue para superfície apropriada;
- `StatusBadge`, `MetricCard` e futuramente `LastUpdated` podem compor o card;
- ação de detalhes é opcional e explícita; o card não é clicável por padrão;
- RBAC/redaction são obrigatórios; não expor IP interno, hostname sensível, stack trace, segredos ou dados biométricos;
- responsividade ocorre por reorganização, não por encolhimento indiscriminado.

## Testes futuros previstos

```text
UNITÁRIOS
- Operational
- Degraded
- Error/Down
- Offline
- TelemetryUnavailable
- Unknown
- signals
- summary
- integração visual com LastUpdated

INTEGRAÇÃO
- HealthCard + StatusBadge
- HealthCard + MetricCard
- HealthCard + LastUpdated
- HealthCard + RBAC
- HealthCard + DetailDrawer
- HealthCard + endpoint de health

REGRESSÃO SEMÂNTICA
- NO_SOURCE != SUCCESS
- TELEMETRY_UNAVAILABLE != HEALTHY
- CHECK_REQUEST_ERROR != TARGET_DOWN
- OFFLINE != ERROR
- BRAND_GREEN != HEALTHY
- STALE_DATA != CURRENT_DATA

RESPONSIVO/A11Y
- 360 / 768 / 1024 / 1440+
- zoom 200%
- screen reader
- teclado na ação opcional
- contraste
- reflow
```

## Continuidade

```text
C1_STATUS_BADGE=FROZEN_INDIVIDUALLY
C2_METRIC_CARD=FROZEN_INDIVIDUALLY
C3_HEALTH_CARD=FROZEN_INDIVIDUALLY
NEXT_OFFICIAL_ITEM=C4_LAST_UPDATED_COMPONENT_REVIEW
```

Nenhuma implementação visual ou mudança em código de produção é autorizada por este checkpoint.
