# NF-01 — Component Review E4 — DegradationBanner

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
E4_DEGRADATION_BANNER=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_E_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=E5_TOAST_INTEGRATION_COHERENCE_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `DegradationBanner` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`DegradationBanner` comunica condição persistente e relevante em que a aplicação continua utilizável, mas uma capacidade está limitada, degradada, desatualizada ou operando por contingência.

```text
CONDIÇÃO OPERACIONAL
        ↓
avaliação do domínio/health
        ↓
DEGRADADA MAS UTILIZÁVEL
        ↓
DegradationBanner
        ↓
usuário continua trabalhando
```

```text
DEGRADATION_BANNER != ERROR_STATE
DEGRADATION_BANNER != TOAST
DEGRADATION_BANNER != STATUS_BADGE
DEGRADATION_BANNER != HEALTH_ENGINE
DEGRADED != DOWN
DEGRADED != ERROR
OFFLINE != ERROR
```

Se não existe continuação segura para a tarefa, o estado deixa de ser apenas degradado e deve ser tratado como bloqueante.

## Anatomia e mensagem

```text
STATE/TONE................................. REQUIRED
TITLE...................................... REQUIRED
IMPACT_MESSAGE............................. REQUIRED
FALLBACK................................... OPTIONAL_WHEN_REAL_AND_AVAILABLE
LAST_UPDATED............................... OPTIONAL_WHEN_TEMPORALLY_RELEVANT
ACTION..................................... OPTIONAL
DISMISS.................................... CONDITIONAL
```

A mensagem deve explicar a capacidade afetada, o impacto, o que ainda funciona e o que o usuário deve fazer. Mensagens genéricas como `Sistema degradado` não atendem ao contrato.

## Fonte de verdade e recuperação

```text
DOMAIN_OR_HEALTH_STATE => DEGRADATION_BANNER
FRONTEND_GUESSES_DEGRADATION............... PROHIBITED
RETRY_STARTED != RECOVERED.................. REQUIRED
TIMEOUT != RECOVERY........................ REQUIRED
VERIFIED_RECOVERY => REMOVE_BANNER......... REQUIRED
```

O componente não decide saúde nem recuperação. A remoção do banner depende de estado canônico de recuperação, não de timer, início de retry ou evento visual isolado.

## Dados antigos e recência

```text
REFRESH_ERROR != NO_USABLE_DATA............ REQUIRED
VALID_STALE_DATA_MAY_REMAIN_VISIBLE......... ALLOWED_WHEN_IDENTIFIED
STALE_DATA != CURRENT_DATA.................. REQUIRED
LAST_UPDATED_PRESERVED...................... REQUIRED
PAGE_RENDER_TIME != DATA_UPDATE_TIME........ PRESERVED
```

Quando dados anteriores ainda são utilizáveis, eles podem permanecer com `LastUpdated` e um `DegradationBanner` indicando possível desatualização. Uma falha de refresh não redefine o timestamp da informação.

## Offline e contingência

```text
OFFLINE_WITH_SAFE_SUPPORTED_MODE............ SUPPORTED
NO_CONFIRMED_QUEUE => NO_SYNC_PROMISE....... REQUIRED
NO_SAFE_CONTINUATION => BLOCKING_STATE...... REQUIRED
```

O banner pode orientar uso de contingência apenas quando o fallback existe de fato. Não deve prometer sincronização posterior sem fila ou mecanismo confirmado.

## Escopo

```text
DEGRADATION_SCOPE = LOCAL | FEATURE | GLOBAL
IMPACT_SCOPE => BANNER_SCOPE................ REQUIRED
GLOBAL_BANNER_FOR_LOCAL_FAILURE............. PROHIBITED
```

A amplitude da comunicação deve corresponder ao impacto real. Uma falha localizada não justifica automaticamente um banner global.

## Persistência e dismiss

```text
DEGRADATION_ACTIVE => BANNER_VISIBLE......... REQUIRED
TIMER_EXPIRY => RECOVERY..................... FALSE
CRITICAL_OPERATIONAL_DEGRADATION_DISMISS.... PROHIBITED_BY_DEFAULT
INFORMATIONAL_DISMISS........................ ALLOWED_WHEN_SAFE_AND_STATE_REMAINS_DISCOVERABLE
```

Condições que alteram a forma de trabalhar devem permanecer visíveis enquanto persistirem. Dismiss é restrito a mensagens não críticas e somente quando o estado continuar descobrível por outro meio.

## Fallback, RBAC, segurança e privacidade

