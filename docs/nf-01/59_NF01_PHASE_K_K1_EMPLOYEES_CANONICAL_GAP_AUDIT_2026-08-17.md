# NF-01 — Fase K — K1 — Auditoria canônica de gaps de Funcionários

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
K1_EMPLOYEES_CANONICAL_GAP_AUDIT=APPROVED_BY_LEANDRO
K1_STATUS=COMPLETE
PHASE_K_EMPLOYEES_RECONCILIATION=IN_PROGRESS
IMPLEMENTATION=DOCUMENTAL_AUDIT_ONLY
EMPLOYEES_VISUAL_CHANGE=NO
EMPLOYEES_HTML_CHANGED=NO
EMPLOYEES_CSS_CHANGED=NO
EMPLOYEES_JS_CHANGED=NO
PRODUCTION_CHANGE=NO
PHASE_L=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate autoriza somente a comparação Current × Canonical da superfície Funcionários do Design Lab. Nenhuma alteração visual/funcional em `03.01-funcionarios.html`, `employees-v1.css` ou `employees-v1.js` foi autorizada em K1.

---

## Fontes auditadas

```text
docs/nf-01/01_PRODUCT_DEFINITION.md
docs/nf-01/02_UI_INVENTORY.md
docs/nf-01/04_ROLES_PERMISSIONS_AND_STATES.md
docs/nf-01/06_COMPONENT_CATALOG.md
docs/nf-01/07_WIREFRAMES.md
docs/nf-01/08_RESPONSIVE_ACCESSIBILITY.md
docs/nf-01/09_TEST_AND_ACCEPTANCE_STRATEGY.md
docs/nf-01/12_NF01_CANONICAL_DECISIONS_2026-08-11.md
docs/nf-01/13_NF01_REMAINING_WORK_ROADMAP.md
docs/nf-01/prototype/screens/03.01-funcionarios.html
docs/nf-01/prototype/assets/employees-v1.css
docs/nf-01/prototype/assets/employees-v1.js
docs/nf-01/prototype/assets/app-shell.css
docs/nf-01/prototype/assets/app-shell.js
```

---

## Resultado executivo

```text
K1_AUDIT_RESULT=GAPS_FOUND
CRITICAL_GAPS=0
HIGH_GAP_THEMES=7
MEDIUM_GAP_THEMES=6
LOW_DEFERRED_OBSERVATIONS=2

PRESERVE_ITEMS=7
RECONCILE_ITEMS=13
REMOVE_ITEMS=2
DEFER_ITEMS=4

K2_IMPLEMENTATION_SCOPE_REQUIRED=YES
PRODUCTION_READY=NO
```

A tela atual já possui boa base de experiência: AppShell compartilhado, breadcrumb, PageHeader, busca diretamente acessível, filtros frequentes, tabela com adaptação para cards em telas menores e estado local de busca sem resultado. A divergência canônica está principalmente em **semântica dos resumos/dados, hierarquia das colunas, RBAC das ações, estados de carregamento/falha/permissão e paginação demonstrativa que simula dados não existentes**.

---

# 1. Matriz Current × Canonical

