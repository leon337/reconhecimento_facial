# NF-01 — Roadmap oficial do trabalho restante

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Status:** `IN_PROGRESS`  
**Produção:** inalterada  
**NF-02:** não iniciada  
**Merge:** não autorizado  
**Gate humano final:** LEANDRO  

---

## 0. Objetivo

Este documento é o **controle operacional do que ainda falta concluir na NF-01**.

Ele existe para que a continuidade da fase não dependa de memória de chat, resumos informais ou contexto implícito.

### Fontes de verdade

```text
DECISOES_CONGELADAS.md
        ↓
12_NF01_CANONICAL_DECISIONS_2026-08-11.md
        ↓
13_NF01_REMAINING_WORK_ROADMAP.md
        ↓
demais documentos/protótipos da NF-01
```

Interpretação:

- `12_*` registra **o que já foi decidido/congelado**;
- `13_*` registra **o que ainda falta executar/revisar para encerrar a NF-01**;
- se um documento antigo sugerir que toda revisão de componentes terminou, mas este roadmap marcar revisão individual como pendente, **este roadmap controla o status operacional do trabalho restante**;
- nenhuma linha deste roadmap autoriza NF-02, produção, backend, migração, IA, deploy ou merge.

---

# 1. Estado consolidado

```text
NF01_STATUS=IN_PROGRESS
CANONICAL_DECISIONS=DOCUMENTED
PRODUCTION_CODE_CHANGED=NO
NF02_STARTED=NO
PR32_MERGED=NO
FINAL_HUMAN_GATE=NOT_READY
```

### RC transversal

```text
CRITICAL_GAPS_CLOSED=6/6
HIGH_GAPS_CLOSED=9/9
MEDIUM_GAPS_CLOSED=6/6
```

Isso significa que as lacunas transversais encontradas pela RC foram tratadas em especificação.

**Não significa que todos os componentes do catálogo passaram por revisão individual profunda.**

### Status correto do catálogo

```text
COMPONENT_CATALOG_BASELINE=FROZEN
COMPONENT_INDIVIDUAL_REVIEW=IN_PROGRESS
```

A baseline define nomes, papéis, estados gerais e limites. A revisão individual aprofunda comportamento, variantes, interação, responsividade, acessibilidade, RBAC, testes e anti-padrões antes de cada componente ser considerado encerrado individualmente.

---

# 2. Componentes já revisados individualmente e congelados

```text
[x] CollapsibleSidebar
[x] HorizontalStepper
[x] ContextDrawer
[x] StickyFormActions
[x] ResponsiveFormGrid
[x] FormSection + Progressive Disclosure
[x] FieldGroup / InlineHelp / ValidationMessage
[x] SearchableCombobox / EntityPicker
[x] Date / Time / Period Picker
[x] AppShell
[x] TopHeader
[x] Breadcrumb
[x] PageHeader
[x] Button
```

Os cinco últimos itens foram revisados e aprovados por LEANDRO em lote, por autorização humana explícita. O contrato detalhado está em:

```text
docs/nf-01/15_NF01_COMPONENT_REVIEW_BATCH_A1_A4_B1_2026-08-11.md
```

```text
BATCH_REVIEW_EXCEPTION_APPROVED_BY_LEANDRO=YES
APPROVAL_SCOPE=A1+A2+A3+A4+B1
```

Políticas transversais já congeladas e que governam os componentes restantes:

```text
[x] Dimensioning Policy — rem/fr/minmax/clamp/container queries
[x] Responsive != shrink everything
[x] Wizard State + Draft/Conflict Model
[x] Dependency Invalidation
[x] Conditional Data Lifecycle
[x] Submit Outcome Reconciliation
[x] Runtime Permission Revalidation
[x] Browser Back/Forward/Refresh
[x] Session Expiration Recovery
[x] Stepper Discoverability / NEEDS_REVIEW
[x] App Context != Form Company
[x] Required/Optional Policy
[x] Error Hierarchy
[x] Step Focus Management
[x] Mobile Keyboard Safe Actions
[x] Design Tokens baseline
[x] Lucide Icon System
[x] Motion / Reduced Motion
[x] Semantic DOM Order
[x] Toast Policy
```

---

# 3. Regra para revisão individual de cada componente restante

Cada componente pendente deve passar pelo seguinte checklist antes de receber `FROZEN_INDIVIDUALLY`:

