# NF-01 — Fase J — J1 — Auditoria canônica de gaps do Dashboard

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
J1_DASHBOARD_CANONICAL_GAP_AUDIT=APPROVED_BY_LEANDRO
J1_STATUS=COMPLETE
PHASE_J_DASHBOARD_RECONCILIATION=IN_PROGRESS
IMPLEMENTATION=DOCUMENTAL_AUDIT_ONLY
DASHBOARD_VISUAL_CHANGE=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate autoriza somente a comparação documental da tela atual do Dashboard com os contratos canônicos da NF-01. Nenhum HTML/CSS/JS visual do Dashboard foi alterado em J1.

## Fontes auditadas

```text
docs/nf-01/01_PRODUCT_DEFINITION.md
docs/nf-01/04_ROLES_PERMISSIONS_AND_STATES.md
docs/nf-01/05_DESIGN_SYSTEM.md
docs/nf-01/06_COMPONENT_CATALOG.md
docs/nf-01/07_WIREFRAMES.md
docs/nf-01/08_RESPONSIVE_ACCESSIBILITY.md
docs/nf-01/09_TEST_AND_ACCEPTANCE_STRATEGY.md
docs/nf-01/12_NF01_CANONICAL_DECISIONS_2026-08-11.md
docs/nf-01/prototype/screens/02.01-dashboard.html
docs/nf-01/prototype/assets/dashboard-v3.css
docs/nf-01/prototype/assets/components.css  # dependência compartilhada observada, sem alteração em J1
```

## Resultado executivo

```text
J1_AUDIT_RESULT=GAPS_FOUND
CRITICAL_GAPS=0
HIGH_GAP_THEMES=6
MEDIUM_GAP_THEMES=5
LOW_DEFERRED_OBSERVATIONS=2

PRESERVE_ITEMS=6
RECONCILE_ITEMS=12
REMOVE_ITEMS=2
DEFER_ITEMS=4

J2_IMPLEMENTATION_SCOPE_REQUIRED=YES
PRODUCTION_READY=NO
```

O Dashboard atual já está estruturalmente próximo do wireframe canônico: possui os três grupos de indicadores, atividade recente e atenção necessária, usa o AppShell compartilhado e mantém dados explicitamente demonstrativos. A divergência principal está na **semântica de estados/dados, RBAC das ações e composição dos atalhos**, não na existência do casco principal.

---

# 1. Matriz Current × Canonical

