# NF-01 — Catalog Completeness RC — H9 — Coerência entre componentes e superfícies

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
H9_COMPONENT_SURFACE_COHERENCE=APPROVED_BY_LEANDRO
H9_STATUS=COMPLETE
NEW_COMPONENT_GAP_COUNT=0
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H10_CATALOG_COMPLETENESS_RC_CLOSEOUT
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação congela a coerência transversal entre componentes e superfícies da NF-01. Não autoriza implementação visual, alteração de produção, NF-02 ou merge.

## Princípio central

```text
CANONICAL_FACT
      ↓
MULTIPLE_UI_REPRESENTATIONS
      ↓
SAME_SEMANTIC_MEANING
```

Componentes podem representar o mesmo fato em contextos diferentes, mas não podem criar verdades alternativas.

```text
SAME_CANONICAL_FACT => SAME_SEMANTIC_MEANING
COMPONENT => NO_ALTERNATE_DOMAIN_TRUTH
```

## Fronteiras de responsabilidade preservadas

A composição não transforma componentes visuais em engines de domínio:

```text
StatusBadge != STATUS_ENGINE
MetricCard != METRIC_ENGINE
HealthCard != HEALTH_ENGINE
LastUpdated != FRESHNESS_ENGINE
ErrorSummary != VALIDATION_ENGINE
EventTimeline != EVENT_ENGINE
CameraPanel != RECOGNITION_ENGINE
PunchResult != PUNCH_ENGINE
```

## Dashboard e saúde

```text
SAME_SOURCE_DOMAIN => NO_CONTRADICTORY_STATE_PRESENTATION
LAST_UPDATED_SCOPE => MUST_MATCH_ASSOCIATED_DATA_SCOPE
TELEMETRY_UNAVAILABLE != HEALTHY
NO_SOURCE => NO_INVENTED_STATUS
NO_DATA != ZERO
```

Um `HealthCard`, `StatusBadge`, `MetricCard` e `LastUpdated` que representam a mesma capacidade devem permanecer semanticamente compatíveis. Fontes diferentes podem ter recências diferentes.

## Funcionários: query compartilhada

```text
QUERY_CONTEXT = SEARCH + FILTERS + SORT + PAGINATION_OR_CURSOR + AUTHORIZED_SCOPE
ROWS + TOTAL + PAGE + FILTER_COUNTS + EMPTY_STATE => SAME_QUERY_AND_SCOPE
```

Guardrails:

```text
CONFIRMED_ZERO_RESULT => EMPTY_STATE
CONFIRMED_ZERO_RESULT => NO_RESULT_PAGINATION
ZERO_ROWS_WITH_GLOBAL_TOTAL => PROHIBITED
EMPTY_STATE_WITH_ACTIVE_RESULT_PAGINATION => PROHIBITED
```

## Dados preservados e falha de refresh

Quando ainda existem dados utilizáveis:

```text
USABLE_PRIOR_DATA
+
REFRESH_FAILURE
→ PRESERVE_CONTENT
→ PRESERVE_LAST_CONFIRMED_TIMESTAMP
→ DEGRADATION_PRESENTATION
```

`ErrorState` não pode contradizer a realidade dizendo que nenhum dado foi carregado quando conteúdo anterior válido continua utilizável.

```text
PRIMARY_STATE_PRESENTATION => MUST_MATCH_USABLE_CONTENT_REALITY
```

## DataTable → DetailDrawer

Abrir e fechar detalhe deve preservar o contexto da lista:

```text
SEARCH
FILTERS
SORT
PAGE
SCROLL_OR_LOGICAL_POSITION_WHEN_APPLICABLE
```

Para a mesma versão da entidade:

```text
SAME_ENTITY_VERSION => SAME_CANONICAL_FACTS
```

Resposta obsoleta de outra entidade não pode atravessar para o drawer atual.

## Mutação e reconciliação entre superfícies

Linha de montagem:

```text
DetailDrawer
    ↓
ConfirmationModal when applicable
    ↓
backend revalidation
    ↓
canonical mutation result
    ↓
reconciliation
    ↓
DataTable / DetailDrawer / MetricCard / EventTimeline / other affected surfaces
    ↓
optional Toast
```

Congelado:

