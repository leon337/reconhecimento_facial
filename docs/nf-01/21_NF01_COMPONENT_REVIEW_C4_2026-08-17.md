# NF-01 — Revisão individual C4 — LastUpdated

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data do gate:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate humano

LEANDRO aprovou explicitamente o contrato individual do componente `C4 — LastUpdated`.

```text
C4_LAST_UPDATED=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_C_COMPONENT_REVIEW=COMPLETE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02_STARTED=NO
```

---

## Propósito

`LastUpdated` comunica a recência real de uma informação. Ele responde “de quando é este dado?”, sem decidir saúde, validade, stale ou erro de domínio.

```text
LAST_UPDATED != FRESHNESS_ENGINE
PAGE_RENDER_TIME != DATA_UPDATE_TIME
NO_TIMESTAMP != NOW
```

---

## Contrato congelado

```text
propósito: comunicar recência............. YES
decidir saúde............................. NO
decidir stale............................. NO

timestamp real da fonte................... YES
tempo de renderização como timestamp...... NO

relativo.................................. YES
absoluto.................................. YES
relativo + absoluto....................... YES quando útil

NO_TIMESTAMP -> UNKNOWN................... YES
NO_TIMESTAMP -> NOW........................ NO
PAGE_REFRESH -> NOVO UPDATED_AT............ NO

timezone explícito/política definida....... YES
timestamp estruturado..................... YES
string visual como fonte de verdade........ NO

data civil = timestamp.................... NO

freshness tone externo.................... YES
CURRENT / STALE / EXPIRED / UNKNOWN....... YES quando fornecidos
componente calcula TTL.................... NO

texto relativo pode envelhecer............ YES
aria-live a cada atualização.............. NO

LastUpdated + MetricCard.................. YES
LastUpdated + HealthCard.................. YES

RBAC herdado do dado...................... YES
interação própria......................... NO
```

---

## Guardrails temporais

- o timestamp apresentado deve corresponder ao evento real que produziu/atualizou o dado;
- refresh/renderização da página não redefine a recência do dado;
- ausência de timestamp não pode ser apresentada como “agora” ou “recentemente”;
- a classificação `CURRENT/STALE/EXPIRED/UNKNOWN` é fornecida por regra externa do domínio;
- TTL varia por tipo de informação e não pertence ao componente;
- datas civis e timestamps absolutos permanecem semanticamente distintos;
- política de timezone deve ser explícita;
- relógio do dispositivo não é fonte canônica automática;
- atualização visual de tempo relativo não deve gerar anúncios `aria-live` repetitivos.

---

## Estados e apresentação

```text
KNOWN
UNKNOWN
```

Freshness opcional recebido externamente:

```text
CURRENT
STALE
EXPIRED
UNKNOWN
```

Formatos permitidos conforme contexto:

```text
Atualizado há 18 s
Atualizado há 4 min
17/08/2026 · 06:43:18
Atualizado há 4 min + timestamp absoluto em contexto de detalhe/auditoria
```

---

## Acessibilidade e responsividade

- componente textual, não interativo;
- não recebe foco por padrão;
- não depende de cor;
- sem `aria-live` a cada mudança de segundo/minuto;
- formatação localizada para PT-BR na apresentação;
- dado temporal permanece estruturado internamente;
- responsividade ocorre por reflow, sem reduzir tipografia abaixo dos tokens.

---

## Testes futuros obrigatórios

### Unitários

- timestamp válido;
- timestamp ausente;
- formato relativo;
- formato absoluto;
- timezone;
- locale pt-BR;
- `CURRENT/STALE/EXPIRED/UNKNOWN` recebidos externamente;
- componente não recalcula freshness de domínio.

### Integração

- `LastUpdated + MetricCard`;
- `LastUpdated + HealthCard`;
- `LastUpdated + DataTable`;
- `LastUpdated + DetailDrawer`;
- timestamp de backend;
- referência temporal confiável.

### Regressão semântica

```text
PAGE_RENDER_TIME != DATA_UPDATE_TIME
NO_TIMESTAMP != NOW
LAST_UPDATED != FRESHNESS_ENGINE
CLIENT_CLOCK != CANONICAL_TIMESTAMP
STALE != ERROR
```

### Responsivo / A11Y

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- screen reader;
- texto localizado;
- timezone explícito;
- ausência de anúncios repetitivos.

---

## Resultado

```text
C1_STATUS_BADGE=FROZEN_INDIVIDUALLY
C2_METRIC_CARD=FROZEN_INDIVIDUALLY
C3_HEALTH_CARD=FROZEN_INDIVIDUALLY
C4_LAST_UPDATED=FROZEN_INDIVIDUALLY
PHASE_C_COMPONENT_REVIEW=COMPLETE
NEXT_OFFICIAL_ITEM=D1_SEARCH_COMPONENT_REVIEW
```

A aprovação de C4 encerra conceitualmente a Fase C. Nenhuma implementação visual ou alteração de produção está autorizada por este registro.