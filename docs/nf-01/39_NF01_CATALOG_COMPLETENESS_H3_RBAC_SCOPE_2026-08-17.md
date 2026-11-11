# NF-01 — Catalog Completeness RC — H3 — RBAC, escopo autorizado e mínimo necessário

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate

```text
H3_RBAC_TENANT_MINIMUM_NECESSARY_COHERENCE=APPROVED_BY_LEANDRO
H3_STATUS=COMPLETE
PHASE_H_CATALOG_COMPLETENESS_RC=IN_PROGRESS
NEXT_OFFICIAL_ITEM=H4_OPERATIONAL_STATE_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação de LEANDRO congela a coerência transversal de RBAC, escopo autorizado e mínimo necessário para a NF-01. Ela não autoriza implementação visual, alteração de produção, início da NF-02 ou merge do PR #32.

## Fontes verificadas

- `app/rbac.py` da branch atual;
- `docs/nf-01/04_ROLES_PERMISSIONS_AND_STATES.md`;
- `docs/nf-01/06_COMPONENT_CATALOG.md`;
- contratos individuais já congelados e checkpoints H1/H1A/H2.

## RBAC real preservado

Papéis atuais:

```text
super_admin
admin
manager
operator
auditor
```

Permissões atuais:

```text
users:view
users:create
biometrics:manage
punch:view
punch:create
```

A NF-01 não cria permissões backend novas.

```text
CURRENT_BACKEND_RBAC=PRESERVED
NEW_BACKEND_PERMISSIONS_INVENTED=NO
```

Exemplo real preservado:

```text
manager:
users:view=YES
users:create=YES
biometrics:manage=NO
punch:view=YES
punch:create=NO
```

Logo, após criação confirmada de funcionário por `manager`, a UI não oferece CTA de biometria proibido.

## Separação semântica

```text
ROLE != PERMISSION
PERMISSION != SCOPE
ROLE != TENANT_SCOPE
UI_VISIBILITY != AUTHORIZATION
CLIENT_RBAC_CHECK != SERVER_AUTHORIZATION
CONFIRMATION != AUTHORIZATION
ROUTE_KNOWLEDGE != AUTHORIZATION
```

A UI reduz affordances indevidas; o backend continua sendo a autoridade e revalida autorização no momento da operação.

## Ações proibidas e indisponibilidade temporária

```text
NO_PERMISSION => NO_FORBIDDEN_AFFORDANCE
PROHIBITED != TEMPORARILY_UNAVAILABLE
```

Uma ação que o usuário não possui não deve aparecer apenas desabilitada como substituto de autorização. Uma ação autorizada, mas temporariamente indisponível por estado, pode aparecer desabilitada com motivo quando isso ajuda a tarefa.

## Shell administrativo e experiência de ponto

```text
PUNCH_CREATE != ADMIN_SHELL_ACCESS
```

`operator` ou contexto de estação com `punch:create` não recebe acesso administrativo por consequência dessa permissão. O fluxo `/punch` permanece semanticamente separado do `AppShell` administrativo.

## Escopo autorizado

H3 congela a abstração `AUTHORIZED_SCOPE` sem inventar uma implementação concreta de tenant que `app/rbac.py` não demonstra.

```text
PERMISSION + AUTHORIZED_SCOPE => QUERY_SCOPE
AUTHORIZED_SCOPE => QUERY
GLOBAL_QUERY => FRONTEND_HIDE = PROHIBITED
FETCH_ALL_THEN_HIDE = PROHIBITED
```

H3 define comportamento, não cria `tenant_id`, `organization_scope`, `unit_scope` ou novo mecanismo backend fictício.

```text
H3 != INVENT_TENANT_IMPLEMENTATION
AUTHORIZED_SCOPE_ABSTRACTION=YES
```

## Contexto da aplicação

A decisão canônica permanece:

```text
APP_CONTEXT != EMPRESA_DO_VINCULO
APP_CONTEXT_CHANGE => NO_SILENT_FORM_MUTATION
```

Mudança de contexto operacional exige revalidação/reconsulta das superfícies dependentes e não altera silenciosamente empresa contratante, unidade, setor, jornada ou draft de formulário.

```text
SCOPE_CHANGE => REVALIDATE_DATA
STALE_SCOPE_RESPONSE => MUST_NOT_OVERRIDE_CURRENT_SCOPE
```

## Mesmo escopo para dados e metadados

Todos os derivados de uma consulta precisam pertencer ao mesmo escopo autorizado:

```text
ROWS
COUNTS
METRICS
PAGINATION_TOTALS
FILTER_OPTIONS
FILTER_COUNTS
SEARCH_RESULTS
CURSORS
```

Guardrails:

```text
VISIBLE_DATA_SCOPE = COUNT_SCOPE
FILTER_OPTIONS + FILTER_COUNTS + RESULTS => SAME_AUTHORIZED_SCOPE
SEARCH => AUTHORIZED_SCOPE_BEFORE_MATCHING
PAGINATION_METADATA => SAME_AUTHORIZED_QUERY_SCOPE
```

A UI não pode revelar existência de entidades fora do escopo por contagens, autocomplete, mensagens, paginação, filtros ou estados auxiliares.

## Entidade autorizada não implica todos os campos

```text
AUTHORIZED_ENTITY != ALL_FIELDS_AUTHORIZED
AUTHORIZED != NECESSARY_FOR_THIS_TASK
AUTHORIZED_DATA => MINIMUM_NECESSARY_DATA => UI
```

Mesmo papéis elevados não precisam receber campos desnecessários em cada superfície. A resposta deve conter apenas os dados necessários à tarefa atual e compatíveis com o escopo autorizado.

## Biometria

```text
BIOMETRICS_MANAGE != RAW_BIOMETRIC_DATA_VIEW
```

A permissão de gestão biométrica não implica exposição de embedding, template, face encoding, raw frames ou score biométrico interno. A operação autorizada continua distinta da exposição de artefatos biométricos brutos.

## Componentes e mensagens

O mesmo escopo autorizado vale para:

```text
Search
FilterBar
EntityPicker
DataTable
Pagination
MetricCard
DetailDrawer
ErrorState
ErrorSummary
Toast
EventTimeline
CameraPanel enrollment
ConfirmationModal
```

Guardrails:

```text
ERROR_MESSAGE_SCOPE = AUTHORIZED_INFORMATION_SCOPE
TOAST_CONTENT => CURRENT_AUTHORIZED_SCOPE
ERROR_SUMMARY => SAME_AUTHORIZED_SCOPE
DETAIL_VIEW != PERMISSION_ESCALATION
COLUMN_HIDDEN != DATA_NOT_FETCHED
MINIMUM_NECESSARY_FIELDS => RESPONSE => COMPONENT
```

## Runtime, cache e mudança de autorização

```text
PERMISSION_REVOKED
=> REVALIDATE_VISIBLE_DATA
=> REMOVE_FORBIDDEN_ACTIONS
=> REMOVE_PROTECTED_CONTENT
```

Mudança de usuário, escopo, contexto ou logout não pode produzir flash de dados da sessão/escopo anterior.

```text
AUTH_SCOPE_CHANGE => NO_PREVIOUS_SCOPE_DATA_FLASH
NO_PERMISSION => NO_FORBIDDEN_DATA_RESIDUE
```

## Bulk e capacidades futuras

Ações em lote revalidam o escopo efetivo no backend no momento da execução.

```text
BULK_ACTION => REVALIDATE_EACH_EFFECTIVE_SCOPE
```

Quando exportação existir, ela não poderá contornar o escopo autorizado:

```text
EXPORT_MUST_NOT_BYPASS_AUTHORIZED_SCOPE
```

Nenhuma nova permissão de exportação é criada por H3.

## Testes futuros

Unitários:
- permissão → catálogo de ações;
- permissão ausente → ação ausente;
- indisponibilidade temporária → disabled com motivo quando apropriado;
- campos autorizados e mínimo necessário;
- invalidação em mudança de escopo.

Integração:
- `manager` cria funcionário sem CTA de biometria;
- `admin` com `biometrics:manage` recebe CTA permitido;
- `auditor` sem affordance de mutação;
- `operator` no fluxo de ponto sem herdar shell admin;
- componentes derivando ações/campos do escopo autorizado.

Segurança/regressão:
- busca fora de escopo;
- vazamento em contagem/filtro/paginação;
- URL direta de `DetailDrawer`;
- permissão revogada com conteúdo aberto;
- resposta stale de escopo antigo;
- nenhum flash de dados anteriores;
- `FETCH_ALL_THEN_HIDE=NO`;
- `CLIENT_CHECK_AS_AUTHORITY=NO`;
- `CONFIRMATION_BYPASSES_RBAC=NO`.

## Contrato congelado

```text
H3_RBAC_TENANT_MINIMUM_NECESSARY

