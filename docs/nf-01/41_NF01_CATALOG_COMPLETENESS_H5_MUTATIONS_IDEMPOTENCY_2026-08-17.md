# NF-01 — Catalog Completeness RC — H5 — Mutações, resultado desconhecido e idempotência

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
H5_MUTATION_UNKNOWN_OUTCOME_IDEMPOTENCY_COHERENCE=APPROVED_BY_LEANDRO
H5_STATUS=COMPLETE
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H6_ACCESSIBILITY_FOCUS_KEYBOARD_ARIA_MOTION_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela a coerência transversal de mutações, `unknown outcome`, reconciliação e idempotência para a NF-01. Ela não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Fontes reconciliadas

H5 consolida e torna transversais regras já congeladas em `ErrorState`, `ConfirmationModal`, `PunchResult`, H3 e H4. Nenhuma tecnologia backend nova é escolhida por esta decisão.

## Linha de montagem da mutação

```text
INTENÇÃO
   ↓
AUTORIZAÇÃO / ESTADO ATUAL
   ↓
CONFIRMAÇÃO quando necessária
   ↓
SUBMIT
   ↓
BACKEND
   ↓
EFEITO CANÔNICO
   ↓
RESULTADO AUTORITATIVO
   ↓
RECONCILIAÇÃO DA UI
```

```text
REQUEST_SENT != MUTATION_CONFIRMED
```

## Estados conceituais da operação

Esses estados pertencem ao ciclo da mutação e não criam um novo enum global do Design System:

```text
IDLE
CONFIRMATION_REQUIRED     quando aplicável
SUBMITTING
CONFIRMED_SUCCESS
CONFIRMED_FAILURE
BUSINESS_REJECTION
CONFLICT
UNKNOWN_OUTCOME
RECONCILING
```

```text
CONFIRMED_FAILURE != UNKNOWN_OUTCOME
BUSINESS_REJECTION != TECHNICAL_FAILURE
```

## Submitting e duplicidade

```text
SUBMITTING => DUPLICATE_UI_TRIGGER_BLOCKED
DUPLICATE_UI_TRIGGER_BLOCKED != SERVER_IDEMPOTENCY
UI_DISABLED != SERVER_IDEMPOTENCY
```

Bloqueio visual reduz duplo clique, mas não protege contra retry do navegador, proxy, reconexão, múltiplas abas ou repetição após timeout.

## Sucesso autoritativo

```text
CONFIRMED_SUCCESS => AUTHORITATIVE_DOMAIN_OUTCOME
REQUEST_ACCEPTED != FINAL_SUCCESS
OPTIMISTIC_UI != CONFIRMED_OUTCOME
```

Para operações críticas, sucesso final otimista é proibido. O frontend não inventa semântica de domínio a partir do simples envio da requisição ou de um status de transporte.

## Resultado desconhecido

Timeout, desconexão, aborto do cliente ou perda da resposta depois do submit não provam que a operação falhou.

```text
TRANSPORT_ERROR != CONFIRMED_OPERATION_FAILURE
CLIENT_REQUEST_ABORTED != SERVER_MUTATION_CANCELLED
UI_CLOSE != OPERATION_CANCELLED
AUTH_STATE_CHANGED != PROOF_OF_PREVIOUS_MUTATION_FAILURE
```

Quando o efeito pode ter ocorrido:

```text
UNKNOWN_OUTCOME
       ↓
RECONCILING
       ↓
VERDADE CANÔNICA
       ↓
CONFIRMED_SUCCESS / CONFIRMED_FAILURE / estado seguro
```

```text
UNKNOWN_OUTCOME => RECONCILE_OR_VERIFY
UNKNOWN_OUTCOME => NO_BLIND_RETRY
UNKNOWN_OUTCOME => NO_SUCCESS_TOAST
UNKNOWN_OUTCOME => NO_FAILURE_TOAST
```

## Retry de escrita

Retry de mutação só é seguro quando:

```text
WRITE_RETRY
=> CONFIRMED_NO_EFFECT
   OR
   REPLAY_SAFE_GUARD
```

```text
SAME_LOGICAL_OPERATION_REPLAY
→ MUST_NOT_CREATE_DUPLICATE_SIDE_EFFECT
```

H5 não congela o mecanismo técnico. Futuras implementações podem usar identidade de operação, idempotency key, restrição única, regra transacional, deduplicação de domínio ou mecanismo equivalente, conforme o caso.

```text
SPECIFIC_BACKEND_IDEMPOTENCY_MECHANISM_FROZEN_BY_H5=NO
```