```text
CONFIRMED_MUTATION => AFFECTED_SURFACES_CONVERGE
SUCCESS_TOAST != STATE_RECONCILIATION
TOAST_BEFORE_CONFIRMED_MUTATION => PROHIBITED
```

Toast é feedback secundário, nunca substituto de reconciliação.

## Unknown outcome

```text
UNKNOWN_OUTCOME
→ PERSISTENT_RECONCILIATION
→ NO_FALSE_SUCCESS
→ NO_FALSE_FAILURE
→ NO_INVENTED_EVENT
→ NO_BLIND_WRITE_RETRY
```

Uma superfície não pode mostrar sucesso enquanto outra permanece em estado anterior ou desconhecido.

## Retry

CTAs como `Tentar novamente` somente são válidos quando H4/H5 classificarem a repetição como segura.

```text
GENERIC_WRITE_RETRY_ALWAYS_SAFE => NO
RETRY => OBEYS_H4_H5
UNKNOWN_OUTCOME => VERIFY_OR_RECONCILE
```

## Wizard e HorizontalStepper

O stepper representa a máquina de estados do wizard; não possui estado de domínio independente.

```text
STEP_VISUAL_STATE => DERIVED_FROM_CANONICAL_WIZARD_STATE
STEPPER_OWNS_WIZARD_STATE => NO
```

Uma etapa não pode aparecer `COMPLETED` enquanto possui erro bloqueante atual não reconciliado.

## Dependency invalidation / NEEDS_REVIEW

Mudança estrutural como relação, empresa ou unidade deve convergir entre:

```text
CANONICAL_DEPENDENCY_INVALIDATION
→ HorizontalStepper
→ ContextDrawer
→ Review surface
→ affected fields/sections
```

`NEEDS_REVIEW` não é apenas decoração de stepper.

## ErrorSummary + FormSection + FieldGroup

```text
ERROR_SUMMARY_ITEM
→ SAME_TARGET
→ SAME_CURRENT_ERROR
→ EXPAND_SECTION_WHEN_NEEDED
→ FOCUS_TARGET
```

Quando o erro é resolvido:

```text
RESOLVED_ERROR
→ ValidationMessage removed
→ ErrorSummary item removed
→ section indicator reevaluated
→ step state reevaluated
→ review state reevaluated
```

Congelado:

```text
RESOLVED_ERROR => NO_GHOST_ERROR_ACROSS_SURFACES
```

## ContextDrawer

```text
FORM => OWNS_EDITING
CONTEXT_DRAWER => SUMMARY_CONTEXT_NAVIGATION
CONTEXT_DRAWER != DUPLICATE_FORM
```

O drawer contextual não duplica campos obrigatórios editáveis nem cria uma segunda fonte de verdade do formulário.

## AppContext x empresa do vínculo

```text
APP_CONTEXT_PRESENTATION != EMPLOYMENT_RELATION_VALUE
APP_CONTEXT_CHANGE => NO_SILENT_FORM_MUTATION
```

O contexto administrativo do TopHeader e a empresa contratante do vínculo são conceitos independentes.

## RBAC coerente entre superfícies

Para a mesma capacidade:

```text
SAME_CAPABILITY => SAME_EFFECTIVE_AUTHORIZATION_RULE
```

PageHeader, DataTable, DetailDrawer, ContextDrawer, gatilhos de ConfirmationModal e demais superfícies não podem divergir sobre uma ação proibida.

```text
CONFIRMATION != AUTHORIZATION_REPAIR
```

Um modal de confirmação não torna legítima uma ação renderizada indevidamente.

## HealthCard + StatusBadge + DegradationBanner

Podem coexistir quando representam camadas diferentes da mesma condição, desde que não se contradigam.

```text
SAME_CAPABILITY_SAME_FACT => CONSISTENT_STATUS
TELEMETRY_UNAVAILABLE => NO_HEALTHY_INFERENCE
```

## EventTimeline

```text
USER_CLICK != DOMAIN_EVENT
NO_CANONICAL_EVENT => NO_TIMELINE_ITEM
```

Quando `PunchResult` e `EventTimeline` representam o mesmo evento:

```text
SAME_CANONICAL_EVENT_ID
→ SAME_SUBJECT
→ SAME_EVENT_TYPE
→ SAME_CANONICAL_TIMESTAMP
```

## CameraPanel + PunchResult

```text
CAMERA_CAPTURE_SUCCESS != PUNCH_SUCCESS
FACE_MATCH_SUCCESS != PUNCH_SUCCESS
PUNCH_SUCCESS => PERSISTENCE_CONFIRMED
```

A cadeia visual deve respeitar a cadeia de domínio:

```text
CameraPanel
→ capture
→ recognition/liveness
→ confirmed subject
→ punch operation
→ persistence
→ PunchResult
```

## Próxima pessoa / sessão compartilhada

```text
NEXT_USER
→ NO_PREVIOUS_USER_TRANSIENT_RESIDUE
```

Estado transitório da câmera, identidade reconhecida, resultado de ponto e mensagens da sessão anterior não atravessam para a próxima pessoa.

## AppShell administrativo e /punch

```text
SHARED_DESIGN_SYSTEM != SHARED_APPLICATION_SHELL
/punch => OUTSIDE_ADMIN_APPSHELL
```

Tokens e componentes podem ser compartilhados sem misturar jornadas administrativas com a jornada dedicada de registro de ponto.

## Responsividade

A composição visual pode mudar entre desktop/tablet/mobile, mas:

```text
RESPONSIVE_RECOMPOSITION != SEMANTIC_REINTERPRETATION
RESPONSIVE_RECOMPOSITION != AUTHORIZATION_CHANGE
```

Mesma entidade, mesma autorização, mesmo estado e mesmas regras permanecem válidos.

## Acessibilidade de composição

Cadeias como:

```text
DataTable
→ DetailDrawer
→ ConfirmationModal
→ close modal
→ DetailDrawer
→ close drawer
→ logical list context
```

devem manter foco e contexto conforme H6. Nenhuma superfície escondida permanece interativa.

## Prioridade de superfície

```text
FIELD_SPECIFIC_ERROR      → ValidationMessage
MULTIPLE_FORM_ERRORS      → ErrorSummary
SURFACE_OPERATION_FAILURE → ErrorState
PERSISTENT_DEGRADATION    → DegradationBanner
CATEGORICAL_STATE         → StatusBadge
SECONDARY_TRANSIENT       → Toast
HIGH_IMPACT_DECISION      → ConfirmationModal
```

Mantém-se:

```text
ONE_CONDITION => ONE_PRIMARY_PERSISTENT_PRESENTATION
CRITICAL_ERROR != TOAST_ONLY
PERSISTENT_OFFLINE != TOAST_ONLY
CONFLICT != TOAST_ONLY
UNKNOWN_OUTCOME != TOAST_ONLY
```

## Mínimo necessário e privacidade

Nenhuma composição autoriza ampliar dados além do necessário.

```text
SURFACE => SAME_AUTHORIZED_MINIMUM_NECESSARY_SCOPE
DETAIL_VIEW != PERMISSION_ESCALATION
TOOLTIP_TOAST_SCREEN_READER_CONTENT => NO_PROTECTED_DATA_BYPASS
```

## Temporalidade continua válida após reconciliação

```text
CROSS_SURFACE_RECONCILIATION => CURRENT_LOGICAL_CONTEXT_ONLY
STALE_ASYNC_RESULT => MUST_NOT_BREAK_RECONCILED_SURFACES
```

Se uma mutação antiga pode ter causado efeito backend, H5 ainda exige reconciliação; H8 impede apenas que seu resultado obsoleto contamine a superfície atual.

## Arquitetura de implementação

H9 não escolhe framework global de estado, event bus ou mecanismo específico.

```text
H9 != IMPLEMENTATION_ARCHITECTURE_SELECTION
SPECIFIC_GLOBAL_STATE_LIBRARY_FROZEN=NO
```

## Resultado de completude

```text
NEW_COMPONENT_GAP_COUNT=0
CROSS_SURFACE_COHERENCE_CONTRACT=FROZEN
```

Nenhum novo componente canônico foi identificado como necessário neste passe. O problema tratado por H9 é de composição e convergência entre as peças já catalogadas.

## Testes futuros

### Unitários / contratos compartilhados

