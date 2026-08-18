# NF-01 — Revisão individual C1 StatusBadge

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Componente:** `C1 — StatusBadge`  
**Gate humano:** LEANDRO  
**Data:** 2026-08-17

---

## Resultado do HUMAN_GATE

```text
C1_STATUS_BADGE=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
```

## Contrato congelado

```text
estado categórico curto................. YES
métrica numérica........................ NO
ação/interação.......................... NO

texto visível obrigatório............... YES
ícone opcional.......................... YES
cor como única informação............... NO

tones:
neutral................................. YES
info.................................... YES
success................................. YES
warning................................. YES
degraded................................ YES
error................................... YES
offline................................. YES
unknown................................. YES

label separado de tone.................. YES

NO_SOURCE -> UNKNOWN.................... YES
NO_SOURCE -> SUCCESS.................... NO

WARNING != DEGRADED..................... YES
OFFLINE != ERROR........................ YES
BRAND_GREEN != HEALTHY.................. YES

SM / MD................................. YES
badge gigante........................... NO

loading dentro do badge................. NO_BY_DEFAULT
status derivado pelo badge.............. NO

tooltip opcional........................ YES
tooltip obrigatório para entender....... NO

RBAC respeitado......................... YES
revelar estado proibido................. NO

StatusBadge clicável.................... NO
```

## Regras semânticas

- `StatusBadge` apresenta um estado já calculado; não funciona como motor de decisão de saúde.
- ausência de fonte/telemetria nunca deve ser convertida em sucesso.
- `UNKNOWN`, `OFFLINE`, `WARNING`, `DEGRADED` e `ERROR` são estados semanticamente distintos.
- verde institucional da marca não implica saúde operacional.
- o significado principal é textual; cor e ícone são reforços.
- estado e `tone` são independentes: o mesmo rótulo pode ter semântica diferente em domínios diferentes.
- informações sem autorização RBAC não devem ser reveladas por meio do badge.

## Testes futuros obrigatórios

```text
UNIT
- label/tone
- icon optional
- SM/MD
- unknown/offline/degraded
- non-interactive semantics

INTEGRATION
- StatusBadge + DataTable
- StatusBadge + HealthCard
- StatusBadge + DetailDrawer
- StatusBadge + RBAC

A11Y / SEMANTIC REGRESSION
- visible text
- screen reader context
- contrast
- no color-only state
- NO_SOURCE -> UNKNOWN
- NO_SOURCE -> SUCCESS forbidden
- OFFLINE != ERROR
- WARNING != DEGRADED
- BRAND_GREEN != HEALTHY
```

## Continuidade

```text
PHASE_B_COMPONENT_REVIEW=COMPLETE
C1_STATUS_BADGE=FROZEN_INDIVIDUALLY
NEXT_OFFICIAL_ITEM=C2_METRIC_CARD_COMPONENT_REVIEW
```

Nenhum código de produção, backend, migração, IA, observabilidade backend, deploy ou merge foi autorizado por este gate.