| Área | Estado atual | Contrato canônico | Classificação | Severidade | Decisão K1 |
|---|---|---|---|---|---|
| AppShell | compartilhado, `active=employees` | AppShell administrativo único | PRESERVE | — | manter |
| Breadcrumb/PageHeader | `Gestão > Funcionários`, título e descrição | localização + título + ação principal | PRESERVE | — | manter hierarquia |
| CTA Novo funcionário | sempre visível, ação demo | somente para `users:create` | RECONCILE | HIGH | tornar permission-aware e apontar ao fluxo canônico quando permitido |
| Aviso de dados demonstrativos | explícito | futuro não se passa por presente | PRESERVE | — | manter e endurecer origem/estado |
| Resumo — funcionários exibidos | contador muda conforme filtro local | card `Total` deve representar total/contexto real; resultado filtrado é outra informação | RECONCILE | HIGH | separar total do dataset de contagem visível |
| Resumo — sem biometria | valor fixo `2` sem fonte/estado declarados | métrica real/source-aware e permission/context-aware | RECONCILE | HIGH | explicitar origem/estado; não inventar valor |
| Resumo — `Admin` | persona mostrada como terceiro “indicador” | “outros reais” somente se houver métrica de negócio real | REMOVE | MEDIUM | remover do bloco de métricas; papel/permissão pertence ao contrato de acesso, não a KPI |
| Busca | nome ou matrícula | Search diretamente acessível | PRESERVE | — | manter |
| Filtro biometria | todas/ativa/não cadastrada | filtro frequente visível | PRESERVE | — | manter conceito |
| Filtro função | opções locais de função | FilterBar estruturada | PRESERVE/RECONCILE | LOW | manter conceito; renomear contrato interno para `function` para não confundir função com access role |
| Limpar filtros | ação própria | Search/FilterBar devem ser canceláveis/limpáveis | PRESERVE | — | manter |
| Colunas principais | Funcionário, Usuário, Função, Biometria, Ações | Nome/Matrícula, Unidade, Biometria, Status, ações | RECONCILE | HIGH | incluir Unidade + Status e rebaixar dados de conta/função conforme prioridade real |
| Coluna Usuário | tratada como campo primário | `FUNCIONARIO != CONTA_DE_USUARIO` | RECONCILE | MEDIUM | não usar conta como identidade principal da pessoa; mover para detalhe/coluna secundária quando aplicável |
| Biometria por linha | `Ativa` / `Não cadastrada` | status textual + semântica | PRESERVE/RECONCILE | MEDIUM | manter conceito; adicionar fonte/estado quando necessário |
| Cadastrar/Recadastrar biometria | visível em todas as linhas | exige `biometrics:manage`; manager/auditor não recebem CTA | RECONCILE | HIGH | esconder quando não permitido; CTA deve ser contextual à pessoa |
| Menu `•••` | ação demo genérica em todas as linhas | ações nomeadas/focáveis e filtradas por permissão | RECONCILE | HIGH | definir menu permission-aware; não sugerir mutações ao auditor |
| Estado READY | seis fixtures visíveis | READY é apenas um dos estados | RECONCILE | HIGH | manter fixture READY, mas declará-la explicitamente |
| Empty local de filtros | “Nenhum funcionário encontrado” ao filtrar 0 | distinguir `FILTER_NO_RESULTS` de `EMPTY` da coleção | RECONCILE | HIGH | manter no-results local e criar Empty real separado |
| LOADING/ERROR/OFFLINE/NO_PERMISSION | não materializados | estados obrigatórios e distintos | RECONCILE | HIGH | criar contratos visuais source-level em K2 |
| Paginação | botões 1/2/Próxima sobre seis fixtures sem página 2 real | não fingir paginação sobre amostra parcial | REMOVE | HIGH | remover paginação viva fictícia; só reapresentar com contrato/dataset explícito |
| DataTable sorting | não existe | DataTable canônica prevê sorting + `aria-sort` quando ordenável | RECONCILE | MEDIUM | definir sorting somente se houver coluna realmente ordenável; não fingir funcionalidade |
| Ações por linha | rótulos visuais `Cadastrar`/`Recadastrar` | ação nomeada e focável | RECONCILE | MEDIUM | nome acessível deve incluir ação + funcionário |
| Navegação para Novo Funcionário | botão demo sem fluxo real do Design Lab | fluxo canônico `03.04-novo-funcionario-v2.html` existe no laboratório | RECONCILE | MEDIUM | K2 pode conectar a superfície quando `users:create` |
| Responsividade | tabela `min-width: 840px`; cards apenas `<=720px` | ~768 deve permanecer utilizável; mobile não espreme/força overflow | RECONCILE | MEDIUM | eliminar faixa intermediária problemática e preferir resposta ao container/espaço real |
| Dimensionamento local | `employees-v1.css` usa `px` extensivamente | `rem/fr/minmax/clamp`; px só exceção técnica | RECONCILE | MEDIUM | normalizar apenas a camada local tocada por K2 |
| Shared `components.css` | dívida transversal de dimensionamento permanece | política canônica compartilhada | DEFER | MEDIUM | não reescrever silenciosamente em K2 |
| DetailDrawer | não existe | componente canônico possível para detalhe sem perder contexto | DEFER | LOW | não criar sem necessidade real comprovada |
| Validação a11y/responsiva completa | não executada | matriz 360/768/1024/1440 + zoom/teclado/screen reader | DEFER | LOW | permanece Fase N |
| Coerência Dashboard × Funcionários | não validada neste gate | coerência entre telas é fase própria | DEFER | LOW | Fase M |

