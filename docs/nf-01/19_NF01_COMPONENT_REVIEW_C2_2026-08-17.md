# NF-01 — Revisão individual C2 MetricCard

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Componente:** `C2 — MetricCard`  
**Gate humano:** LEANDRO  
**Decisão:** `APPROVED`  
**Status:** `FROZEN_INDIVIDUALLY`

---

## Contrato congelado

```text
C2_METRIC_CARD

valor quantitativo...................... ✅
estado categórico....................... ❌
motor de saúde.......................... ❌

label................................... ✅ obrigatório
valor................................... ✅ quando disponível
unidade................................. ✅ quando aplicável
período/contexto........................ ✅ quando necessário

NO_DATA = ZERO.......................... ❌
NO_SOURCE => NO_METRIC.................. ✅

LOADING................................. ✅
READY................................... ✅
NO_DATA................................. ✅
ERROR................................... ✅
STALE................................... ✅

MetricCard decide stale................. ❌

delta................................... ✅ opcional
base da comparação...................... ✅ obrigatória com delta
UP = POSITIVE........................... ❌
DOWN = NEGATIVE......................... ❌

LastUpdated integration................. ✅
RBAC/scope antes da métrica............. ✅

clicável por padrão..................... ❌
ação explícita.......................... ✅ quando necessária

responsivo por reorganização............ ✅
encolher tipografia para caber.......... ❌

valor fictício durante loading.......... ❌
zero usado para ausência de dados....... ❌
```

## Regras complementares congeladas

- `MetricCard` apresenta valor quantitativo + contexto, não estado categórico.
- `0` é um valor válido e nunca representa automaticamente ausência de dados.
- ausência de fonte confiável impede a apresentação de uma métrica inventada.
- unidade e período devem ser explícitos quando necessários para interpretação.
- tendência e semântica são independentes: `UP` não significa automaticamente positivo e `DOWN` não significa automaticamente negativo.
- comparação deve declarar a base (`vs ontem`, `vs média de 7 dias`, etc.).
- `STALE`, `ERROR` e `NO_DATA` são estados distintos.
- `MetricCard` não decide sozinho quando um dado se tornou stale.
- RBAC/escopo deve restringir a consulta antes da composição da métrica.
- loading usa `Skeleton`; não exibe valores fictícios.
- responsividade reorganiza os cards; não reduz tipografia indiscriminadamente.
- integração futura com `LastUpdated` é obrigatória quando recência fizer parte do significado.

## Testes futuros previstos

```text
UNITÁRIOS
- value + label
- unidade/formatação
- zero válido
- NO_DATA
- ERROR
- STALE
- delta + base de comparação
- trend direction != semantic sentiment

INTEGRAÇÃO
- MetricCard + fonte de dados
- MetricCard + LastUpdated
- MetricCard + Skeleton
- MetricCard + RBAC
- MetricCard + Dashboard grid

REGRESSÃO SEMÂNTICA
- NO_DATA != 0
- STALE != READY atual
- UP != POSITIVE
- DOWN != NEGATIVE
- NO_SOURCE => NO_METRIC

RESPONSIVO / A11Y
- 360 / 768 / 1024 / 1440+
- zoom 200%
- screen reader
- valores longos
- localização pt-BR
```

## Gate

```text
C2_METRIC_CARD=FROZEN_INDIVIDUALLY
APPROVED_BY=LEANDRO
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02_STARTED=NO
PR32_MERGE=BLOCKED
NEXT_OFFICIAL_ITEM=C3_HEALTH_CARD_COMPONENT_REVIEW
```
