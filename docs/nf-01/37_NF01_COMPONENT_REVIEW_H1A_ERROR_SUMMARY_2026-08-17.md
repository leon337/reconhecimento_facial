# NF-01 — Component Review H1A — ErrorSummary

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
H1A_ERROR_SUMMARY=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
H1_CATALOG_GAP=RESOLVED
COMPONENT_INDIVIDUAL_REVIEW=COMPLETE
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H2_GLOBAL_SEMANTIC_STATE_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `ErrorSummary` para a NF-01 e resolve o único gap encontrado por H1. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`ErrorSummary` consolida problemas atuais de formulário, etapa ou wizard e oferece navegação até o alvo correto. Ele não valida dados nem executa regras de negócio.

```text
VALIDATION / DOMAIN RESULT
          ↓
canonical current errors
          ↓
ErrorSummary
          ↓
navigation to actionable target
          ↓
FieldGroup / FormSection / Wizard step
```

```text
ERROR_SUMMARY != VALIDATION_ENGINE
ERROR_SUMMARY != BUSINESS_RULE_ENGINE
ERROR_SUMMARY != VALIDATION_MESSAGE
ERROR_SUMMARY != ERROR_STATE
ERROR_SUMMARY != TOAST
```

`ValidationMessage` permanece junto ao campo; `ErrorSummary` consolida e navega; `ErrorState` comunica falha persistente de operação/superfície.

## Escopo e apresentação

Escopos suportados:

```text
FORM / STEP
WIZARD REVIEW
SYSTEM / WIZARD item, quando aplicável
```

O resumo não permanece vazio na interface e não depende de um número mínimo rígido de erros. Um único erro pode justificar `ErrorSummary` quando a navegação/tarefa exigir.

```text
NO_ACTIVE_ERRORS => NO_ERROR_SUMMARY
SUMMARY_NEEDED => TASK_AND_NAVIGATION_CONTEXT
```

A ordem dos itens segue a ordem lógica da tarefa, etapa, seção e DOM, não a ordem acidental de respostas do backend.

```text
ERROR_ORDER => USER_TASK_ORDER
ERROR_TARGET != DOM_POSITION_INDEX
```

Cada item usa identidade lógica estável e, por padrão, um item acionável por alvo. Mensagens locais detalhadas continuam preservadas.

## Navegação e foco

Ao ativar um item, a aplicação deve localizar o alvo, abrir etapa/seção quando necessário, garantir visibilidade e então mover o foco ao controle apropriado.

```text
ERROR_TARGET_IN_COLLAPSED_SECTION => EXPAND_BEFORE_FOCUS
CROSS_STEP_ERROR_NAVIGATION => CANONICAL_STEP_TRANSITION
ERROR_NAVIGATION_TARGET => MUST_REMAIN_VISIBLE
```

A decisão previamente congelada para submit inválido permanece:

```text
DEFAULT_INVALID_SUBMIT_FOCUS => FIRST_ACTIONABLE_ERROR
SUMMARY_MANDATORY_AUTOFOCUS => NO
```

O `ErrorSummary` deve ser semanticamente descobrível e operável sem obrigar foco automático no próprio resumo.

## Atualidade dos erros

Erros resolvidos saem do resumo atual. Validações assíncronas obsoletas não podem reintroduzir erros antigos.

```text
RESOLVED_ERROR => REMOVE_FROM_CURRENT_SUMMARY
STALE_VALIDATION_RESPONSE => MUST_NOT_REINTRODUCE_ERROR
VALIDATING != VALIDATION_ERROR
```

Campos condicionais que deixam de participar do payload ativo também deixam o resumo ativo.

```text
HIDDEN_INACTIVE_FIELD => REMOVE_FROM_ACTIVE_ERROR_SUMMARY
```

`ErrorSummary` não é motor de dependências; apenas apresenta classificação canônica produzida pelo domínio/validação.

## Warning, conflito e outcome desconhecido

```text
WARNING != ERROR_SUMMARY_ITEM_BY_DEFAULT
CONFLICT_ERROR != FIELD_VALIDATION_ERROR
SUBMIT_OUTCOME_UNKNOWN => NO_FIELD_BLAME
SUBMIT_OUTCOME_UNKNOWN => RECONCILIATION_REQUIRED
```

Conflitos ou condições globais podem aparecer em escopo de sistema/wizard quando apropriado, mas o resumo não substitui a superfície persistente nem a reconciliação de estado.

## RBAC, tenant e privacidade