```text
same fact → same semantic mapping
same permission → same action visibility
same query → same rows/count/page/empty
same entity version → same status
same event id → same event facts
same error → same target
```

### Integração

Linha administrativa:

```text
AppShell
→ Funcionários
→ Search + FilterBar
→ DataTable
→ DetailDrawer
→ ConfirmationModal
→ mutation
→ reconciliation
→ DataTable + Drawer + Timeline + Toast
```

Linha do onboarding:

```text
HorizontalStepper
→ FormSection
→ FieldGroup
→ EntityPicker
→ ErrorSummary
→ StickyFormActions
→ autosave/submit
→ Review
```

Linha de ponto:

```text
CameraPanel
→ recognition
→ persistence
→ PunchResult
→ EventTimeline
```

### Regressões obrigatórias

```text
SAME_FACT_DIFFERENT_STATUS=NO
SAME_EVENT_DIFFERENT_TIMESTAMP=NO
SAME_ENTITY_DIFFERENT_AUTH_ACTIONS=NO
ZERO_ROWS_WITH_GLOBAL_TOTAL=NO
EMPTY_STATE_WITH_ACTIVE_PAGINATION=NO
ERRORSTATE_CONTRADICTS_PRESERVED_DATA=NO
SUCCESS_TOAST_WITH_STALE_SURFACES=NO
UNKNOWN_OUTCOME_WITH_SUCCESS_UI=NO
USER_CLICK_CREATES_TIMELINE_EVENT=NO
STEPPER_VALID_WITH_BLOCKING_FORM_ERROR=NO
RESOLVED_ERROR_GHOSTS_OTHER_SURFACES=NO
CAMERA_SUCCESS_EQUALS_PUNCH_SUCCESS=NO
OLD_USER_DATA_REMAINS_FOR_NEXT_USER=NO
RESPONSIVE_MODE_CHANGES_PERMISSION=NO
RESPONSIVE_MODE_CHANGES_SEMANTICS=NO
```

## Contrato congelado

```text
H9_COMPONENT_SURFACE_COHERENCE

same canonical fact -> same meaning................ YES
component invents alternate domain truth........... NO
same entity version -> same canonical facts......... YES
same event id -> same subject/type/time.............. YES
Search/Filter/Sort/Page -> one query context......... YES
rows/counts/page/empty -> same scope................. YES
confirmed zero + active result pagination........... NO
DataTable -> DetailDrawer preserves list context..... YES
confirmed mutation -> affected surfaces converge..... YES
Toast = reconciliation.............................. NO
Toast before confirmed mutation..................... NO
UNKNOWN_OUTCOME -> contradictory success/failure..... NO
UNKNOWN_OUTCOME -> persistent reconciliation......... YES
generic write retry always safe..................... NO
retry obeys H4/H5................................... YES
Stepper owns wizard state........................... NO
Stepper reflects canonical wizard state............. YES
ErrorSummary/Field/Section/Stepper share error....... YES
resolved error may remain as ghost elsewhere......... NO
ContextDrawer becomes duplicate form................ NO
AppContext = employment company..................... NO
same capability -> coherent authorization............ YES
ConfirmationModal repairs missing authorization..... NO
HealthCard/StatusBadge same fact contradiction....... NO
LastUpdated scope matches associated data............ YES
EventTimeline invented from user click............... NO
PunchResult/EventTimeline same event disagreement.... NO
CameraPanel success = punch success................. NO
next user retains previous transient state........... NO
shared Design System = shared AppShell everywhere.... NO
/punch remains outside admin AppShell................ YES
responsive recomposition changes semantics........... NO
responsive recomposition changes permission.......... NO
one condition -> one primary persistent presentation.. YES
surface may bypass minimum necessary data............ NO
screen-reader/tooltip/toast may leak protected data.. NO
stale async result may break reconciled surfaces..... NO
new component gap.................................... 0
new implementation architecture frozen............... NO
```

## Próximo passo

```text
NEXT_OFFICIAL_ITEM=H10_CATALOG_COMPLETENESS_RC_CLOSEOUT
```

H10 deve reconciliar formalmente H1–H9, confirmar cobertura, gaps, invariantes e decidir se a Fase H pode ser declarada `COMPLETE` antes da entrada no Design Lab.
