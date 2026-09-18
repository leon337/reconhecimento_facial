# NF-01 — Component Review E3 — Skeleton

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
E3_SKELETON=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_E_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=E4_DEGRADATION_BANNER_COMPONENT_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `Skeleton` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`Skeleton` comunica que a estrutura da informação é conhecida, mas os dados ainda estão sendo carregados.

```text
REQUEST
   ↓
PENDING
   ↓
estrutura conhecida
   ↓
Skeleton
   ↓
RESOLVED
   ├── dados → conteúdo
   ├── zero  → EmptyState
   └── falha → ErrorState
```

```text
SKELETON != DATA
SKELETON != EMPTY_STATE
SKELETON != ERROR_STATE
SKELETON != PROGRESS_BAR
```

## Semântica congelada

```text
LOADING => NO_FAKE_VALUE
LOADING => NO_FAKE_STATUS
LOADING => NO_FAKE_SUCCESS
LOADING != HEALTHY
```

O Skeleton antecipa forma e espaço, nunca valores, estados ou sucesso fictícios.

## Estrutura e estabilidade visual

```text
SKELETON_LAYOUT_APPROX_FINAL_LAYOUT......... REQUIRED
AVOID_UNNECESSARY_LAYOUT_SHIFT.............. REQUIRED
RESPONSIVE_LOGIC_MATCHES_FINAL_COMPONENT.... REQUIRED
USE_WHEN_FINAL_STRUCTURE_IS_PREDICTABLE..... REQUIRED
```

A geometria deve representar aproximadamente altura, largura, espaçamento, grid, cards e linhas do conteúdo final. Quando a estrutura final for desconhecida, outro indicador de carregamento pode ser mais adequado.

## Primeira carga e refresh

```text
INITIAL_LOAD != BACKGROUND_REFRESH........... REQUIRED_DISTINCTION
INITIAL_LOAD_SKELETON........................ SUPPORTED
BACKGROUND_REFRESH_ERASES_VALID_DATA......... NOT_DEFAULT
VALID_PREVIOUS_DATA_MAY_REMAIN_VISIBLE....... ALLOWED_WHEN_IDENTIFIED
PAGE_RENDER_TIME != DATA_UPDATE_TIME......... PRESERVED
```

Durante refresh, dados anteriores podem permanecer quando ainda são úteis e claramente identificados. Iniciar uma atualização não redefine `LastUpdated`.

## Carregamento parcial

```text
PARTIAL_LOADING => LOCALIZE_SKELETON......... REQUIRED
UNNECESSARY_PAGE_WIDE_SKELETON............... PROHIBITED
```

Se apenas uma seção estiver carregando, somente a região correspondente deve usar Skeleton.

## Interação

```text
SKELETON_IS_INTERACTIVE...................... FALSE
SKELETON_IS_FOCUSABLE........................ FALSE
SKELETON_HAS_ACTIONS......................... FALSE
```

Skeleton é visualmente transitório e inerte. Não deve simular botões ou ações utilizáveis.

## RBAC, privacidade e estrutura autorizada

```text
TENANT_RBAC_SCOPE => AUTHORIZED_STRUCTURE => SKELETON
SKELETON_STRUCTURE => SAME_AUTHORIZED_SCOPE
UNAUTHORIZED_STRUCTURE_DISCLOSURE............ PROHIBITED
```

Mesmo sem valores, a estrutura pode revelar atributos sensíveis; por isso RBAC deve ser resolvido antes da composição do Skeleton.

## Progresso, timeout e duração

```text
KNOWN_PROGRESS != SKELETON................... REQUIRED
SKELETON != TIMEOUT_ENGINE................... REQUIRED
SKELETON_AS_FINAL_STATE...................... PROHIBITED
INFINITE_SKELETON............................ PROHIBITED
AVOID_SKELETON_FLASH......................... REQUIRED
```

Skeleton representa espera estrutural indeterminada. Progresso mensurável exige outro padrão. Timeout/offline/error são classificados pela camada de operação e devem substituir o Skeleton quando aplicável.

## Movimento e acessibilidade

```text
ANIMATION.................................... OPTIONAL
AGGRESSIVE_SHIMMER........................... PROHIBITED
REDUCED_MOTION => NO_REQUIRED_ANIMATION...... REQUIRED
SKELETON_SHAPES_IN_A11Y_TREE................. PROHIBITED
ARIA_BUSY_CONTEXTUAL......................... ALLOWED_AND_RECOMMENDED_WHEN_APPLICABLE
EXCESSIVE_LOADING_ANNOUNCEMENTS.............. PROHIBITED
```

As formas visuais devem ser decorativas para tecnologia assistiva. A região real pode comunicar `aria-busy="true"` ou estado equivalente, sem anunciar cada retângulo individualmente.

## Integrações previstas

```text
Skeleton + MetricCard
Skeleton + HealthCard
Skeleton + DataTable
Skeleton + Search
Skeleton + FilterBar
Skeleton → EmptyState
Skeleton → ErrorState
Skeleton → conteúdo
Skeleton + RBAC
Skeleton + LastUpdated
```

## Testes futuros obrigatórios

### Unitários

- render básico e variantes estruturais;
- Skeleton inerte e não focável;
- ausência de valores/status fictícios;
- formas fora da árvore de acessibilidade;
- reduced motion;
- estrutura autorizada por RBAC.

### Integração

- `Skeleton → conteúdo`;
- `Skeleton → EmptyState`;
- `Skeleton → ErrorState`;
- primeira carga versus background refresh;
- loading parcial localizado;
- Search/Filter/DataTable sem stale response vencendo estado atual.

### Regressão semântica

```text
LOADING != EMPTY
LOADING != ERROR
LOADING != SUCCESS
LOADING != HEALTHY
NO_FAKE_VALUE
NO_FAKE_STATUS
INITIAL_LOAD != BACKGROUND_REFRESH
```

### Responsivo e acessibilidade

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- `prefers-reduced-motion`;
- screen reader;
- `aria-busy` contextual;
- ausência de tab stops fictícios;
- layout shift reduzido.

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
E1_EMPTY_STATE=FROZEN_INDIVIDUALLY
E2_ERROR_STATE=FROZEN_INDIVIDUALLY
E3_SKELETON=FROZEN_INDIVIDUALLY
PHASE_E_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=E4_DEGRADATION_BANNER_COMPONENT_REVIEW
```
