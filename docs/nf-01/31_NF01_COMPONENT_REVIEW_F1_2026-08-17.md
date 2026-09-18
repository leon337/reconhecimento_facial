# NF-01 — Component Review F1 — DetailDrawer

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
F1_DETAIL_DRAWER=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_F_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=F2_CONFIRMATION_MODAL_COMPONENT_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela o contrato conceitual de `DetailDrawer` para a NF-01. Esta aprovação não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Responsabilidade

`DetailDrawer` apresenta detalhes de uma entidade específica sem destruir o contexto da superfície de origem.

```text
DataTable / lista / timeline
        ↓
trigger explícito de detalhe
        ↓
ENTITY_ID
        ↓
AUTHORIZED DETAIL QUERY
        ↓
DetailDrawer
        ↓
fechar
        ↓
mesma busca / filtros / sort / página / contexto
```

```text
DETAIL_DRAWER != CONTEXT_DRAWER
DETAIL_DRAWER != FULL_PAGE
DETAIL_DRAWER != CONFIRMATION_MODAL
DETAIL_DRAWER != SPLIT_PANE
DETAIL_DRAWER != HISTORY_ENGINE
```

## Baseline e modalidade

```text
DETAIL_DRAWER_BASELINE...................... READ_ONLY
DESKTOP_TABLET.............................. SIDE_MODAL_OVERLAY
MOBILE...................................... FULL_SCREEN_OVERLAY
BACKGROUND_VISIBLE_ON_DESKTOP.............. YES
BACKGROUND_INTERACTIVE_WHILE_OPEN.......... NO
```

O baseline é leitura contextual. Edição extensa, wizard ou aplicação complexa dentro do drawer são proibidos; quando a complexidade exceder inspeção contextual, a experiência deve migrar para página completa.

## Anatomia

```text
HEADER
  ENTITY_IDENTITY / TITLE
  OPTIONAL_STATUS_BADGE
  CLOSE_ICON_BUTTON
BODY
  READ_ONLY_SECTIONS
  OPTIONAL_LAST_UPDATED
  LOCAL_LOADING_OR_ERROR_STATE
FOOTER
  OPTIONAL_CONTEXTUAL_ACTIONS
```

A identidade humana da entidade tem prioridade sobre IDs técnicos. IDs internos não devem ser expostos sem necessidade.

## Preservação do contexto de origem

```text
DETAIL_OPEN_CLOSE => PRESERVE_SEARCH
DETAIL_OPEN_CLOSE => PRESERVE_FILTERS
DETAIL_OPEN_CLOSE => PRESERVE_SORT
DETAIL_OPEN_CLOSE => PRESERVE_PAGE
DETAIL_OPEN_CLOSE => PRESERVE_OR_RESTORE_SCROLL_CONTEXT
```

Quando a arquitetura usar URL navegável, o estado de detalhe pode ser restaurável por Back/Forward, sem colocar PII desnecessária na URL.

## RBAC, privacidade e dados

```text
TENANT_RBAC_SCOPE
    ↓
AUTHORIZED_ENTITY
    ↓
AUTHORIZED_FIELDS
    ↓
AUTHORIZED_ACTIONS
    ↓
DetailDrawer
```

```text
FETCH_ALL_THEN_HIDE........................ PROHIBITED
MINIMUM_NECESSARY_DATA..................... REQUIRED
UNNECESSARY_PII_IN_URL..................... PROHIBITED
PERMISSION_REVOKED => REMOVE_PROTECTED_DATA REQUIRED
```

Campos e ações proibidos não devem ser carregados e depois ocultados apenas por CSS. Mudança de permissão enquanto o drawer está aberto exige remoção segura do conteúdo protegido ou fechamento/estado de acesso seguro.

## Loading, erro e concorrência

```text
DETAIL_LOADING => SKELETON
DETAIL_LOADING => NO_FAKE_VALUE
DETAIL_LOADING => NO_FAKE_STATUS
STALE_ENTITY_RESPONSE_MUST_NOT_OVERRIDE_CURRENT_ENTITY
```

