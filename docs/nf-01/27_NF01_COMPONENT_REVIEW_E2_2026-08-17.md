# NF-01 — Component Review E2 — ErrorState

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
E2_ERROR_STATE=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_E_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=E3_SKELETON_COMPONENT_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `ErrorState` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`ErrorState` comunica falha conhecida que impede total ou parcialmente a conclusão da tarefa atual e, quando possível, apresenta recuperação segura.

```text
OPERAÇÃO / CONSULTA
        ↓
tentativa executada
        ↓
falha conhecida
        ↓
classificação
        ↓
ErrorState
```

```text
ERROR != EMPTY
REQUEST_FAILED != OPERATION_FAILED
TRANSPORT_ERROR != CONFIRMED_OPERATION_FAILURE
RETRY != BLIND_REPEAT
USER_MESSAGE != INTERNAL_DIAGNOSTIC
FIELD_VALIDATION_ERROR != ERROR_STATE
ERROR_STATE != TOAST
ERROR_STATE != DEGRADATION_BANNER
```

## Estados e escopo congelados

```text
BLOCKING_LOAD_ERROR........................ SUPPORTED
SECTION_ERROR.............................. SUPPORTED
ACTION_ERROR............................... SUPPORTED
OFFLINE_BLOCKING........................... SUPPORTED
ACCESS_DENIED.............................. SUPPORTED_AS_DISTINCT_AUTHORIZATION_STATE
UNKNOWN_OUTCOME............................ SUPPORTED

TITLE...................................... REQUIRED
DESCRIPTION................................ REQUIRED
ICON....................................... OPTIONAL
RECOVERY_ACTION............................ OPTIONAL_WHEN_SAFE
SECONDARY_ACTION........................... OPTIONAL
SAFE_REFERENCE_ID.......................... OPTIONAL
```

## Retry, idempotência e reconciliação

```text
RETRY_SAFE_READ............................ ALLOWED
RETRY_NON_IDEMPOTENT_WRITE_BLINDLY......... PROHIBITED
IDEMPOTENCY_OR_EQUIVALENT_GUARD............ REQUIRED_FOR_CRITICAL_WRITES_WHEN_RETRYABLE
UNKNOWN_OUTCOME => RECONCILE_OR_VERIFY...... REQUIRED
CONFIRMED_NO_EFFECT_BEFORE_RETRY............ REQUIRED_WHEN_OPERATION_IS_NOT_IDEMPOTENT
```

Timeout ou falha de transporte não prova que a operação de domínio falhou. Em operações críticas, especialmente registro de ponto, a UI deve reconciliar/verificar o estado canônico antes de oferecer repetição potencialmente duplicadora.

## Falha parcial e dados ainda utilizáveis

```text
PARTIAL_FAILURE => LOCALIZE_FAILURE.......... REQUIRED
REFRESH_ERROR != NO_USABLE_DATA.............. REQUIRED
VALID_STALE_DATA_MAY_REMAIN_VISIBLE........... ALLOWED_WHEN_IDENTIFIED
PARTIAL_ERROR_DESTROYS_VALID_PAGE............. PROHIBITED
```

Quando dados válidos anteriores continuam úteis, `LastUpdated` e, quando aplicável, `DegradationBanner` podem preservar o contexto em vez de substituir toda a superfície por erro bloqueante.

## Segurança, privacidade e RBAC

```text
STACK_TRACE_TO_USER.......................... PROHIBITED
SQL_TO_USER.................................. PROHIBITED
SECRET_OR_TOKEN_TO_USER...................... PROHIBITED
INTERNAL_HOST_IP_PATH_TO_USER................ PROHIBITED_UNLESS_EXPLICITLY_SAFE_AND_NECESSARY
BIOMETRIC_OR_UNNECESSARY_PERSONAL_DATA....... PROHIBITED
RAW_BACKEND_MESSAGE_AS_USER_MESSAGE.......... PROHIBITED
SAFE_REFERENCE_ID............................ ALLOWED
RBAC_SCOPE_BEFORE_MESSAGE.................... REQUIRED
ENUMERATION_LEAK_VIA_403_404.................. PROHIBITED
```

`REFERENCE_ID` serve apenas para correlação segura com logs/suporte e não deve incorporar diagnóstico sensível.

## Concorrência e estado atual

```text
STALE_ERROR_RESPONSE_MUST_NOT_OVERRIDE_CURRENT_STATE
CURRENT_QUERY_OR_OPERATION_STATE_WINS
```

Uma falha antiga não pode substituir um sucesso mais recente da mesma superfície.

## Acessibilidade e responsividade

```text
TEXTUAL_ERROR_MEANING........................ REQUIRED
ICON_ONLY_MEANING............................ PROHIBITED
KEYBOARD_ACCESS_FOR_ACTIONS.................. REQUIRED
FOCUS_VISIBLE................................ REQUIRED
FOCUS_MANAGEMENT............................. CONTEXTUAL
ROLE_ALERT_ALWAYS............................ PROHIBITED
RESPONSIVE_BY_REFLOW_NOT_TINY_TYPE........... REQUIRED
```

## Integrações previstas

```text
ErrorState + DataTable
ErrorState + Search / FilterBar / Pagination
ErrorState + Form / ValidationMessage
ErrorState + Toast
ErrorState + DegradationBanner
ErrorState + LastUpdated
ErrorState + RBAC / Session
```

## Testes futuros obrigatórios

### Unitários

- `BLOCKING_LOAD_ERROR`, `SECTION_ERROR`, `ACTION_ERROR`, `OFFLINE_BLOCKING`, `ACCESS_DENIED`, `UNKNOWN_OUTCOME`;
- com/sem retry;
- safe reference id;
- mensagem sanitizada;
- ausência de exposição de diagnóstico interno.

### Integração

- timeout após write com reconciliação;
- retry idempotente sem duplicação;
- erro parcial preservando dados válidos;
- sessão expirada;
- RBAC sem enumeração;
- resposta de erro antiga descartada quando estado atual já venceu.

### Segurança

- nenhuma exposição de stack trace, SQL, segredos, infraestrutura interna desnecessária, biometria ou PII não necessária.

### Responsivo e acessibilidade

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- teclado;
- screen reader;
- foco contextual;
- anúncios sem excesso de `role=alert`.

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
PHASE_E_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=E3_SKELETON_COMPONENT_REVIEW
```