## Intenção e identidade de operação

```text
SAME_LOGICAL_OPERATION != NEW_USER_INTENT
RECONCILABLE_CRITICAL_MUTATION => STABLE_OPERATION_IDENTITY_OR_EQUIVALENT
```

Uma nova ação legítima não pode ser confundida com replay da operação anterior.

## Cancelamento

```text
PRE_SUBMIT_CANCEL != BACKEND_OPERATION_CANCEL
```

Fechar modal, drawer, aba ou abortar a requisição do cliente não implica rollback. H5 não inventa capacidade backend de cancelamento.

## Estado atual, conflito e autorização

O snapshot mostrado pela UI não é autoridade para a execução.

```text
CONFIRMATION_SNAPSHOT != AUTHORITATIVE_CURRENT_STATE
PERMISSION_AT_RENDER != PERMISSION_AT_EXECUTION
MUTATION_SUBMIT => BACKEND_AUTHORIZATION_REVALIDATION
CONFLICT => NO_SILENT_OVERWRITE
CONFIRMATION != AUTHORIZATION
```

Backend deve revalidar autorização, escopo, entidade, estado atual e regra de domínio no momento efetivo da mutação.

## Falha confirmada e rejeição de negócio

```text
CONFIRMED_FAILURE => EFFECT_CONFIRMED_ABSENT_OR_NOT_APPLIED
BUSINESS_REJECTION != TECHNICAL_FAILURE
UI != BUSINESS_RULE_ENGINE
```

Retry só pode ser oferecido quando a operação for efetivamente segura para repetição.

## Feedback e superfícies

```text
SUCCESS_TOAST => CONFIRMED_OUTCOME
UNKNOWN_OUTCOME => PERSISTENT_NEUTRAL_RECOVERY_STATE
CONFIRMED_MUTATION => RECONCILE_AFFECTED_SURFACES
```

Após sucesso confirmado, `DataTable`, `DetailDrawer`, `StatusBadge`, `MetricCard`, `EventTimeline`, formulários e outras superfícies afetadas devem ser reconciliadas com os mesmos fatos canônicos.

```text
USER_CLICK != DOMAIN_EVENT
UI_SUCCESS != AUDIT_EVIDENCE
```

Evento histórico só existe quando o domínio fornece evento canônico; feedback visual não substitui auditoria.

## Operações em lote

```text
BULK_MUTATION_ATOMICITY => MUST_BE_EXPLICIT
PARTIAL_SUCCESS != FULL_SUCCESS
```

O contrato pode ser atômico ou permitir resultado parcial, mas essa semântica deve ser conhecida. Resultado parcial exige reconciliação por item/escopo efetivamente afetado.

## Offline

```text
NO_CONFIRMED_DURABLE_QUEUE => NO_QUEUED_WRITE_CLAIM
OFFLINE_WRITE => NO_FAKE_QUEUED_STATE
```

Sem fila durável, identidade da operação e reconciliação reais, a UI não promete sincronização futura.

## Autosave e drafts

```text
AUTOSAVE_REQUEST_SENT != DRAFT_SAVED
DRAFT_SAVED => CONFIRMED_CANONICAL_SAVE
```

Resultado incerto de autosave deve ser apresentado como não confirmado; ordenação de saves concorrentes será aprofundada em H8.

## Undo

```text
UNDO != TRANSACTION_ROLLBACK
UNDO => NEW_AUTHORIZED_MUTATION
```

Uma ação de desfazer, quando existir, é nova mutação sujeita a autorização, estado atual e resultado canônico.

## Aplicações críticas preservadas

### Criação de funcionário

Timeout após possível criação não autoriza cadastrar novamente às cegas. Deve haver reconciliação para confirmar entidade criada ou ausência de efeito.

### Biometria

Mutação biométrica exige revalidação de autorização e estado. Timeout não autoriza declarar falha nem repetir remoção/cadastro sem verificar o estado canônico.

### Registro de ponto

```text
FACE_MATCH_SUCCESS != PUNCH_SUCCESS
TRANSPORT_ERROR != CONFIRMED_PUNCH_FAILURE
UNKNOWN_OUTCOME => RECONCILE_OR_VERIFY
UNKNOWN_OUTCOME => NO_BLIND_RETRY
```

Duplicação de ponto é um cenário obrigatório de teste de resiliência.

## Contrato congelado

