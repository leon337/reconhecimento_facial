# NF-01 — Component Review F2 — ConfirmationModal

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
F2_CONFIRMATION_MODAL=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_F_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=F3_EVENT_TIMELINE_COMPONENT_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `ConfirmationModal` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`ConfirmationModal` interrompe deliberadamente uma ação destrutiva, irreversível ou de impacto relevante antes da execução.

```text
INTENÇÃO DO USUÁRIO
        ↓
ação de alto impacto
        ↓
ConfirmationModal
        ↓
decisão explícita
   ┌────┴─────┐
 cancelar   confirmar
              ↓
       backend valida
              ↓
       estado canônico
```

```text
CONFIRMATION_MODAL != DECORATIVE_ARE_YOU_SURE
CONFIRMATION != AUTHORIZATION
CONFIRMATION_MODAL != REAUTHENTICATION
CONFIRMATION_MODAL != LEGAL_COMPLIANCE_ENGINE
```

Confirmação não substitui autorização, autenticação adicional, regra de negócio, verificação de estado atual ou conformidade legal.

## Quando usar

Candidatos incluem exclusão de biometria, desativação de funcionário, descarte de alterações relevantes, revogação de acesso, exclusão de registro e ações em lote de alto impacto.

```text
ROUTINE_ACTION => NO_CONFIRMATION_MODAL
```

Salvar formulário comum, abrir detalhe, aplicar filtro, trocar aba, copiar texto ou navegar não exige confirmação por padrão.

## Anatomia e conteúdo

```text
TITLE........................ REQUIRED
TARGET....................... REQUIRED_WHEN_ENTITY_EXISTS
CONSEQUENCE.................. REQUIRED
CANCEL_ACTION................ REQUIRED
CONFIRM_ACTION............... REQUIRED
SECONDARY_CONTEXT............ OPTIONAL
```

O alvo e o escopo da ação devem ser explícitos. A consequência deve explicar o que realmente acontecerá, distinguindo ações reversíveis de irreversíveis.

```text
CONFIRM_LABEL => EXPLICIT_ACTION_VERB
YES_NO_GENERIC_LABELS....................... PROHIBITED
NO_CONFIRMED_RECOVERY => NO_RECOVERY_PROMISE
REVERSIBLE != IRREVERSIBLE
```

## Modalidade, foco e fechamento

`ConfirmationModal` é modal real e deixa todas as camadas inferiores inertes. Quando aberto sobre `DetailDrawer`, o drawer fica temporariamente inerte e o modal assume o foco.

```text
NESTED_CONFIRMATION_MODAL................... PROHIBITED
CANCEL_BUTTON............................... REQUIRED
SAFE_INITIAL_FOCUS.......................... REQUIRED_FOR_DESTRUCTIVE_CONFIRMATION
DESTRUCTIVE_AUTOFOCUS....................... PROHIBITED
GLOBAL_ENTER_AUTO_CONFIRMS_DESTRUCTIVE...... PROHIBITED
ESCAPE_BEFORE_SUBMIT........................ REQUIRED_WHEN_CANCELLABLE
BACKDROP_CLOSE.............................. OPTIONAL_WHEN_SAFE
UI_CLOSE != OPERATION_CANCELLED
```

Após uma mutação já enviada, fechar a UI não significa cancelar a operação no backend.

## Submitting, duplicidade e idempotência

```text
SUBMITTING => DUPLICATE_CONFIRMATION_BLOCKED
UI_DISABLED != SERVER_IDEMPOTENCY
SERVER_IDEMPOTENCY_OR_TRANSACTION_RULE...... REQUIRED_WHEN_APPLICABLE
```

O frontend evita duplo acionamento, mas operações críticas devem possuir proteção apropriada também no backend quando aplicável.

## Falhas, resultado desconhecido e reconciliação

```text
REQUEST_FAILED != OPERATION_FAILED
TRANSPORT_ERROR != CONFIRMED_OPERATION_FAILURE
UNKNOWN_OUTCOME => RECONCILE_OR_VERIFY
UNKNOWN_OUTCOME => NO_BLIND_RETRY
UNKNOWN_OUTCOME => NO_SUCCESS_TOAST
UNKNOWN_OUTCOME => NO_FAILURE_TOAST
```

Se a mutação pode ter sido concluída mas a resposta se perdeu, o sistema deve reconciliar o estado antes de repetir ou declarar sucesso/falha.