---

# 2. Gaps HIGH que K2 deve resolver

## K1-H1 — Resumos sem contrato confiável de significado/origem

O primeiro card representa **linhas visíveis após filtros**, enquanto o wireframe chama o conceito de `Total`. O segundo card usa `2` fixo sem metadado de fonte/estado e o terceiro card apresenta `Admin` como se fosse métrica.

```text
CURRENT=
  visible_filter_count
  fixed_biometric_count
  persona_as_metric

CANONICAL=
  real_total_or_explicit_fixture_total
  real_biometric_pending_or_explicit_fixture
  only real additional metric
```

K2 deve separar “total da coleção” de “resultados visíveis” e remover o pseudo-KPI de papel administrativo.

## K1-H2 — Hierarquia da tabela não corresponde à hierarquia canônica

Current:

```text
Funcionário | Usuário | Função | Biometria | Ações
```

Canonical:

```text
Nome/Matrícula | Unidade | Biometria | Status | Ações
```

`Usuário` não deve substituir o contexto operacional de `Unidade` nem o estado da pessoa/vínculo. O produto também congela `FUNCIONARIO != CONTA_DE_USUARIO`.

## K1-H3 — CTA Novo funcionário não materializa `users:create`

O botão está sempre presente no mock.

```text
super_admin/admin/manager => pode receber CTA
operator/auditor           => CTA ausente
```

Metadata visual não substitui autorização backend.

## K1-H4 — ações biométricas ignoram `biometrics:manage`

Todas as linhas exibem `Cadastrar` ou `Recadastrar` biometria. Isso conflita diretamente com a matriz real:

```text
super_admin/admin => ação
manager           => ocultar
auditor           => ocultar
operator          => ocultar
```

## K1-H5 — estados da coleção estão incompletos e Empty está conflado

A tela possui somente:

```text
READY_FIXTURE
FILTER_NO_RESULTS
```

Precisa distinguir:

```text
LOADING
EMPTY_DATASET
READY
FILTER_NO_RESULTS
ERROR
OFFLINE
NO_PERMISSION
```

`FILTER_NO_RESULTS != EMPTY_DATASET != ERROR`.

## K1-H6 — paginação viva é fictícia

A superfície renderiza páginas `1`, `2` e `Próxima`, mas o JS possui apenas seis linhas locais e não existe segunda página real. O catálogo canônico proíbe fingir paginação sobre amostra parcial.

```text
FAKE_PAGINATION=REMOVE
REAL_PAGINATION=FUTURE_CONTRACT_ONLY_UNTIL_DATASET_EXISTS
```

## K1-H7 — RBAC da linha/menu ainda não existe como variante

O menu `•••` e os CTAs biométricos são iguais independentemente do papel. K2 precisa materializar variantes source-level sem fingir enforcement:

```text
admin/super_admin => leitura + ações permitidas
manager           => leitura + criar funcionário; sem biometria
auditor           => leitura; sem mutações
operator          => sem superfície administrativa
```

---

# 3. Gaps MEDIUM

```text
K1-M1  coluna Usuário é primária demais para um domínio onde funcionário != conta
K1-M2  ações `Cadastrar/Recadastrar` precisam nome acessível contextual
K1-M3  sorting/aria-sort não possui contrato quando aplicável
K1-M4  responsive gap entre tabela 840px e conversão para cards em 720px
K1-M5  employees-v1.css usa px como política geral
K1-M6  CTA Novo funcionário é apenas demo action apesar do fluxo V2 existir no Design Lab
```