```text
1. propósito e problema que resolve
2. anatomia
3. variantes permitidas
4. estados
5. comportamento e interações
6. dependências com outros componentes
7. RBAC / privacidade quando aplicável
8. responsividade / container behavior
9. teclado / foco / screen reader
10. loading / empty / error / offline quando aplicável
11. anti-padrões / uso proibido
12. testes unitários futuros
13. testes de integração futuros
14. testes responsivos/a11y futuros
15. RC rápida: “há melhoria aplicável ainda não incorporada?”
16. aprovação humana explícita
17. marcar como FROZEN_INDIVIDUALLY
```

O padrão continua sendo revisão individual. O lote `A1+A2+A3+A4+B1` é uma exceção explicitamente autorizada por LEANDRO e não altera automaticamente o método dos componentes seguintes.

Analogia operacional: cada componente é uma peça da linha de montagem. Estar listado no catálogo significa que a peça existe no projeto; passar pela revisão individual significa que ela foi inspecionada antes de entrar no conjunto final.

---

# 4. Fase A — Revisão individual dos componentes estruturais restantes

**Objetivo:** fechar o esqueleto comum das páginas antes de desenhar telas finais.

```text
[x] A1 AppShell
[x] A2 TopHeader
[x] A3 Breadcrumb
[x] A4 PageHeader
```

### Critério de saída da Fase A

```text
APPSHELL_COMPONENT=FROZEN_INDIVIDUALLY
TOP_HEADER=FROZEN_INDIVIDUALLY
BREADCRUMB=FROZEN_INDIVIDUALLY
PAGE_HEADER=FROZEN_INDIVIDUALLY
```

```text
PHASE_A_COMPONENT_REVIEW=COMPLETE
```

---

# 5. Fase B — Ações, navegação local e ajuda

```text
[x] B1 Button
[ ] B2 IconButton
[ ] B3 Tooltip
[ ] B4 Tabs
```

Observações:

- `Tooltip` nunca contém informação obrigatória;
- `IconButton` precisa de nome acessível e contexto suficiente;
- `Tabs` não substitui wizard nem navegação principal;
- hierarquia `primary / secondary / tertiary / destructive` deve permanecer consistente com `StickyFormActions`.

**Próxima ação oficial:** `B2 — revisar IconButton como componente`, sem ainda aplicar visualmente às telas.

---

# 6. Fase C — Status, métricas e recência

```text
[ ] C1 StatusBadge
[ ] C2 MetricCard
[ ] C3 HealthCard
[ ] C4 LastUpdated
```

Guardrail obrigatório:

```text
BRAND_GREEN != HEALTHY
TELEMETRY_UNAVAILABLE != SUCCESS
NO_SOURCE => NO_INVENTED_STATUS
```

Essa fase deve preservar a política de “sem falso verde”.

---

# 7. Fase D — Busca, filtros e dados tabulares

```text
[ ] D1 Search
[ ] D2 FilterBar
[ ] D3 DataTable
[ ] D4 Pagination
```

Pontos de revisão obrigatórios:

- busca e filtro não são a mesma coisa;
- filtros ativos nunca ficam invisíveis;
- DataTable não deve ser esmagada em mobile;
- 360 px pode usar resumo/lista + DetailDrawer sem perder semântica;
- ordenação e paginação devem ser acessíveis;
- preservar estado de busca/filtro/página quando apropriado.

---

# 8. Fase E — Estados de sistema e feedback

```text
[ ] E1 EmptyState
[ ] E2 ErrorState
[ ] E3 Skeleton
[ ] E4 DegradationBanner
[~] E5 Toast — política transversal já congelada; realizar apenas revisão de integração/coerência
```

Regra:

```text
EMPTY != ERROR
ERROR_CRITICO != TOAST_APENAS
LOADING_TIMEOUT => ESTADO_TERMINAL_RECUPERAVEL
```

---

# 9. Fase F — Overlays, confirmação e histórico de eventos

```text
[ ] F1 DetailDrawer
[ ] F2 ConfirmationModal
[ ] F3 EventTimeline
```

Pontos obrigatórios:

- focus trap somente quando a semântica exigir;
- retorno de foco ao disparador;
- Escape e fechamento explícito;
- confirmação destrutiva deve mostrar entidade + consequência;
- EventTimeline não pode inventar causalidade entre eventos.

---

# 10. Fase G — Câmera e resultado de ponto

```text
[ ] G1 CameraPanel
[ ] G2 PunchResult
```

Esses dois componentes exigem revisão aprofundada porque participam de fluxos operacionais sensíveis.

### CameraPanel

Revisar pelo menos:

```text
CAMERA_PERMISSION_REQUIRED
CAMERA_UNAVAILABLE
CAMERA_READY
CAPTURE_PREPARING
CAPTURING
VALIDATING_QUALITY
PROCESSING
SUCCESS
FAILURE
```

Guardrails:

- câmera ao vivo no fluxo normal;
- não usar galeria/upload como atalho;
- texto de estado acompanha preview;
- não mostrar frame congelado como câmera ativa;
- acessível por teclado nos controles aplicáveis;
- reduced motion respeitado.

### PunchResult

Revisar pelo menos:

```text
SUCCESS_CONFIRMED
RETRYABLE_ERROR
DUPLICATE_BLOCKED
OFFLINE/NETWORK_ERROR quando distinguível
OUTCOME_UNKNOWN quando aplicável
```

Guardrail:

```text
SUCCESS somente após confirmação real do servidor/persistência correspondente.
```

---

# 11. Fase H — RC de completude do catálogo

Somente após A–G:

```text
[ ] H1 comparar 06_COMPONENT_CATALOG.md com todos os contratos individuais
[ ] H2 verificar componente listado sem revisão profunda
[ ] H3 verificar duplicações conceituais
[ ] H4 verificar inconsistências de estados
[ ] H5 verificar consistência de nomes
[ ] H6 verificar RBAC entre componentes
[ ] H7 verificar acessibilidade transversal
[ ] H8 verificar responsividade/container behavior transversal
[ ] H9 verificar testes futuros unitários/integrados previstos
[ ] H10 corrigir documentação residual conflitante
```

Saída:

```text
COMPONENT_INDIVIDUAL_REVIEW=COMPLETE
COMPONENT_CATALOG=FINAL_FOR_NF01
```

---

# 12. Fase I — Reconciliar o shell visual no Design Lab

**Somente depois da revisão individual dos componentes.**

```text
[ ] I1 materializar AppShell canônico no Design Lab
[ ] I2 CollapsibleSidebar expandida/compacta/overlay
[ ] I3 TopHeader
[ ] I4 Breadcrumb + PageHeader
[ ] I5 validar área útil recuperada pelo conteúdo
[ ] I6 validar navegação e estado ativo
[ ] I7 validar 360/768/1024/1440+
[ ] I8 validar zoom 200%
[ ] I9 validar teclado/foco
```

Nenhum código de produção.

---

# 13. Fase J — Reconciliar Dashboard

Preservar conteúdo/decisões aprovadas; trocar shell/distribuição quando necessário.

```text
[ ] J1 aplicar AppShell canônico
[ ] J2 preservar operação como protagonista
[ ] J3 preservar política sem falso verde
[ ] J4 revisar cards/métricas/atividade/alertas
[ ] J5 validar densidade e área útil
[ ] J6 responsividade
[ ] J7 acessibilidade
[ ] J8 RC visual
```

---

# 14. Fase K — Reconciliar Funcionários

```text
[ ] K1 aplicar AppShell canônico
[ ] K2 preservar título + Novo funcionário
[ ] K3 preservar métricas aprovadas
[ ] K4 revisar Search + FilterBar
[ ] K5 revisar DataTable / fallback mobile
[ ] K6 preservar estado biométrico e ações por permissão
[ ] K7 responsividade
[ ] K8 acessibilidade
[ ] K9 RC visual
```

---

# 15. Fase L — Reconciliar Novo Funcionário V2

O contrato funcional de oito etapas permanece congelado.

```text
[ ] L1 remover stepper vertical residual
[ ] L2 aplicar HorizontalStepper icon-first
[ ] L3 adicionar “Ver etapas” sob demanda
[ ] L4 aplicar ContextDrawer sob demanda
[ ] L5 aplicar ResponsiveFormGrid
[ ] L6 aplicar FormSection / Progressive Disclosure
[ ] L7 aplicar FieldGroup canônico
[ ] L8 aplicar EntityPicker e Date/Time/Period
[ ] L9 aplicar StickyFormActions
[ ] L10 demonstrar Wizard State / autosave / conflito / NEEDS_REVIEW
[ ] L11 demonstrar Error Hierarchy
[ ] L12 demonstrar permissões de biometria
[ ] L13 demonstrar revisão/conclusão sem CTA prematuro
[ ] L14 responsividade 360/768/1024/1440+
[ ] L15 zoom 200%
[ ] L16 teclado/foco/a11y
[ ] L17 RC visual
```

---

# 16. Fase M — Coerência entre telas

```text
[ ] M1 Dashboard, Funcionários e Novo Funcionário usam o mesmo shell
[ ] M2 mesmas ações usam mesma hierarquia visual
[ ] M3 mesmos estados usam mesma linguagem
[ ] M4 sidebar mantém comportamento entre telas
[ ] M5 header mantém contexto consistente
[ ] M6 spacing/tokens consistentes
[ ] M7 não existem componentes duplicados ad hoc
[ ] M8 nenhum protótipo contradiz registro canônico
```

