# NF-01 — Roadmap oficial do trabalho restante

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Status:** `IN_PROGRESS`  
**Produção:** inalterada  
**NF-02:** não iniciada  
**Merge:** não autorizado  
**Gate humano final:** LEANDRO

---

## Estado consolidado

```text
NF01_STATUS=IN_PROGRESS
CANONICAL_DECISIONS=DOCUMENTED
PRODUCTION_CODE_CHANGED=NO
NF02_STARTED=NO
PR32_MERGED=NO
FINAL_HUMAN_GATE=NOT_READY
COMPONENT_CATALOG_BASELINE=FROZEN
COMPONENT_INDIVIDUAL_REVIEW=IN_PROGRESS
PHASE_A_COMPONENT_REVIEW=COMPLETE
PHASE_B_COMPONENT_REVIEW=COMPLETE
PHASE_C_COMPONENT_REVIEW=COMPLETE
```

### RC transversal

```text
CRITICAL_GAPS_CLOSED=6/6
HIGH_GAPS_CLOSED=9/9
MEDIUM_GAPS_CLOSED=6/6
```

## Componentes congelados

```text
[x] CollapsibleSidebar
[x] HorizontalStepper
[x] ContextDrawer
[x] StickyFormActions
[x] ResponsiveFormGrid
[x] FormSection + Progressive Disclosure
[x] FieldGroup / InlineHelp / ValidationMessage
[x] SearchableCombobox / EntityPicker
[x] Date / Time / Period Picker
[x] AppShell
[x] TopHeader
[x] Breadcrumb
[x] PageHeader
[x] Button
[x] IconButton
[x] Tooltip
[x] Tabs
[x] StatusBadge
[x] MetricCard
[x] HealthCard
[x] LastUpdated
```

## Fase A — Estrutura

```text
[x] A1 AppShell
[x] A2 TopHeader
[x] A3 Breadcrumb
[x] A4 PageHeader
```

## Fase B — Ações, navegação local e ajuda

```text
[x] B1 Button
[x] B2 IconButton
[x] B3 Tooltip
[x] B4 Tabs
```

## Fase C — Status, métricas e recência

```text
[x] C1 StatusBadge
[x] C2 MetricCard
[x] C3 HealthCard
[x] C4 LastUpdated
```

Guardrails:

```text
BRAND_GREEN != HEALTHY
TELEMETRY_UNAVAILABLE != SUCCESS
NO_SOURCE => NO_INVENTED_STATUS
NO_DATA != ZERO
NO_SOURCE => NO_METRIC
CHECK_ERROR != TARGET_DOWN
OFFLINE != ERROR
STALE_DATA != CURRENT_DATA
LAST_UPDATED != FRESHNESS_ENGINE
PAGE_RENDER_TIME != DATA_UPDATE_TIME
NO_TIMESTAMP != NOW
CLIENT_CLOCK != CANONICAL_TIMESTAMP
```

```text
PHASE_C_COMPONENT_REVIEW=COMPLETE
```

## Fase D — Busca, filtros e dados tabulares

```text
[ ] D1 Search
[ ] D2 FilterBar
[ ] D3 DataTable
[ ] D4 Pagination
```

**Próxima ação oficial:** `D1 — revisar Search como componente`, sem aplicar visualmente às telas.

## Fase E — Estados de sistema e feedback

```text
[ ] E1 EmptyState
[ ] E2 ErrorState
[ ] E3 Skeleton
[ ] E4 DegradationBanner
[~] E5 Toast — revisão de integração/coerência
```

## Fase F — Overlays, confirmação e histórico

```text
[ ] F1 DetailDrawer
[ ] F2 ConfirmationModal
[ ] F3 EventTimeline
```

## Fase G — Câmera e resultado de ponto

```text
[ ] G1 CameraPanel
[ ] G2 PunchResult
```

## Fase H — RC de completude do catálogo

```text
[ ] H1–H10 revisão transversal final do catálogo
```

## Fase I — Design Lab / AppShell

```text
[ ] I1–I9 materialização e validação do AppShell
```

## Fase J — Dashboard

```text
[ ] J1–J8 reconciliação visual/semântica
```

## Fase K — Funcionários

```text
[ ] K1–K9 reconciliação visual/semântica
```

## Fase L — Novo Funcionário V2

```text
[ ] L1–L17 reconciliação do onboarding de 8 etapas
```

## Fase M — Coerência entre telas

```text
[ ] M1–M8 coerência transversal
```

## Fase N — Validação do Design Lab

```text
RESPONSIVIDADE: 360 / 768 / 1024 / 1440+ / intermediários / teclado mobile
ACESSIBILIDADE: teclado / foco / zoom 200% / reduced motion / ARIA / screen reader / contraste
TESTES FUTUROS: UNITÁRIOS / INTEGRAÇÃO / REGRESSÃO / RESPONSIVO / A11Y / SEGURANÇA
```

## Fase O — Evidências, auditoria e fechamento

```text
[ ] O1–O10 evidências, revisão independente, PR e Gate humano final
```

## Guardrails permanentes

```text
DO_NOT_MERGE_WITHOUT_EXPLICIT_LEANDRO_APPROVAL
DO_NOT_START_NF02
DO_NOT_CHANGE_PRODUCTION_CODE
DO_NOT_CHANGE_BACKEND
DO_NOT_MIGRATE_PONTO_TO_ATTENDANCE_EVENT
DO_NOT_IMPLEMENT_AI
DO_NOT_IMPLEMENT_OBSERVABILITY_BACKEND
DO_NOT_DEPLOY
DO_NOT_DECLARE_LEGAL_COMPLIANCE
DO_NOT_EDIT_DECISOES_CONGELADAS_MD
```

## Ponte para novo chat

Ler decisões canônicas, este roadmap, closeout, catálogo, especificação Novo Funcionário V2, checkpoints individuais recentes e PR #32/HEAD atual; depois continuar pelo primeiro item não concluído.

```text
NEXT_OFFICIAL_ITEM=D1_SEARCH_COMPONENT_REVIEW
VISUAL_IMPLEMENTATION=NOT_YET
```
