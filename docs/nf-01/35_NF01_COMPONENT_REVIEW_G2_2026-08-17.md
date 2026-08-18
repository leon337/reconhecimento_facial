# NF-01 — Component Review G2 — PunchResult

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
G2_PUNCH_RESULT=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_G_COMPONENT_REVIEW=COMPLETE
NEXT_OFFICIAL_ITEM=H1_CATALOG_COMPLETENESS_RC
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `PunchResult` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`PunchResult` comunica o resultado canônico da tentativa de registrar o ponto. Ele não é o mecanismo de reconhecimento facial, regra de negócio, persistência, cálculo de jornada ou folha.

```text
CameraPanel
    ↓
captura válida
    ↓
reconhecimento / liveness
    ↓
identidade confirmada
    ↓
operação de registro
    ↓
persistência / domínio
    ↓
PunchResult
```

```text
PUNCH_RESULT != FACE_RECOGNITION_RESULT
PUNCH_RESULT != PUNCH_ENGINE
PUNCH_RESULT != WORKED_HOURS_ENGINE
PUNCH_RESULT != PAYROLL_ENGINE
FACE_MATCH_SUCCESS != PUNCH_SUCCESS
```

## Regra de sucesso

Sucesso só existe após persistência confirmada pelo domínio/backend.

```text
PUNCH_SUCCESS => PERSISTENCE_CONFIRMED
DISPLAYED_EMPLOYEE => CONFIRMED_SUBJECT
DISPLAYED_PUNCH_TYPE => CANONICAL_EVENT_TYPE
DISPLAYED_TIME => CANONICAL_PERSISTED_TIME
CLIENT_CLOCK != CANONICAL_PUNCH_TIMESTAMP
PUNCH_RESULT != EVENT_TYPE_ENGINE
```

Reconhecimento facial positivo não autoriza a UI a declarar o ponto registrado antes da persistência canônica.

## Estados canônicos

```text
PROCESSING
SUCCESS_CONFIRMED
FAILURE_CONFIRMED
BUSINESS_REJECTION
UNKNOWN_OUTCOME
PENDING_SYNC   ONLY_IF_DURABLE_OFFLINE_QUEUE_EXISTS
```

```text
FAILURE_CONFIRMED != UNKNOWN_OUTCOME
SUCCESS_CONFIRMED != PENDING_SYNC
PENDING_SYNC != PERSISTED_SERVER_SUCCESS
```

`PENDING_SYNC` só poderá existir quando houver fila offline durável, identidade de evento, semântica de sincronização e reconciliação comprovadas.

## Resultado desconhecido e reconciliação

```text
TRANSPORT_ERROR != CONFIRMED_PUNCH_FAILURE
UNKNOWN_OUTCOME => RECONCILE_OR_VERIFY
UNKNOWN_OUTCOME => NO_BLIND_RETRY
UNKNOWN_OUTCOME => NO_SUCCESS_TOAST
UNKNOWN_OUTCOME => NO_FAILURE_TOAST
```

Se o backend pode ter persistido o registro mas a resposta se perdeu, a UI não declara sucesso nem falha até reconciliar o estado canônico. Repetição deve ser segura e protegida por idempotência/deduplicação apropriada no backend; desabilitar botão não substitui essa garantia.

```text
DISABLED_BUTTON != IDEMPOTENCY
```

## Falha confirmada e rejeição de negócio

`FAILURE_CONFIRMED` exige evidência canônica de que o registro não foi persistido. `BUSINESS_REJECTION` é uma decisão do domínio, não um erro técnico genérico.

```text
PUNCH_RESULT != BUSINESS_RULE_ENGINE
NO_MATCH != PUNCH_PERSISTENCE_FAILURE
LIVENESS_FAILED != PUNCH_PERSISTENCE_FAILURE
```

Falha de reconhecimento ou liveness antes da operação de ponto não deve ser apresentada como falha de persistência do ponto.

## Offline

```text
NO_CONFIRMED_OFFLINE_QUEUE => NO_PENDING_SYNC_CLAIM
PENDING_SYNC != SERVER_SUCCESS
```

Se futuramente existir fluxo offline, a UI deve distinguir claramente `salvo neste dispositivo / aguardando sincronização` de `registro confirmado no servidor`.

## Identidade, localização e privacidade

```text
MINIMUM_NECESSARY_IDENTITY................ REQUIRED
RAW_BIOMETRIC_SCORE....................... NOT_USER_FACING
RAW_BIOMETRIC_DATA........................ PROHIBITED
RAW_GEOLOCATION........................... NOT_DEFAULT_PUNCH_RESULT
SAFE_PUBLIC_REFERENCE != INTERNAL_ID
USER_MESSAGE != INTERNAL_DIAGNOSTIC
```

CPF completo, embedding, score facial, hash biométrico, chaves internas, coordenadas brutas, stack trace, SQL, host, token ou payload sensível não pertencem à superfície principal.

## Superfície principal e Toast

Registro de ponto é operação crítica, portanto `PunchResult` é feedback principal e persistente da tarefa.

```text
CRITICAL_PUNCH_RESULT != TOAST_ONLY
PUNCH_RESULT => PRIMARY_PERSISTENT_TASK_FEEDBACK
```

Toast pode complementar apenas após resultado confirmado.

## Sessão compartilhada e próxima pessoa

```text
NEXT_SESSION
→ clear identity
→ clear punch result
→ clear captured frame
→ clear transient biometric state
→ reset CameraPanel
```