current backend RBAC preserved................. YES
new backend permissions invented............... NO
ROLE = PERMISSION.............................. NO
PERMISSION = SCOPE............................. NO
ROLE = TENANT_SCOPE............................ NO
UI visibility = authorization.................. NO
client RBAC check = server authorization....... NO
backend revalidation........................... YES
forbidden action hidden........................ YES
forbidden action disabled as auth substitute... NO
temporarily unavailable may be disabled........ YES
PUNCH_CREATE = ADMIN_SHELL_ACCESS.............. NO
manager users:create........................... YES
manager biometrics:manage...................... NO
manager forbidden biometric CTA............... NO
authorized scope before query.................. YES
fetch all then hide............................ NO
rows/counts/options/metrics same scope......... YES
search authorized before matching.............. YES
pagination metadata same scope................. YES
entity authorized = every field authorized..... NO
authorized = necessary for task................ NO
minimum necessary data......................... YES
BIOMETRICS_MANAGE = RAW_BIOMETRIC_VIEW......... NO
safe error/message scope....................... YES
Toast respects current authorized scope........ YES
ErrorSummary respects authorized scope......... YES
scope change revalidates data.................. YES
stale old-scope response wins.................. NO
permission revoked retains protected data...... NO
previous-scope data flash...................... NO
route knowledge = authorization................ NO
confirmation = authorization................... NO
tenant backend implementation invented by H3... NO
authorized-scope abstraction................... YES
bulk actions revalidate effective scope........ YES
exports may bypass scope....................... NO
```

## Estado final

```text
H3_RBAC_TENANT_MINIMUM_NECESSARY_COHERENCE=COMPLETE
NEXT_OFFICIAL_ITEM=H4_OPERATIONAL_STATE_COHERENCE
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```