---

# 4. Itens PRESERVE

```text
P1 AppShell compartilhado
P2 breadcrumb + PageHeader
P3 busca diretamente acessível
P4 filtros frequentes visíveis
P5 status biométrico textual por pessoa
P6 conversão conceitual tabela → cards no mobile
P7 aviso explícito de dados demonstrativos
```

---

# 5. Itens REMOVE na próxima implementação aprovada

```text
R1 summary card `Admin` do bloco de indicadores
R2 paginação viva fictícia sobre a amostra local
```

Remover a paginação fictícia não elimina a capacidade futura de paginação. A paginação volta quando houver dataset/contrato verdadeiro para demonstrá-la.

---

# 6. Itens DEFER

```text
D1 dívida global de dimensionamento em components.css
D2 DetailDrawer até existir necessidade comprovada
D3 validação visual/a11y/responsiva completa → Fase N
D4 coerência cruzada Dashboard × Funcionários × Onboarding → Fase M
```

---

# 7. Escopo implementável proposto para K2

```text
K2_EMPLOYEES_CANONICAL_RECONCILIATION

TARGETS=
  docs/nf-01/prototype/screens/03.01-funcionarios.html
  docs/nf-01/prototype/assets/employees-v1.css
  docs/nf-01/prototype/assets/employees-v1.js

GOALS=
  preserve shared AppShell and current content intent
  make visible fixture role/permissions explicit
  make New employee CTA users:create-aware
  make biometric row actions biometrics:manage-aware
  define permission-aware row action contract
  replace summary pseudo-metrics with source/state-aware summaries
  separate dataset total from filtered-visible result count
  reconcile table priorities to include Unidade + Status
  demote account username from primary employee identity
  define LOADING|EMPTY_DATASET|READY|FILTER_NO_RESULTS|ERROR|OFFLINE|NO_PERMISSION
  remove fake live pagination
  keep search + frequent filters
  preserve mobile summary/card strategy
  normalize touched local CSS toward rem/fr/minmax/container-aware behavior
  connect New employee CTA to Design Lab V2 only when permitted

DO_NOT=
  rewrite components.css globally
  implement backend permission enforcement
  add production routes/templates
  start Phase L
  start Phase M
  start Phase N
  start NF02
  merge PR
```

---

# 8. Testes derivados para K2+

## Unitários futuros

```text
users:create absent => New employee CTA not rendered
biometrics:manage absent => biometric CTAs not rendered
employee collection source missing != total zero
filter no results != empty dataset
error != empty
offline != error
filtered visible count does not overwrite dataset total
pagination absent when no pagination dataset/contract exists
```

## Integração futura

```text
admin/super_admin => read + create + biometrics affordances
manager => read + create; no biometrics affordance
auditor => read-only; no mutation affordance
operator => no Employees/AppShell admin

Employees READY → filter → FILTER_NO_RESULTS → clear → READY
Employees LOADING → READY
Employees LOADING → ERROR
Employees OFFLINE remains persistent and is not Toast-only
Funcionários → Novo Funcionário preserves shared AppShell
search/filters preserve expected state across intended navigation
```

---

# 9. Limites do K1

```text
BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
INTERMEDIATE_WIDTH_VISUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
SCREEN_READER_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

Portanto:

```text
K1_COMPLETE != PHASE_K_COMPLETE
K1_COMPLETE != VISUAL_HOMOLOGATION
K1_COMPLETE != AUTOMATED_TEST_PASS
K1_COMPLETE != PRODUCTION_READY
```

---

# 10. Próxima fronteira

```text
NEXT_OFFICIAL_PHASE=K_EMPLOYEES_RECONCILIATION
NEXT_OFFICIAL_ITEM=K2_DEFINITION_GATE
```

K2 deve executar somente a reconciliação comprovada por esta matriz. Nenhuma aprovação de K2 é inferida deste gate.