| Área | Estado atual | Contrato canônico | Classificação | Severidade | Decisão J1 |
|---|---|---|---|---|---|
| AppShell | compartilhado, `active=dashboard` | AppShell único | PRESERVE | — | manter |
| PageHeader | Dashboard + descrição + data | título e visão geral | PRESERVE | — | manter hierarquia |
| Breadcrumb | não renderizado | shell geral prevê breadcrumb; wireframe raiz do Dashboard não o explicita | DEFER | LOW | não contar como gap bloqueante; decidir apenas se houver necessidade hierárquica real |
| KPI Funcionários | `24` + `+2 no mês` demonstrativo | `MetricCard`: número/unidade/período/contexto; não inventar zero | RECONCILE | HIGH | preservar métrica base; remover crescimento derivado se fonte não existir |
| KPI Registros hoje | `37` + `até 12:04` | dado real do escopo + recência/fonte | RECONCILE | HIGH | preservar; transformar recência em contrato explícito de dado/LastUpdated |
| KPI Biometrias pendentes | `2` demonstrativo | métrica operacional real, permission-aware | RECONCILE | HIGH | preservar conceito; estados e origem obrigatórios |
| Estados dos KPIs | somente READY demonstrativo | LOADING/READY/EMPTY/ERROR/OFFLINE/NO_PERMISSION/TELEMETRY_UNAVAILABLE quando aplicável | RECONCILE | HIGH | J2 deve materializar variantes sem falso verde |
| Atividade recente | 4 linhas demonstrativas | dados reais do contexto; loading/empty/error separados | RECONCILE | HIGH | preservar superfície; criar estados explícitos |
| Ações da atividade | `Ver registros` + `Abrir lista completa` | uma hierarquia de ação clara; consultar registros com `punch:view` | RECONCILE | MEDIUM | eliminar duplicidade semântica; manter um destino dominante |
| Atenção necessária | biometria pendente + “Sem outras pendências” | somente fontes reais; warning acionável | RECONCILE | HIGH | preservar painel; nunca declarar ausência de pendências sem fonte válida |
| Quick Action — Consultar registros | presente | wireframe prevê `Ver registros` | RECONCILE | MEDIUM | manter capacidade, unificar nomenclatura/hierarquia e exigir `punch:view` |
| Quick Action — Cadastrar funcionário | presente | não integra o núcleo do wireframe do Dashboard | REMOVE | MEDIUM | remover do bloco primário do Dashboard em J2; ação continua pertencendo a Funcionários quando `users:create` |
| Quick Action — Cadastrar biometria | presente, sem entidade selecionada | biometria exige `biometrics:manage` e contexto de funcionário | REMOVE | HIGH | remover do bloco genérico do Dashboard; manter no fluxo contextual de funcionário |
| Saúde operacional | ausente | wireframe mostra papel secundário; UI de saúde ainda não implementada | DEFER | MEDIUM | não criar CTA vivo até existir superfície/fonte; nunca simular healthy |
| IA/PREDIX | ausente | não ocupar card principal antes de capacidade real | PRESERVE | — | manter ausente |
| Dados demonstrativos | banner explícito + valores fictícios | futuro não se passa por presente; verdade antes de estética | PRESERVE | — | manter aviso enquanto Design Lab usar fixtures |
| RBAC do Dashboard | persona fixa `Administrador Demo`; ações não possuem variantes por papel | permissão precede affordance; manager/auditor/operator diferem | RECONCILE | HIGH | J2 deve definir variantes/visibilidade por `users:create`, `biometrics:manage`, `punch:view` |
| Estados persistentes | Toast de demo e superfícies READY | Toast só suplementar; problema persistente usa state/banner | RECONCILE | MEDIUM | não usar Toast como único tratamento de erro/offline/permissão |
| Responsividade local | CSS local usa `720px/430px`; compartilhado usa 1180/980/720/430 | alvos 360/768/1024/1440 são testes; layout deve responder à perda de espaço | RECONCILE | MEDIUM | preservar comportamento, converter política local para unidades/contratos canônicos quando J2 tocar CSS |
| Dimensionamento local | `dashboard-v3.css` usa px extensivamente | `rem/fr/minmax/clamp`; px só exceção técnica | RECONCILE | MEDIUM | normalizar CSS local em J2 sem ampliar escopo global |
| Dívida compartilhada `components.css` | também contém muitos px no conteúdo do Dashboard | mesma política canônica | DEFER | MEDIUM | registrar dívida transversal; não reescrever arquivo compartilhado em J2 sem gate próprio |
| A11y source-level | headings, roles, labels visíveis e estados textuais presentes | teclado/foco/reader/zoom/contraste precisam evidência | DEFER | LOW | validação completa permanece Fase N |
| Ponto | não aparece como conteúdo do Dashboard | `/punch` fora do AppShell admin | PRESERVE | — | manter fronteira |
| Saúde técnica como KPI principal | ausente | saúde técnica não compete com operação | PRESERVE | — | manter secundária |

---

# 2. Gaps HIGH que J2 deve resolver

## J1-H1 — MetricCards sem contrato completo de estado/origem

```text
CURRENT=READY_DEMO_ONLY
CANONICAL=LOADING|READY|EMPTY|ERROR|OFFLINE|NO_PERMISSION|TELEMETRY_UNAVAILABLE_AS_APPLICABLE
```

Os valores demonstrativos são aceitáveis no laboratório porque o banner os identifica como fixtures, mas a composição atual ainda não demonstra o comportamento quando a fonte estiver ausente, carregando ou falhando.

## J1-H2 — crescimento `+2 no mês` sem fonte canônica declarada

O wireframe exige `Funcionários`, não uma tendência mensal. J2 deve manter o total e só preservar a tendência se houver fonte real definida. Caso contrário, remover a tendência do mock canônico.

## J1-H3 — atividade recente sem estados alternativos

A superfície deve distinguir:

```text
LOADING
EMPTY
READY
ERROR
OFFLINE
NO_PERMISSION
```

Uma lista fixa não basta como contrato de produto.

## J1-H4 — “Sem outras pendências” pode virar falso verde

A frase é segura apenas enquanto explicitamente limitada ao mock. A variante canônica precisa derivar ausência de pendências de uma consulta válida; erro/telemetria indisponível não podem produzir “sem pendências”.

## J1-H5 — ação genérica `Cadastrar biometria`

A ação exige `biometrics:manage` e entidade de funcionário. Um atalho genérico no Dashboard cria affordance sem contexto e pode aparecer para `manager`/`auditor` se o protótipo for reutilizado sem variante RBAC.

## J1-H6 — RBAC ainda não materializado nas variantes do Dashboard

O mock atual representa apenas `Administrador Demo`. J2 deve tornar explícito o comportamento de:

```text
admin/super_admin
manager
auditor
operator
```

sem inventar permissões novas.

---