Somente após resultado canônico confirmado:

```text
CONFIRMED_MUTATION
      ↓
RECONCILE_AFFECTED_SURFACES
      ↓
CLOSE_MODAL
      ↓
OPTIONAL_SECONDARY_TOAST
```

## Concorrência, estado e RBAC

O snapshot exibido no modal não é fonte autoritativa para a execução.

```text
CONFIRMATION_SNAPSHOT != AUTHORITATIVE_CURRENT_STATE
CONFIRMATION_NEVER_BYPASSES_RBAC
BACKEND_REVALIDATES_TENANT_RBAC_ENTITY_STATE_POLICY
CONFLICT_OR_STATE_CHANGE => SAFE_RECONCILIATION
PERMISSION_REVOKED => DENY_SAFELY
```

A confirmação em lote deve refletir o escopo real e a seleção deve ser revalidada antes da execução.

```text
SELECTION_SCOPE => MUST_MATCH_CONFIRMATION_SCOPE
QUERY_SCOPE_CHANGE => REVALIDATE_SELECTION
```

## Padrões excepcionais

```text
TYPED_CONFIRMATION......................... OPTIONAL_EXTREME_RISK_PATTERN
TYPED_CONFIRMATION_BASELINE................ NO
COUNTDOWN_CONFIRMATION_BASELINE............ NO
```

Digitar uma palavra de confirmação pode ser usado apenas para risco excepcionalmente alto e não faz parte do baseline comum.

## Privacidade e segurança

O modal apresenta apenas informação necessária à decisão.

```text
MINIMUM_NECESSARY_CONFIRMATION_CONTEXT...... REQUIRED
STACK_TRACE_SQL_TOKEN_SECRET................ PROHIBITED
INTERNAL_OR_BIOMETRIC_DETAIL................ PROHIBITED_UNLESS_EXPLICITLY_NECESSARY_AND_AUTHORIZED
```

## Acessibilidade e responsividade

```text
DIALOG_SEMANTICS............................ REQUIRED
ACCESSIBLE_TITLE............................ REQUIRED
CONSEQUENCE_ASSOCIATED...................... REQUIRED
BACKGROUND_INERT............................ REQUIRED
FOCUS_TRAP................................. REQUIRED
SAFE_INITIAL_FOCUS.......................... REQUIRED
FOCUS_RETURN............................... REQUIRED
KEYBOARD_ACTIONS........................... REQUIRED
DESTRUCTIVE_MEANING_NOT_COLOR_ONLY......... REQUIRED
ROLE_ALERTDIALOG_ALWAYS.................... PROHIBITED
RESPONSIVE_REFLOW.......................... REQUIRED
ZOOM_200_PERCENT_OPERABLE.................. REQUIRED
```

## Integrações previstas

```text
DetailDrawer → ConfirmationModal
DataTable bulk action → ConfirmationModal
StickyFormActions → discard confirmation
ConfirmationModal → backend → canonical state
ConfirmationModal → Toast
ConfirmationModal → conflict handling
ConfirmationModal → permission revalidation
```

## Testes futuros obrigatórios

### Unitários

- abrir/fechar, cancelar e confirmar;
- foco inicial seguro;
- variante destrutiva;
- submitting e bloqueio de duplicidade;
- labels explícitos;
- typed confirmation opcional.

### Integração

- `DetailDrawer → ConfirmationModal`;
- ação em lote de `DataTable`;
- descarte via `StickyFormActions`;
- backend → estado canônico → reconciliação;
- Toast apenas após resultado confirmado;
- conflito e permissão revogada.

### Resiliência

- timeout após mutação;
- resultado desconhecido e reconciliação;
- duplo submit;
- idempotência quando aplicável;
- estado da entidade alterado durante confirmação.

### Segurança

- revalidação RBAC;
- isolamento por tenant;
- escopo da seleção;
- mínimo necessário de dados;
- ausência de diagnósticos sensíveis.

### Responsivo e acessibilidade

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- teclado e screen reader;
- focus trap e focus return;
- Escape quando cancelável;
- reduced motion.

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
PHASE_E_COMPONENT_REVIEW=COMPLETE
F1_DETAIL_DRAWER=FROZEN_INDIVIDUALLY
F2_CONFIRMATION_MODAL=FROZEN_INDIVIDUALLY
PHASE_F_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=F3_EVENT_TIMELINE_COMPONENT_REVIEW
```