O resumo respeita o mesmo escopo autorizado da superfície atual. Não pode reter ou revelar rótulos, valores ou mensagens de campos que deixaram de estar autorizados.

```text
ERROR_SUMMARY => SAME_AUTHORIZED_SCOPE
FIELD_NO_LONGER_AUTHORIZED => REMOVE_PROTECTED_SUMMARY_ITEM
USER_MESSAGE != INTERNAL_DIAGNOSTIC
```

São proibidos stack trace, SQL, schema interno, endpoints, identificadores sensíveis e detalhes técnicos desnecessários.

## Contagem

A contagem apresentada reflete os itens acionáveis visíveis no próprio resumo, não a quantidade de regras internas executadas.

```text
DISPLAYED_ERROR_COUNT => DISPLAYED_ACTIONABLE_ITEMS
```

## Acessibilidade e responsividade

O componente usa heading textual, lista semântica e itens acionáveis com nomes compreensíveis isoladamente. Estado não depende apenas de cor.

```text
COLOR_ONLY_MEANING => PROHIBITED
UNIVERSAL_ROLE_ALERT => NO
EVERY_VALIDATION_CHANGE => NO_FULL_SUMMARY_ANNOUNCEMENT
```

Links/ações precisam ser operáveis por teclado, com foco visível. Atualizações não devem provocar tempestade de anúncios em leitores de tela.

Em 360/768/1024/1440+, larguras intermediárias e zoom 200%, o resumo reflowa verticalmente e a navegação até o alvo não pode deixá-lo oculto atrás de header, `StickyFormActions` ou teclado virtual.

## Integrações

```text
ErrorSummary + FieldGroup
ErrorSummary + ValidationMessage
ErrorSummary + FormSection
ErrorSummary + HorizontalStepper
ErrorSummary + StickyFormActions
ErrorSummary + ErrorState
ErrorSummary + conflict
ErrorSummary + RBAC
```

## Testes futuros

Unitários:
- ausência com zero erros;
- um e múltiplos erros;
- ordenação e contagem;
- identidade estável do alvo;
- remoção de erro resolvido;
- item não associado a campo;
- mensagens seguras.

Integração:
- navegação para `FieldGroup`;
- expansão de `FormSection` antes do foco;
- transição canônica entre etapas do wizard;
- `ValidationMessage` local preservada;
- conflito/outcome desconhecido sem culpa de campo;
- RBAC removendo item protegido.

Concorrência:
- validação remota A lenta;
- validação B atual vence;
- resposta tardia de A não reintroduz erro.

A11y/responsivo:
- 360/768/1024/1440+ e intermediários;
- zoom 200%;
- teclado;
- screen reader;
- foco no alvo;
- no announcement storm;
- alvo visível com sticky UI e teclado mobile.

## Contrato congelado

```text
H1A_ERROR_SUMMARY

consolida erros atuais....................... YES
valida dados................................. NO
executa regras de negócio.................... NO
ErrorSummary = ValidationMessage............. NO
ErrorSummary = ErrorState.................... NO
ErrorSummary = Toast......................... NO
FORM/STEP scope.............................. YES
WIZARD REVIEW scope.......................... YES
SYSTEM/WIZARD item........................... YES when applicable
summary vazio persistente.................... NO
mínimo rígido de erros....................... NO
ordem por tarefa/DOM........................ YES
stable target identity....................... YES
one actionable item per target by default.... YES
local ValidationMessage preservada........... YES
collapsed section expands before focus....... YES
cross-step canonical transition.............. YES
invalid submit focus -> first error........... YES
summary mandatory autofocus.................. NO
resolved error remains....................... NO
stale validation reintroduces error.......... NO
VALIDATING = ERROR........................... NO
inactive conditional field in summary........ NO
unauthorized field in summary................ NO
warning automatically becomes error.......... NO
conflict = field validation.................. NO
unknown submit = field validation............ NO
unknown submit requires reconciliation....... YES
safe user message............................ YES
internal diagnostic.......................... NO
displayed count = actionable items........... YES
color-only meaning........................... NO
keyboard navigation.......................... YES
screen-reader structure...................... YES
role=alert universal......................... NO
announcement storm........................... NO
responsive reflow............................ YES
target hidden by sticky UI................... NO
```

## Estado final de H1A

```text
H1A_ERROR_SUMMARY=FROZEN_INDIVIDUALLY
H1_GAP_RESOLVED=YES
COMPONENT_INDIVIDUAL_REVIEW=COMPLETE
NEXT_OFFICIAL_ITEM=H2_GLOBAL_SEMANTIC_STATE_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```