```text
NEXT_USER => NO_PREVIOUS_USER_TRANSIENT_DATA
AUTO_RESET => ONLY_AFTER_RESULT_IS_READABLE
TIMER_EXPIRY != OPERATION_SUCCESS
```

O resultado deve permanecer tempo suficiente para leitura. Valores universais de auto-reset não são congelados nesta etapa.

## Concorrência e deduplicação

```text
SESSION_ID / OPERATION_ID => CURRENT_SESSION_WINS
STALE_PUNCH_RESULT_MUST_NOT_OVERRIDE_CURRENT_SESSION
PUNCH_EVENT_ID => DEDUPLICATION
```

Resposta tardia de uma sessão anterior nunca pode aparecer para a pessoa seguinte, por consistência e privacidade.

## Integração com EventTimeline e CameraPanel

```text
SAME_CANONICAL_EVENT => SAME_CANONICAL_FACTS
PunchResult + EventTimeline => CONSISTENT_EVENT_DATA
PUNCH_RESULT_ACTIVE => NO_BACKGROUND_CAPTURE_FOR_NEXT_SESSION
```

Uma vez exibido `PunchResult`, o `CameraPanel` não inicia silenciosamente captura para uma nova pessoa.

## Acessibilidade e responsividade

```text
SUCCESS != GREEN_ONLY
FAILURE != RED_ONLY
TEXTUAL_RESULT............................. REQUIRED
TEXTUAL_EVENT_TYPE........................ REQUIRED_WHEN_APPLICABLE
TEXTUAL_CANONICAL_TIME..................... REQUIRED_WHEN_CONFIRMED
ACCESSIBLE_NEXT_ACTION..................... REQUIRED
FOCUS_OR_ANNOUNCEMENT_ON_MATERIAL_RESULT... CONTEXTUAL
RESPONSIVE_INFORMATION_PRIORITY............ REQUIRED
```

A prioridade visual e semântica é: resultado → tipo → horário → identidade quando apropriada → próxima ação.

## Contrato congelado

```text
G2_PUNCH_RESULT

resultado canônico do registro............... YES
face-recognition result...................... NO
punch engine................................. NO
worked-hours/payroll engine.................. NO
PUNCH_SUCCESS => PERSISTENCE_CONFIRMED....... YES
FACE_MATCH_SUCCESS = PUNCH_SUCCESS............ NO
canonical employee........................... YES
canonical event type......................... YES
canonical timestamp.......................... YES
client clock as evidence..................... NO
SUCCESS_CONFIRMED............................. YES
FAILURE_CONFIRMED............................. YES
BUSINESS_REJECTION............................ YES when supplied by domain
UNKNOWN_OUTCOME............................... YES
PENDING_SYNC.................................. ONLY_IF_DURABLE_OFFLINE_QUEUE_EXISTS
FAILURE_CONFIRMED = UNKNOWN_OUTCOME........... NO
PENDING_SYNC = SERVER_SUCCESS................. NO
transport timeout = punch failure............. NO
UNKNOWN_OUTCOME → reconcile.................. YES
UNKNOWN_OUTCOME → blind retry................ NO
duplicate prevention.......................... YES backend-supported
UI disabled = idempotency..................... NO
NO_MATCH = punch persistence failure.......... NO
LIVENESS_FAILED = punch persistence failure... NO
raw biometric score........................... NO
raw biometric data............................ NO
unnecessary PII............................... NO
raw geolocation by default.................... NO
internal diagnostics.......................... NO
critical result = Toast only.................. NO
primary persistent feedback................... YES
Next person clears transient data............. YES
previous-user residue......................... NO
stale result overrides new session............ NO
PunchResult + EventTimeline consistency....... YES
PunchResult active + background capture....... NO
success/failure by color only................. NO
textual/a11y result........................... YES
responsive.................................... YES
```

## Testes futuros obrigatórios

### Unitários

- `PROCESSING`, `SUCCESS_CONFIRMED`, `FAILURE_CONFIRMED`, `BUSINESS_REJECTION`, `UNKNOWN_OUTCOME`;
- timestamp canônico, tipo de batida e identidade mínima;
- limpeza da sessão e deduplicação.

### Integração

- `CameraPanel → reconhecimento → punch → PunchResult`;
- timeout após possível persistência → reconciliação;
- `PunchResult → EventTimeline` com os mesmos fatos canônicos;
- `Próxima pessoa` limpando estado transitório;
- RBAC/tenant quando aplicável.

### Resiliência e concorrência

- resposta perdida depois da persistência;
- retry seguro/idempotente;
- resposta obsoleta de sessão anterior;
- nova sessão iniciada antes de resposta anterior;
- evento repetido não duplica resultado.

### Segurança e privacidade

- nenhum score/embedding/frame em UI, log ou analytics indevido;
- nenhuma PII além do mínimo necessário;
- nenhum resíduo da pessoa anterior;
- nenhuma exposição de diagnóstico interno.

### Responsivo e acessibilidade

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- teclado e screen reader;
- resultado textual sem dependência exclusiva de cor;
- foco/anúncio contextual e próxima ação acessível.

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
G1_CAMERA_PANEL=FROZEN_INDIVIDUALLY
G2_PUNCH_RESULT=FROZEN_INDIVIDUALLY
PHASE_G_COMPONENT_REVIEW=COMPLETE
COMPONENT_INDIVIDUAL_REVIEW=COMPLETE
NEXT_OFFICIAL_ITEM=H1_CATALOG_COMPLETENESS_RC
```
