# NF-01 — Component Review E5 — Toast

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
E5_TOAST=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_E_COMPONENT_REVIEW=COMPLETE
NEXT_OFFICIAL_ITEM=F1_DETAIL_DRAWER_COMPONENT_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela a revisão de integração/coerência do `Toast` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`Toast` é feedback secundário e transitório para um evento confirmado ou informação breve que não precisa permanecer como estado principal da tarefa.

```text
EVENTO CONFIRMADO
      ↓
feedback secundário útil
      ↓
Toast
      ↓
desaparece sem alterar
o estado real da aplicação
```

```text
TOAST = TRANSIENT_SECONDARY_FEEDBACK
TOAST != SYSTEM_STATE
TOAST != ERROR_STATE
TOAST != DEGRADATION_BANNER
TOAST != VALIDATION_MESSAGE
TOAST != CONFIRMATION_MODAL
TOAST != STATUS_BADGE
TOAST != AUDIT_LOG
```

## Resultado confirmado

```text
SUCCESS_TOAST => CONFIRMED_OUTCOME
UNKNOWN_OUTCOME != SUCCESS_TOAST
UNKNOWN_OUTCOME != FAILURE_TOAST
TRANSPORT_ERROR != CONFIRMED_OPERATION_FAILURE
```

Timeout ou falha de transporte em operação crítica não autoriza Toast de sucesso nem de falha conclusiva quando o resultado ainda é desconhecido. O estado deve ser reconciliado/verificado conforme o contrato de `ErrorState`.

Resultados críticos devem possuir feedback persistente ou localizado na tarefa quando necessário; Toast pode complementar, mas não ser a única evidência operacional.

## Anatomia e tons

```text
MESSAGE.............................. REQUIRED
TONE................................. REQUIRED
ICON................................. OPTIONAL
ACTION............................... OPTIONAL
DISMISS.............................. OPTIONAL

TONES = SUCCESS | INFO | WARNING | ERROR
ERROR_TONE => TRANSIENT_NON_BLOCKING_ONLY
```

Mensagens devem indicar o evento concreto (`Funcionário atualizado`, `Link copiado`, `Não foi possível copiar o link`) e evitar textos genéricos como `Sucesso!` ou `Erro!`.

## Persistência, timer e interação

```text
AUTO_DISMISS................................. ALLOWED_CONTEXTUALLY
UNIVERSAL_FIXED_TIMEOUT...................... NOT_FROZEN
INTERACTIVE_OR_IMPORTANT_TOAST............... NEEDS_SUFFICIENT_TIME
FOCUS_OR_INTERACTION => DO_NOT_DISMISS_UNDER_USER
TOAST_ACTION => NOT_ONLY_CRITICAL_RECOVERY_PATH
```

Ação opcional (`Desfazer`, `Tentar novamente`, `Ver`) só é válida quando segura. A única recuperação crítica não pode desaparecer junto com um Toast.

`Undo` não substitui automaticamente `ConfirmationModal` para ações destrutivas/alto impacto.

## Frequência, deduplicação e fila

```text
HIGH_FREQUENCY_EVENT != TOAST_EACH_OCCURRENCE
REPEATED_EQUIVALENT_EVENT => DEDUPLICATE_OR_COALESCE
NO_UNBOUNDED_TOAST_STACK
CONTROLLED_QUEUE............................. REQUIRED
```

Autosave recorrente não deve gerar Toast a cada ocorrência; indicador persistente discreto é preferível. Eventos equivalentes repetidos devem ser deduplicados ou agregados quando semanticamente seguro.

## Relação com DegradationBanner e recuperação

```text
PERSISTENT_CONDITION => DEGRADATION_BANNER
VERIFIED_RECOVERY => BANNER_REMOVED + OPTIONAL_TOAST
PERSISTENT_OFFLINE != TOAST_ONLY
CRITICAL_ERROR != TOAST_ONLY
CONFLICT != TOAST_ONLY
```

Exemplo coerente: degradação/offline persistente usa `DegradationBanner`; quando a recuperação for canonicamente verificada, um Toast opcional pode informar `Conexão restabelecida`.

## Segurança, privacidade e RBAC

```text
RBAC_CONTEXT_BEFORE_MESSAGE_OR_ACTION........ REQUIRED
MINIMUM_NECESSARY_INFORMATION................ REQUIRED
STACK_TRACE_SQL_TOKEN_SECRET................. PROHIBITED
INTERNAL_HOST_IP_PATH........................ PROHIBITED_UNLESS_EXPLICITLY_SAFE_AND_NECESSARY
BIOMETRIC_DETAIL_OR_UNNECESSARY_PII.......... PROHIBITED
```