```text
CAPABILITY_STATE + PERMISSION + POLICY => AVAILABLE_FALLBACK
INVENTED_OR_UNAUTHORIZED_FALLBACK............ PROHIBITED
MESSAGE_RESPECTS_RBAC........................ REQUIRED
STACK_TRACE_SQL_TOKEN_SECRET................. PROHIBITED
INTERNAL_HOST_IP_PATH........................ PROHIBITED_UNLESS_EXPLICITLY_SAFE_AND_NECESSARY
BIOMETRIC_DETAIL_OR_UNNECESSARY_PII.......... PROHIBITED
TELEMETRY_UNAVAILABLE != SUCCESS............. PRESERVED
```

O banner não pode revelar capacidades, infraestrutura ou dados fora do escopo autorizado. Falta de telemetria nunca deve ser convertida por inferência em estado saudável.

## Relação com componentes já congelados

```text
StatusBadge
→ estado compacto

DegradationBanner
→ impacto + orientação persistente

ErrorState
→ tarefa/superfície bloqueada ou falhou

Toast
→ evento transitório complementar
```

`HealthCard`/domínio podem fornecer o estado; `DegradationBanner` apenas apresenta a condição e sua consequência operacional.

## Acessibilidade e responsividade

```text
TEXTUAL_MEANING.............................. REQUIRED
ICON_ONLY_MEANING............................ PROHIBITED
RESPONSIVE_REFLOW............................ REQUIRED
TINY_TYPE_TO_FIT............................. PROHIBITED
MATERIAL_STATE_CHANGE_ANNOUNCEMENT........... CONTEXTUAL
POLLING_ANNOUNCEMENT_STORM................... PROHIBITED
ROLE_ALERT_ALWAYS............................ PROHIBITED
```

A entrada da degradação ou mudança material pode ser anunciada; polling que apenas confirma o mesmo estado não deve gerar anúncios repetitivos.

## Contrato congelado

```text
SYSTEM_OR_CAPABILITY_STILL_USABLE............ REQUIRED_FOR_DEGRADATION
FULLY_BLOCKING_FAILURE........................ NOT_DEGRADATION

EXPLAIN_AFFECTED_CAPABILITY.................. REQUIRED
EXPLAIN_IMPACT............................... REQUIRED
REAL_FALLBACK................................. OPTIONAL_WHEN_AVAILABLE
INVENT_FALLBACK............................... PROHIBITED

DOMAIN_OR_HEALTH_SUPPLIES_STATE.............. REQUIRED
DEGRADATION_BANNER_AS_HEALTH_ENGINE.......... PROHIBITED

STALE_DATA_MAY_REMAIN_IDENTIFIED............. ALLOWED
STALE_AS_CURRENT.............................. PROHIBITED
LAST_UPDATED_PRESERVED........................ REQUIRED

OFFLINE_SUPPORTED............................ ALLOWED
UNCONFIRMED_SYNC_PROMISE...................... PROHIBITED

LOCAL_FEATURE_GLOBAL_SCOPE................... SUPPORTED
GLOBAL_FOR_LOCAL_FAILURE...................... PROHIBITED

PERSIST_WHILE_ACTIVE.......................... REQUIRED
VERIFIED_RECOVERY_REMOVES..................... REQUIRED
CRITICAL_DISMISS.............................. PROHIBITED_BY_DEFAULT

RECOVERY_ACTIONS.............................. ALLOWED_WHEN_SAFE
BLIND_RETRY................................... PROHIBITED

FALLBACK_RESPECTS_RBAC........................ REQUIRED
MESSAGE_RESPECTS_RBAC......................... REQUIRED
SENSITIVE_INTERNAL_DETAILS.................... PROHIBITED

RESPONSIVE_REFLOW............................. REQUIRED
A11Y_CONTEXTUAL............................... REQUIRED
POLLING_ANNOUNCEMENT_STORM.................... PROHIBITED
```

## Testes futuros obrigatórios

### Unitários

- estado degradado;
- título, impacto e fallback;
- ação e `LastUpdated`;
- escopo local/feature/global;
- dismissível versus não dismissível;
- ausência de fallback inventado.

### Integração

- `DegradationBanner + HealthCard`;
- `DegradationBanner + LastUpdated`;
- `DegradationBanner + ErrorState`;
- `DegradationBanner + Toast`;
- modo offline e contingência;
- RBAC e fallback autorizado;
- recuperação verificada removendo o banner.

### Regressão operacional

```text
FACIAL_DOWN + SAFE_FALLBACK_AVAILABLE => DEGRADATION
FACIAL_DOWN + NO_SAFE_FALLBACK => BLOCKING_STATE
STALE_DATA_AVAILABLE => DATA + LAST_UPDATED + DEGRADATION
TELEMETRY_UNAVAILABLE => NEVER_INFER_HEALTHY
RETRY_STARTED != RECOVERED
TIMEOUT != RECOVERY
```

### Responsivo e acessibilidade

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- teclado;
- screen reader;
- anúncio de mudança material sem tempestade durante polling.

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
PHASE_E_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=E5_TOAST_INTEGRATION_COHERENCE_REVIEW
```
