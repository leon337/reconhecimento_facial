# NF-01 — Catalog Completeness RC — H7 — Responsividade e dimensionamento

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
H7_RESPONSIVE_DIMENSIONAL_COHERENCE=APPROVED_BY_LEANDRO
H7_STATUS=COMPLETE
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H8_TEMPORAL_CONCURRENCY_STALE_RESPONSE_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela a coerência transversal de responsividade, dimensionamento, reflow, container-awareness, zoom, teclado virtual, orientação e safe areas para a NF-01. Não autoriza implementação visual, produção, NF-02 ou merge.

## Princípio responsivo

```text
RESPONSIVE != SHRINK_DESKTOP
RESPONSIVE = REORGANIZE + REDISTRIBUTE + LIMIT + EXPAND + COLLAPSE
COMPONENT_SPACE != VIEWPORT_WIDTH
REUSABLE_COMPONENT => PREFER_CONTAINER_AWARE_LAYOUT_WHEN_APPROPRIATE
```

`360 / 768 / 1024 / 1440+` permanecem alvos mínimos de teste, não quatro interfaces rígidas. Larguras intermediárias também são obrigatórias.

## Breakpoints e conteúdo

```text
TEST_TARGET != ONLY_BREAKPOINT_ALLOWED
DEVICE_NAME != BREAKPOINT_ARCHITECTURE
CONTENT_OR_FUNCTIONAL_PRESSURE => LAYOUT_TRANSITION
INTERMEDIATE_WIDTHS => REQUIRED_VALIDATION
```

Breakpoints estruturais devem nascer da perda de legibilidade, espaço útil ou funcionalidade, não do nome do dispositivo.

## Política dimensional

```text
REM => BASE_DIMENSION_UNIT
FR_MINMAX => GRID_DISTRIBUTION
CLAMP => BOUNDED_FLUID_SIZING
CONTAINER_QUERY => COMPONENT_SPACE_ADAPTATION
CQI_CH_PERCENT => USE_WHEN_SEMANTICALLY_APPROPRIATE
VW_DVH => VIEWPORT_WHEN_NEEDED_AND_BOUNDED
PX => TECHNICAL_EXCEPTION_NOT_GENERAL_LAYOUT_POLICY
FIXED_PIXEL_LAYOUT_AS_GENERAL_POLICY=PROHIBITED
```

`px` não é universalmente proibido; borda de `1px` e outras exceções técnicas continuam permitidas quando justificadas.

## Shell e largura útil

```text
SIDEBAR_COLLAPSE => RELEASED_WIDTH_RETURNS_TO_MAIN_CONTENT
PERMANENT_DEAD_GUTTER_AFTER_COLLAPSE=PROHIBITED
VERY_WIDE_FORM => COMFORTABLE_EDITING_WIDTH
EXTRA_DASHBOARD_SPACE => USEFUL_CONTEXT_NOT_DECORATIVE_STRETCH
```

A sidebar continua com referências fluidas do Design System e o `MainWorkspace` usa o espaço liberado imediatamente.

## Tipografia e legibilidade

```text
FLUID_SIZE => SENSIBLE_MIN_MAX
UNBOUNDED_VIEWPORT_FONT_SCALING=PROHIBITED
LONG_TEXT => READABILITY_LIMIT_WHEN_APPROPRIATE
READABILITY_LIMIT => CONTENT_DEPENDENT
```

## Formulários

```text
RESPONSIVE_FORM_GRID => ONE_TO_THREE_COLUMNS_BY_AVAILABLE_SPACE
RIGID_PER_FIELD_PIXEL_WIDTH=PROHIBITED
SEMANTIC_FIELD_WIDTH => GRID_RELATIONSHIP_AND_AVAILABLE_SPACE
SEMANTIC_DOM_ORDER => PRESERVED
```

Mudança de colunas nunca altera a ordem lógica, de leitura ou foco congelada em H6.

## Mobile

```text
MOBILE != SHRUNK_DESKTOP
MOBILE_SIDEBAR => OVERLAY
MOBILE_WIZARD => SIMPLIFIED_PRESENTATION_WITH_SEMANTICS_PRESERVED
MOBILE_FORM => SINGLE_COLUMN_WHEN_REQUIRED_BY_SPACE
MOBILE_PRIMARY_ACTION => MAY_USE_AVAILABLE_WIDTH
MOBILE_DRAWER => FULL_OR_NEAR_FULL_OVERLAY_WHEN_NEEDED
```

O `HorizontalStepper` pode simplificar sua representação quando o espaço for insuficiente, mas sem perder `Etapa X de 8`, estados e acesso textual às etapas.

## DataTable e informação necessária

```text
MOBILE_TABLE != DESKTOP_TABLE_SQUEEZED
MOBILE_TABLE => SUMMARY_DETAIL_ADAPTATION_WHEN_NEEDED
RESPONSIVE_RELOCATION=ALLOWED
RESPONSIVE_LOSS_OF_REQUIRED_INFORMATION=PROHIBITED
PAGE_LEVEL_HORIZONTAL_OVERFLOW=PROHIBITED
CONTROLLED_COMPONENT_OVERFLOW => EXCEPTION_NOT_BASELINE
```