Toast pode aparecer em superfícies compartilhadas e deve ser conservador com PII. Ações embutidas respeitam o RBAC atual do usuário.

## Acessibilidade, movimento e responsividade

```text
AUTO_FOCUS_TOAST............................. PROHIBITED
ARIA_LIVE.................................... CONTEXTUAL
ASSERTIVE_FOR_EVERY_ERROR.................... PROHIBITED
KEYBOARD_ACCESS_FOR_ACTIONS.................. REQUIRED
FOCUS_VISIBLE................................ REQUIRED
REDUCED_MOTION............................... REQUIRED
SAFE_AREAS................................... REQUIRED
COVER_STICKY_OR_CRITICAL_ACTIONS............. PROHIBITED
```

Toast não rouba foco. Mensagens simples podem usar anúncio `polite` ou equivalente; anúncios assertivos são reservados para contexto realmente necessário. Movimento deve respeitar `prefers-reduced-motion`.

No mobile, a composição deve respeitar safe areas e não cobrir `StickyFormActions`, controles essenciais de punch ou ações críticas.

## Contrato congelado

```text
TRANSIENT_SECONDARY_FEEDBACK................. REQUIRED
PERSISTENT_SYSTEM_STATE...................... NOT_TOAST

SUCCESS_TOAST_REQUIRES_CONFIRMED_OUTCOME..... REQUIRED
UNKNOWN_SUBMIT_AS_SUCCESS_OR_FAILURE_TOAST... PROHIBITED

SUCCESS_INFO_WARNING......................... SUPPORTED
TRANSIENT_COMPLEMENTARY_ERROR................ SUPPORTED
CRITICAL_ERROR_TOAST_ONLY.................... PROHIBITED

MESSAGE_REQUIRED............................. YES
ICON_OPTIONAL................................ YES
ACTION_OPTIONAL.............................. YES
DISMISS_OPTIONAL............................. YES

AUTO_DISMISS_CONTEXTUAL...................... YES
CRITICAL_ACTION_DISAPPEARS_WITH_TIMEOUT...... PROHIBITED
INTERACTION_PROTECTS_FROM_DISMISS............. REQUIRED

DEDUPLICATION................................ REQUIRED_WHEN_APPLICABLE
CONTROLLED_QUEUE............................. REQUIRED
UNBOUNDED_STACK.............................. PROHIBITED
AUTOSAVE_TOAST_EACH_EVENT.................... PROHIBITED

VERIFIED_RECOVERY_TOAST...................... OPTIONAL
OFFLINE_PERSISTENT_TOAST_ONLY................ PROHIBITED

RBAC......................................... REQUIRED
PRIVACY_MINIMUM_NECESSARY.................... REQUIRED
INTERNAL_DIAGNOSTIC.......................... PROHIBITED

AUTO_FOCUS................................... PROHIBITED
ARIA_LIVE_CONTEXTUAL......................... REQUIRED
ASSERTIVE_FOR_ALL............................ PROHIBITED
REDUCED_MOTION............................... REQUIRED
SAFE_AREA.................................... REQUIRED
COVER_CRITICAL_ACTION....................... PROHIBITED
```

## Testes futuros obrigatórios

### Unitários

- `SUCCESS`, `INFO`, `WARNING`, `ERROR` transitório;
- auto-dismiss e dismiss manual;
- ação opcional;
- deduplicação e fila;
- reduced motion;
- proteção de timer durante foco/interação.

### Integração

- `Toast + ErrorState`;
- `Toast + DegradationBanner`;
- `Toast + ValidationMessage`;
- `Toast + ConfirmationModal`;
- Toast após navegação;
- RBAC e sessão;
- autosave sem tempestade de notificações;
- recuperação verificada removendo banner e Toast opcional.

### Regressão semântica

```text
SUCCESS_TOAST => CONFIRMED_OUTCOME
UNKNOWN_OUTCOME != SUCCESS_TOAST
UNKNOWN_OUTCOME != FAILURE_TOAST
PERSISTENT_OFFLINE != TOAST_ONLY
CRITICAL_ERROR != TOAST_ONLY
CONFLICT != TOAST_ONLY
HIGH_FREQUENCY_EVENT != TOAST_EACH_TIME
```

### Responsivo e acessibilidade

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- screen reader;
- teclado;
- foco visível;
- reduced motion;
- timer com foco/interação;
- safe areas e não sobreposição de ações essenciais.

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
E4_DEGRADATION_BANNER=FROZEN_INDIVIDUALLY
E5_TOAST=FROZEN_INDIVIDUALLY
PHASE_E_COMPONENT_REVIEW=COMPLETE
NEXT_OFFICIAL_ITEM=F1_DETAIL_DRAWER_COMPONENT_REVIEW
```