---

# 17. Fase N — Validação do Design Lab

### Responsividade

```text
[ ] 360
[ ] 768
[ ] 1024
[ ] 1440+
[ ] larguras intermediárias orientadas pelo conteúdo
[ ] portrait/landscape quando aplicável
[ ] teclado virtual mobile
```

### Acessibilidade

```text
[ ] teclado completo
[ ] Tab / Shift+Tab
[ ] foco visível
[ ] retorno de foco drawer/modal
[ ] foco após mudança de etapa
[ ] foco/summary após erro
[ ] zoom 200% / reflow
[ ] reduced motion
[ ] labels / aria-describedby
[ ] aria-current / aria-live
[ ] screen reader nos fluxos críticos
[ ] contraste real dos estados finais
```

### Testes futuros — contrato

A NF-01 continua sem afirmar execução de testes de produção da nova UI. Antes do Gate, porém, a documentação deve continuar explicitando o que a NF-02 deverá automatizar:

```text
UNITARIOS
INTEGRACAO
REGRESSAO
RESPONSIVO
ACESSIBILIDADE
SEGURANCA
```

---

# 18. Fase O — Evidências, auditoria e fechamento

```text
[ ] O1 atualizar evidências visuais
[ ] O2 atualizar 07_WIREFRAMES.md se necessário
[ ] O3 atualizar 08_RESPONSIVE_ACCESSIBILITY.md se necessário
[ ] O4 atualizar 09_TEST_AND_ACCEPTANCE_STRATEGY.md
[ ] O5 executar revisão independente final da NF-01
[ ] O6 reconciliar 10_NF01_CLOSEOUT.md
[ ] O7 atualizar PR #32
[ ] O8 verificar CI/evidências aplicáveis
[ ] O9 confirmar invariantes de produção
[ ] O10 solicitar Gate humano final de LEANDRO
```

Somente após aprovação explícita:

```text
FINAL_HUMAN_GATE=APPROVED
```

O merge continua sendo uma ação separada e também não deve ser inferido.

---

# 19. Definição de pronto da NF-01

A NF-01 somente pode ser considerada pronta quando **todos** forem verdadeiros:

```text
[ ] decisões canônicas reconciliadas
[ ] revisão individual dos componentes concluída
[ ] catálogo final reconciliado
[ ] AppShell visual reconciliado
[ ] Dashboard reconciliado
[ ] Funcionários reconciliado
[ ] Novo Funcionário reconciliado
[ ] coerência entre telas validada
[ ] responsividade validada no Design Lab
[ ] acessibilidade validada no nível aplicável à NF-01
[ ] contrato de testes da NF-02 atualizado
[ ] revisão independente concluída
[ ] PR #32 atualizado
[ ] nenhuma mudança de produção fora do escopo
[ ] Gate humano explícito de LEANDRO
```

---

# 20. Guardrails permanentes até o fechamento

```text
DO_NOT_MERGE_WITHOUT_EXPLICIT_LEANDRO_APPROVAL
DO_NOT_START_NF02
DO_NOT_CHANGE_PRODUCTION_CODE
DO_NOT_CHANGE_BACKEND
DO_NOT_MIGRATE_PONTO_TO_ATTENDANCE_EVENT
DO_NOT_IMPLEMENT_AI
DO_NOT_IMPLEMENT_OBSERVABILITY_BACKEND
DO_NOT_DEPLOY
DO_NOT_DECLARE_LEGAL_COMPLIANCE
DO_NOT_EDIT_DECISOES_CONGELADAS_MD
```

---

# 21. Ponte para um novo chat

Um novo chat deve começar lendo, nesta ordem:

```text
1. DECISOES_CONGELADAS.md
2. docs/nf-01/12_NF01_CANONICAL_DECISIONS_2026-08-11.md
3. docs/nf-01/13_NF01_REMAINING_WORK_ROADMAP.md
4. docs/nf-01/10_NF01_CLOSEOUT.md
5. docs/nf-01/06_COMPONENT_CATALOG.md
6. docs/nf-01/prototype/NEW_EMPLOYEE_V2_UX_SPEC.md
7. docs/nf-01/15_NF01_COMPONENT_REVIEW_BATCH_A1_A4_B1_2026-08-11.md
8. PR #32 e HEAD atual da branch
```

Depois deve continuar **pelo primeiro item não concluído deste roadmap**.

Estado atual após o gate humano do lote:

```text
NEXT_OFFICIAL_ITEM=B2_ICON_BUTTON_COMPONENT_REVIEW
VISUAL_IMPLEMENTATION=NOT_YET
```