## Drawers, modais e cards

```text
DRAWER_LAYOUT => AVAILABLE_SPACE_AWARE
DETAIL_DRAWER => SIDE_MODAL_OR_FULL_SCREEN_ACCORDING_TO_SPACE
MODAL => FIT_AVAILABLE_SAFE_AREA
CARD_LAYOUT => MIN_USEFUL_WIDTH + AVAILABLE_CONTAINER
CARD_EXPANSION => LIMITED_BY_CONTENT_UTILITY
BACKGROUND_CONTENT => MUST_NOT_BE_FORCED_BELOW_USABLE_WIDTH
```

## Touch targets

```text
INTERACTIVE_TARGET => COMFORTABLE_TOUCH_SIZE
ICON_VISUAL_SIZE != INTERACTION_TARGET_SIZE
```

A referência aproximada de 44 CSS px permanece como área confortável quando aplicável, preferencialmente expressa em `rem`.

## Zoom e reflow

```text
ZOOM_200 => FUNCTIONAL_REFLOW_REQUIRED
ZOOM_200 => NO_CLIPPED_TEXT
ZOOM_200 => NO_LOST_ACTIONS
ZOOM_200 => NO_OVERLAPPING_SURFACES
PHYSICAL_SCREEN_SIZE != AVAILABLE_CSS_SPACE
```

Zoom pode naturalmente acionar comportamentos antes associados a containers mais estreitos.

## Teclado virtual e StickyFormActions

```text
VIRTUAL_KEYBOARD_OPEN => ACTIVE_FIELD_REMAINS_VISIBLE_AND_OPERABLE
STICKY != FIXED_AT_ALL_COSTS
STICKY_FORM_ACTIONS => MAY_REFLOW_OR_RETURN_TO_NORMAL_FLOW
SAFE_AREA => DEVICE_ENVIRONMENT_AWARE
MOBILE_VIEWPORT_HEIGHT => PREFER_DYNAMIC_SAFE_MECHANISM_WHEN_NEEDED
```

`dvh`, safe-area, `scroll-padding` e reorganização das ações permanecem ferramentas permitidas quando necessárias.

## Orientação e estado da tarefa

```text
ORIENTATION_CHANGE => REFLOW
ORIENTATION_CHANGE => NO_UNNECESSARY_TASK_STATE_RESET
```

Troca portrait/landscape não deve resetar formulário, etapa, câmera ou contexto sem necessidade técnica real.

## Câmera e mídia

```text
CAMERA_PREVIEW => PRESERVE_ASPECT_RATIO
RESPONSIVE_LAYOUT => NO_CAMERA_DISTORTION
LAYOUT_ROTATION != IDENTITY_OR_LIVENESS_DECISION
MEDIA => MUST_NOT_FORCE_PAGE_OVERFLOW
```

## Composição responsiva

```text
BREADCRUMB_COMPACTION => PRESERVE_LOCATION_MEANING
PAGE_HEADER => MAY_STACK_ACTIONS_WITHOUT_SEMANTIC_LOSS
FILTERS_COLLAPSED != ACTIVE_FILTERS_HIDDEN
SEARCH => RESPONSIVE_WIDTH_WITH_ACCESSIBLE_NAME_PRESERVED
```

## Testes futuros obrigatórios

### Unitários

- `ResponsiveFormGrid` em containers largos/estreitos e ordem semântica preservada;
- sidebar expandida/compacta com recuperação de largura;
- drawer side/overlay;
- stepper detalhado/simplificado;
- `StickyFormActions` em viewport normal e viewport restrito pelo teclado virtual.

### Integração

- composição `AppShell → Sidebar → MainWorkspace → PageHeader → Search/Filter → DataTable → DetailDrawer`;
- 360 / 768 / 1024 / 1440+;
- larguras intermediárias;
- zoom 200%;
- portrait/landscape;
- teclado mobile aberto;
- sidebar expandida/compacta;
- drawer aberto/fechado.

### Regressão

```text
RESPONSIVE_SHRINKS_DESKTOP_ONLY=NO
FOUR_RIGID_LAYOUTS_ONLY=NO
INTERMEDIATE_WIDTH_BREAKAGE=NO
PERMANENT_SIDEBAR_DEAD_SPACE=NO
RIGID_FIELD_PIXEL_WIDTHS=NO
MOBILE_SQUEEZED_TABLE=NO
REQUIRED_INFO_LOST_DUE_TO_WIDTH=NO
PAGE_HORIZONTAL_OVERFLOW=NO
ZOOM_200_CLIPPING=NO
STICKY_ACTIONS_COVER_ACTIVE_FIELD=NO
ORIENTATION_RESETS_TASK_STATE=NO
CAMERA_PREVIEW_DISTORTION=NO
CSS_REORDER_BREAKS_SEMANTIC_ORDER=NO
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
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H8_TEMPORAL_CONCURRENCY_STALE_RESPONSE_COHERENCE
VISUAL_IMPLEMENTATION=NOT_YET
```