Falhas localizadas usam `ErrorState`. `NOT_FOUND` e `NOT_AUTHORIZED` devem ser tratados sem revelar existência indevida da entidade.

## Fechamento e foco

```text
CLOSE_BUTTON............................... REQUIRED
ESCAPE..................................... REQUIRED
BACKDROP_CLOSE............................. OPTIONAL_WHEN_SAFE
FOCUS_ENTERS_DRAWER........................ REQUIRED
FOCUS_TRAP................................ REQUIRED_BASELINE_MODAL
BACKGROUND_INERT........................... REQUIRED
FOCUS_RETURN_TO_TRIGGER.................... REQUIRED_WHEN_TRIGGER_EXISTS
LOGICAL_FOCUS_FALLBACK..................... REQUIRED_WHEN_TRIGGER_NO_LONGER_EXISTS
```

O foco inicial deve ser seguro e nunca cair automaticamente em ação destrutiva.

## Stacking e ações

```text
NESTED_DETAIL_DRAWER....................... PROHIBITED_BY_DEFAULT
CONFIRMATION_MODAL_OVER_DRAWER............. SUPPORTED
HIGH_IMPACT_ACTION => CONFIRMATION.......... WHEN_APPLICABLE
UNKNOWN_OUTCOME => NO_SUCCESS_CLOSE......... REQUIRED
```

Ações disponíveis derivam de estado da entidade + RBAC + política. Ações proibidas normalmente não são renderizadas.

## Reconciliação após mutação

```text
CONFIRMED_MUTATION
      ↓
CANONICAL_ENTITY_STATE
      ├── DetailDrawer
      └── Origin surface / DataTable
```

Drawer e superfície de origem devem convergir para o mesmo estado. Exclusão confirmada pode fechar o drawer e reconciliar a lista; Toast é apenas feedback secundário.

## Scroll, responsividade e acessibilidade

Preferência por uma região principal de scroll no body, com header estável e footer opcionalmente sticky. Evitar múltiplos scroll containers aninhados.

```text
RESPONSIVE_REFLOW_OR_FULLSCREEN............. REQUIRED
RIGID_DESKTOP_WIDTH_ON_MOBILE............... PROHIBITED
ZOOM_200_PERCENT_OPERABLE................... REQUIRED
VIRTUAL_KEYBOARD_DOES_NOT_HIDE_ACTIONS...... REQUIRED
ACCESSIBLE_NAME............................. REQUIRED
DIALOG_SEMANTICS............................ REQUIRED
ARIA_MODAL_EQUIVALENT....................... REQUIRED_BASELINE
HEADING_HIERARCHY........................... REQUIRED
STATUS_NOT_COLOR_ONLY....................... REQUIRED
```

## Integrações previstas

```text
DataTable → DetailDrawer
DetailDrawer + StatusBadge
DetailDrawer + LastUpdated
DetailDrawer + Skeleton
DetailDrawer + ErrorState
DetailDrawer + ConfirmationModal
DetailDrawer + Toast
DetailDrawer + EventTimeline
URL / Back / Forward
```

## Testes futuros obrigatórios

### Unitários

- open/close;
- header/body/footer;
- loading/error/not-found;
- ações autorizadas;
- Close/Escape.

### Integração

- DataTable → DetailDrawer → close preservando Search/Filter/Sort/Page;
- URL + Back/Forward;
- `DetailDrawer + ConfirmationModal`;
- mutação confirmada reconciliando drawer e lista.

### Concorrência

- entidade A lenta e entidade B rápida: B permanece atual e A é descartada.

### Segurança

- isolamento por tenant;
- RBAC de entidade, campos e ações;
- revogação de permissão enquanto aberto;
- ausência de PII desnecessária na URL;
- mínimo necessário de dados.

### Responsivo e acessibilidade

- 360 / 768 / 1024 / 1440+;
- zoom 200%;
- teclado e screen reader;
- focus trap e focus return;
- Escape;
- full-screen mobile;
- teclado virtual.

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
PHASE_F_COMPONENT_REVIEW=IN_PROGRESS
NEXT_OFFICIAL_ITEM=F2_CONFIRMATION_MODAL_COMPONENT_REVIEW
```