# 3. Gaps MEDIUM

```text
J1-M1  duas ações equivalentes dentro de Atividade recente
J1-M2  bloco Quick Actions diverge do núcleo do wireframe
J1-M3  Saúde operacional deve permanecer diferida até existir superfície/fonte real
J1-M4  dashboard-v3.css usa px como política geral
J1-M5  dívida de dimensionamento em components.css é transversal e não deve ser corrigida silenciosamente em J2
```

---

# 4. Itens PRESERVE

```text
P1 AppShell compartilhado
P2 título/descrição “Dashboard / visão geral da operação”
P3 IA/PREDIX ausente do Dashboard principal
P4 banner explícito de dados demonstrativos no Design Lab
P5 /punch fora da experiência administrativa
P6 saúde técnica ausente dos KPIs principais
```

Os três conceitos de KPI, Atividade recente e Atenção necessária são **preservados como conceitos**, mas classificados como `RECONCILE` porque seus contratos de estado/origem ainda precisam ser materializados.

---

# 5. Itens REMOVE na próxima implementação aprovada

```text
R1 quick action genérica “Cadastrar funcionário” do bloco primário do Dashboard
R2 quick action genérica “Cadastrar biometria” do bloco primário do Dashboard
```

Isto não remove as capacidades do produto. Apenas retira esses atalhos da composição canônica do Dashboard; `Cadastrar funcionário` permanece na superfície Funcionários e biometria permanece contextual/permissional.

---

# 6. Itens DEFER

```text
D1 Breadcrumb visível no Dashboard raiz — decidir só se hierarquia real exigir
D2 Saúde operacional viva — aguardar superfície/fonte real; não fingir implementação
D3 dívida global de px em components.css — tratar em gate transversal apropriado
D4 validação manual/automatizada completa de a11y/responsividade — Fase N
```

---

# 7. Escopo implementável proposto para J2

```text
J2_DASHBOARD_CANONICAL_RECONCILIATION

TARGETS=
  docs/nf-01/prototype/screens/02.01-dashboard.html
  docs/nf-01/prototype/assets/dashboard-v3.css

GOALS=
  preserve canonical three KPI concepts
  remove unsupported monthly trend unless source contract exists
  materialize KPI state variants
  materialize Activity recent state variants
  harden Attention against false-green semantics
  reconcile action hierarchy to one clear records action
  remove generic create-employee/biometric shortcuts from Dashboard
  document/represent RBAC variants without inventing permissions
  keep health operational deferred/not-live
  normalize touched local dashboard CSS toward rem/fr/minmax/clamp

DO_NOT=
  rewrite components.css globally
  start Phase K
  start Phase L
  implement backend
  create production routes/templates
  implement health backend/UI
  implement AI/PREDIX
  start NF02
  merge PR
```

## Testes derivados para J2+

### Unitários futuros

```text
MetricCard source missing != zero
MetricCard error != empty
Attention valid-empty => no-pending state
Attention error/unknown => never “sem pendências”
manager => no biometrics CTA
auditor => no mutation CTA
operator => no admin Dashboard
records action => requires punch:view
```

### Integração futura

```text
Dashboard READY with real scoped data
Dashboard LOADING → READY
Dashboard LOADING → ERROR
Dashboard valid EMPTY/zero-domain scenarios without invented data
Dashboard manager/auditor variants
Dashboard responsive 360/768/1024/1440 + intermediates
Dashboard zoom 200% + keyboard + screen reader
```

---

# 8. Limites preservados

```text
DASHBOARD_VISUAL_CHANGE_IN_J1=NO
PRODUCTION_CODE_CHANGED=NO
APP_CHANGED=NO
TEMPLATES_CHANGED=NO
STATIC_CHANGED=NO
MIGRATIONS_CHANGED=NO
BACKEND_CHANGED=NO
DECISOES_CONGELADAS_CHANGED=NO
NF02_STARTED=NO
PONTO_TO_ATTENDANCE_EVENT_MIGRATION=NO
AI_IMPLEMENTED=NO
OBSERVABILITY_BACKEND_IMPLEMENTED=NO
DEPLOY=NO
PRODUCTION_HOMOLOGATION=NO
LEGAL_CONFORMITY_DECLARED=NO
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
PR_MERGE=NOT_AUTHORIZED
FINAL_HUMAN_GATE=NOT_READY
```

## Próxima fronteira

```text
NEXT_OFFICIAL_PHASE=J_DASHBOARD_RECONCILIATION
NEXT_OFFICIAL_ITEM=J2_DASHBOARD_CANONICAL_RECONCILIATION_GATE
```

Nenhuma aprovação de J2 é inferida deste gate.
