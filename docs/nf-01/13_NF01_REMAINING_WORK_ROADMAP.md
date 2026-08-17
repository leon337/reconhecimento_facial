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
COMPONENT_CATALOG_BASELINE=FROZEN
COMPONENT_INDIVIDUAL_REVIEW=IN_PROGRESS
PHASE_A_COMPONENT_REVIEW=COMPLETE
PHASE_B_COMPONENT_REVIEW=COMPLETE
```

### RC transversal

```text
CRITICAL_GAPS_CLOSED=6/6
HIGH_GAPS_CLOSED=9/9
MEDIUM_GAPS_CLOSED=6/6
```

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
[x] IconButton
[x] Tooltip
[x] Tabs
[x] StatusBadge
[x] MetricCard
```

---

# 3. Regra para revisão individual

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
15. RC rápida
16. aprovação humana explícita
17. marcar como FROZEN_INDIVIDUALLY
```

---

# 4. Fase A — Estrutura

```text
[x] A1 AppShell
[x] A2 TopHeader
[x] A3 Breadcrumb
[x] A4 PageHeader
PHASE_A_COMPONENT_REVIEW=COMPLETE
```

---

# 5. Fase B — Ações, navegação local e ajuda

```text
[x] B1 Button
[x] B2 IconButton
[x] B3 Tooltip
[x] B4 Tabs
PHASE_B_COMPONENT_REVIEW=COMPLETE
```

---

# 6. Fase C — Status, métricas e recência

```text
[x] C1 StatusBadge
[x] C2 MetricCard
[ ] C3 HealthCard
[ ] C4 LastUpdated
```

Guardrails:

```text
BRAND_GREEN != HEALTHY
TELEMETRY_UNAVAILABLE != SUCCESS
NO_SOURCE => NO_INVENTED_STATUS
NO_DATA != ZERO
NO_SOURCE => NO_METRIC
```

**Próxima ação oficial:** `C3 — revisar HealthCard como componente`, sem aplicar visualmente às telas.

---

# 7. Fase D — Busca, filtros e dados tabulares

```text
[ ] D1 Search
[ ] D2 FilterBar
[ ] D3 DataTable
[ ] D4 Pagination
```

---

# 8. Fase E — Estados de sistema e feedback

```text
[ ] E1 EmptyState
[ ] E2 ErrorState
[ ] E3 Skeleton
[ ] E4 DegradationBanner
[~] E5 Toast — revisão de integração/coerência
```

---

# 9. Fase F — Overlays, confirmação e histórico

```text
[ ] F1 DetailDrawer
[ ] F2 ConfirmationModal
[ ] F3 EventTimeline
```

---

# 10. Fase G — Câmera e resultado de ponto

```text
[ ] G1 CameraPanel
[ ] G2 PunchResult
```

---

# 11. Fase H — RC de completude do catálogo

```text
[ ] H1 comparar 06_COMPONENT_CATALOG.md com contratos individuais
[ ] H2 verificar componente sem revisão profunda
[ ] H3 verificar duplicações conceituais
[ ] H4 verificar inconsistências de estados
[ ] H5 verificar consistência de nomes
[ ] H6 verificar RBAC
[ ] H7 verificar acessibilidade transversal
[ ] H8 verificar responsividade/container behavior
[ ] H9 verificar testes futuros previstos
[ ] H10 corrigir documentação residual conflitante
```

---

# 12. Fase I — Design Lab / AppShell

```text
[ ] I1 materializar AppShell canônico
[ ] I2 CollapsibleSidebar expandida/compacta/overlay
[ ] I3 TopHeader
[ ] I4 Breadcrumb + PageHeader
[ ] I5 validar área útil
[ ] I6 validar navegação/estado ativo
[ ] I7 validar 360/768/1024/1440+
[ ] I8 zoom 200%
[ ] I9 teclado/foco
```

---

# 13. Fase J — Dashboard

```text
[ ] J1 AppShell
[ ] J2 operação protagonista
[ ] J3 sem falso verde
[ ] J4 cards/métricas/atividade/alertas
[ ] J5 densidade/área útil
[ ] J6 responsividade
[ ] J7 acessibilidade
[ ] J8 RC visual
```

---

# 14. Fase K — Funcionários

```text
[ ] K1 AppShell
[ ] K2 título + Novo funcionário
[ ] K3 métricas
[ ] K4 Search + FilterBar
[ ] K5 DataTable / fallback mobile
[ ] K6 biometria e permissões
[ ] K7 responsividade
[ ] K8 acessibilidade
[ ] K9 RC visual
```

---

# 15. Fase L — Novo Funcionário V2

```text
[ ] L1 remover stepper vertical residual
[ ] L2 HorizontalStepper icon-first
[ ] L3 “Ver etapas” sob demanda
[ ] L4 ContextDrawer
[ ] L5 ResponsiveFormGrid
[ ] L6 FormSection / Progressive Disclosure
[ ] L7 FieldGroup
[ ] L8 EntityPicker + Date/Time/Period
[ ] L9 StickyFormActions
[ ] L10 Wizard State/autosave/conflito/NEEDS_REVIEW
[ ] L11 Error Hierarchy
[ ] L12 permissões biometria
[ ] L13 revisão/conclusão
[ ] L14 360/768/1024/1440+
[ ] L15 zoom 200%
[ ] L16 teclado/foco/a11y
[ ] L17 RC visual
```

---

# 16. Fase M — Coerência entre telas

```text
[ ] M1 shell comum
[ ] M2 hierarquia visual comum
[ ] M3 linguagem de estados comum
[ ] M4 sidebar consistente
[ ] M5 header consistente
[ ] M6 spacing/tokens
[ ] M7 sem componentes ad hoc duplicados
[ ] M8 protótipos reconciliados
```

---

# 17. Fase N — Validação do Design Lab

```text
RESPONSIVIDADE: 360 / 768 / 1024 / 1440+ / intermediários / teclado mobile
ACESSIBILIDADE: teclado / foco / zoom 200% / reduced motion / ARIA / screen reader / contraste
TESTES FUTUROS: UNITÁRIOS / INTEGRAÇÃO / REGRESSÃO / RESPONSIVO / A11Y / SEGURANÇA
```

---

# 18. Fase O — Evidências, auditoria e fechamento

```text
[ ] O1 evidências visuais
[ ] O2 wireframes
[ ] O3 responsive/accessibility
[ ] O4 test/acceptance strategy
[ ] O5 revisão independente
[ ] O6 closeout
[ ] O7 PR #32
[ ] O8 CI/evidências
[ ] O9 invariantes de produção
[ ] O10 Gate humano final de LEANDRO
```

---

# 19. Definição de pronto

A NF-01 só fecha após catálogo, Design Lab, três telas reconciliadas, coerência, responsividade/a11y, contrato de testes, revisão independente, PR atualizado, ausência de mudança de produção fora do escopo e Gate explícito de LEANDRO.

---

# 20. Guardrails permanentes

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

# 21. Ponte para novo chat

Ler decisões canônicas, este roadmap, closeout, catálogo, especificação Novo Funcionário V2, checkpoints individuais recentes e PR #32/HEAD atual; depois continuar pelo primeiro item não concluído.

```text
NEXT_OFFICIAL_ITEM=C3_HEALTH_CARD_COMPONENT_REVIEW
VISUAL_IMPLEMENTATION=NOT_YET
```