```text
H5_MUTATION_UNKNOWN_OUTCOME_IDEMPOTENCY

REQUEST_SENT = MUTATION_CONFIRMED................ NO
HTTP_SUCCESS = DOMAIN_SUCCESS.................... NOT_ASSUMED
ACCEPTED = COMPLETED............................. NO
SUBMITTING duplicate UI trigger.................. BLOCKED
UI disabled = server idempotency................. NO
CONFIRMED_SUCCESS => authoritative outcome....... YES
CONFIRMED_FAILURE != UNKNOWN_OUTCOME............. YES
BUSINESS_REJECTION != TECHNICAL_FAILURE.......... YES
CONFLICT => no silent overwrite.................. YES
TRANSPORT_ERROR = operation failure.............. NO
CLIENT_ABORT = backend cancellation.............. NO
UI_CLOSE = operation cancelled................... NO
UNKNOWN_OUTCOME => reconcile..................... YES
UNKNOWN_OUTCOME => blind retry................... NO
UNKNOWN_OUTCOME => success Toast................. NO
UNKNOWN_OUTCOME => failure Toast................. NO
WRITE_RETRY requires confirmed no-effect
or replay-safe guard............................. YES
same logical replay duplicates side effect....... NO
new legitimate intent = retry.................... NO
stable operation identity/equivalent
for reconcilable critical mutations.............. YES
specific backend mechanism frozen by H5.......... NO
backend revalidates authorization/state.......... YES
confirmation bypasses RBAC....................... NO
critical optimistic final success................ NO
OPTIMISTIC_UI = CONFIRMED_OUTCOME................ NO
CONFIRMED_MUTATION => reconcile surfaces......... YES
USER_CLICK = DOMAIN_EVENT........................ NO
UI_SUCCESS = AUDIT_EVIDENCE...................... NO
BULK atomicity explicit.......................... YES
PARTIAL_SUCCESS = FULL_SUCCESS................... NO
no durable offline queue -> queued claim......... NO
AUTOSAVE_REQUEST_SENT = DRAFT_SAVED.............. NO
UNDO = transaction rollback...................... NO
UNDO as new authorized mutation.................. YES
```

## Testes futuros obrigatórios

### Unitários

- state machine `SUBMITTING`, `CONFIRMED_SUCCESS`, `CONFIRMED_FAILURE`, `BUSINESS_REJECTION`, `CONFLICT`, `UNKNOWN_OUTCOME`, `RECONCILING`;
- bloqueio de gatilho duplicado;
- ausência de sucesso/falha prematuros;
- classificação correta entre retry seguro e retry proibido.

### Integração

- mutação concluída no backend com resposta perdida;
- reconciliação encontra efeito canônico;
- criação de funcionário potencialmente duplicada;
- remoção/cadastro biométrico;
- registro de ponto;
- permissão revogada antes do submit efetivo;
- conflito de estado entre confirmação e execução;
- resultado parcial em lote quando suportado.

### Resiliência

- double click;
- timeout + retry;
- browser/proxy replay;
- reconexão mobile;
- múltiplas abas;
- mesmo identificador lógico não produz efeito duplicado quando o mecanismo aplicável existir.

### Segurança

- reconciliação respeita RBAC, escopo autorizado e mínimo necessário;
- nenhuma operação é autorizada por estado antigo da UI;
- nenhuma mensagem de resultado desconhecido revela diagnóstico interno.

## Invariantes preservados

```text
app/**=UNCHANGED
templates/**=UNCHANGED
static/**=UNCHANGED
migrations/**=UNCHANGED
backend/routes=UNCHANGED
DECISOES_CONGELADAS.md=UNCHANGED
NF02=NOT_STARTED
Ponto_to_AttendanceEvent=NOT_EXECUTED
AI=NOT_IMPLEMENTED
OBSERVABILITY_BACKEND=NOT_IMPLEMENTED
DEPLOY=NO
PR32_MERGE=NOT_AUTHORIZED
```

## Continuidade

```text
H1_CATALOG_INVENTORY=COMPLETE_WITH_GAP
H1A_ERROR_SUMMARY=COMPLETE
H2_GLOBAL_SEMANTIC_STATE_COHERENCE=COMPLETE
H3_RBAC_TENANT_MINIMUM_NECESSARY_COHERENCE=COMPLETE
H4_OPERATIONAL_STATE_COHERENCE=COMPLETE
H5_MUTATION_UNKNOWN_OUTCOME_IDEMPOTENCY_COHERENCE=COMPLETE
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H6_ACCESSIBILITY_FOCUS_KEYBOARD_ARIA_MOTION_COHERENCE
```
