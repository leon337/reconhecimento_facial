# NF-01 — Fase L — L1 — Auditoria canônica de gaps do Novo Funcionário V2

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-18  
**Autoridade humana:** LEANDRO

---

## Gate e estado

```text
L1_ONBOARDING_CANONICAL_GAP_AUDIT=APPROVED_BY_LEANDRO
L1_STATUS=COMPLETE
PHASE_L_ONBOARDING_RECONCILIATION=IN_PROGRESS
IMPLEMENTATION=DOCUMENTAL_AUDIT_ONLY
ONBOARDING_VISUAL_CHANGE_IN_L1=NO
ONBOARDING_HTML_CHANGED_IN_L1=NO
ONBOARDING_CSS_CHANGED_IN_L1=NO
ONBOARDING_JS_CHANGED_IN_L1=NO
PRODUCTION_CHANGE=NO
PHASE_M=NOT_STARTED
PHASE_N=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate autoriza somente a comparação Current × Canonical do Novo Funcionário V2 no Design Lab. Nenhuma mudança visual/funcional em `03.04-novo-funcionario-v2.html`, `new-employee-v2.css` ou `new-employee-v2.js` foi autorizada por L1.

---

## Fontes auditadas

```text
docs/nf-01/04_ROLES_PERMISSIONS_AND_STATES.md
docs/nf-01/06_COMPONENT_CATALOG.md
docs/nf-01/07_WIREFRAMES.md
docs/nf-01/08_RESPONSIVE_ACCESSIBILITY.md
docs/nf-01/09_TEST_AND_ACCEPTANCE_STRATEGY.md
docs/nf-01/12_NF01_CANONICAL_DECISIONS_2026-08-11.md
docs/nf-01/13_NF01_REMAINING_WORK_ROADMAP.md
docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
docs/nf-01/prototype/assets/new-employee-v2.css
docs/nf-01/prototype/assets/new-employee-v2.js
```

Blobs auditados:

```text
ONBOARDING_HTML_SHA=f524c048d9a7df15b80f626e51659aabe1715471
ONBOARDING_CSS_SHA=06fb9d6c7667305c4d993601a4fa8e9322aa637a
ONBOARDING_JS_SHA=cf73d0a34ece6e75b68d124a4e9f3c19f6b15a1e
```

---

## Resultado executivo

```text
L1_AUDIT_RESULT=GAPS_FOUND
CRITICAL_GAPS=0
HIGH_GAP_THEMES=9
MEDIUM_GAP_THEMES=7
LOW_DEFERRED_OBSERVATIONS=3

PRESERVE_ITEMS=13
RECONCILE_ITEMS=17
REMOVE_ITEMS=3
DEFER_ITEMS=7

L2_IMPLEMENTATION_SCOPE_REQUIRED=YES
PRODUCTION_READY=NO
```

O V2 atual já cobre grande parte do **conteúdo funcional** das oito etapas, mas sua **arquitetura de interação** ainda representa a direção anterior ao congelamento canônico de 11/08: stepper vertical permanente, painel lateral permanente, ações divididas entre o rail e a barra inferior, ausência de `ContextDrawer`, ausência de `NEEDS_REVIEW` e ausência de variantes reais de affordance por permissão.

A principal conclusão de L1 é:

```text
CONTEUDO_FUNCIONAL_BASE=STRONG
CANONICAL_INTERACTION_ARCHITECTURE=NOT_YET_ADOPTED
```

---

# 1. Matriz Current × Canonical

| Área | Estado atual | Contrato canônico | Classificação | Severidade | Decisão L1 |
|---|---|---|---|---|---|
| AppShell | compartilhado, `active=employees` | AppShell administrativo único | PRESERVE | — | manter |
| Breadcrumb/PageHeader | Gestão > Funcionários > Novo funcionário V2 | localização + título | PRESERVE | — | manter e simplificar rótulo V2 quando reconciliado |
| Isolamento | aviso explícito de Design Lab e sem backend | futuro não se passa por presente | PRESERVE | — | manter |
| Oito etapas | 0–7 na ordem canônica | oito domínios congelados | PRESERVE | — | manter conteúdo-base |
| Tipo de relação | CLT comum/intermitente/sem vínculo/outros | mesma taxonomia | PRESERVE | — | manter |
| Dados pessoais | identificação, civis, contato, dependentes, PcD | contrato funcional amplo | PRESERVE | — | manter e ajustar semântica de campos |
| Endereço | Brasil urbano, rural e exterior | país primeiro + variantes | PRESERVE | — | manter |
| Vínculo | empresa, unidade, setor, cargo, gestor, jornada, modalidades | cadastros mestres + dependências | PRESERVE/RECONCILE | HIGH | preservar campos; trocar seleção simples por contrato EntityPicker e dependências |
| Pagamento | banco, conta-salário, PIX, outra, terceiro | formas estruturadas + exceção revisável | PRESERVE | — | manter conteúdo-base |
| Acesso | padrão sem conta, perfis RBAC existentes | funcionário != conta | PRESERVE | — | manter |
| Biometria | agora/depois, aviso, câmera simulada, sem upload | câmera ao vivo + transparência + permissão | PRESERVE/RECONCILE | HIGH | manter conceito; tornar permission-aware e ampliar estados |
| Revisão | resumo por seção + Editar + pendências | revisão consolidada | PRESERVE | — | manter |
| Rascunho local | autosave, restaurar, salvar/sair, descartar | persistência e retomada | PRESERVE/RECONCILE | MEDIUM | manter demo; reconciliar estados/ações |
| Foco após etapa | heading recebe foco | step change move foco | PRESERVE | — | manter, respeitar reduced motion |
| Stepper | coluna vertical com texto permanente | HorizontalStepper icon-first | REMOVE/RECONCILE | HIGH | substituir completamente |
| Ver etapas | não existe | visão textual sob demanda | RECONCILE | HIGH | criar contrato visual/acessível |
| Painel de contexto | coluna direita fixa com 3 cards | ContextDrawer fechado por padrão | REMOVE/RECONCILE | HIGH | substituir por drawer sob demanda |
| Permissão simulada | card fixo “Administrador” | permissões refletidas nas affordances | REMOVE/RECONCILE | HIGH | remover hardcode; usar metadata/variante source-level |
| Sticky actions | Descartar em barra; Salvar/sair no rail; Voltar sempre renderizado | ações unificadas por etapa | RECONCILE | HIGH | unificar `Descartar | Salvar e sair | Voltar | Continuar/Concluir` |
| Primeira etapa | Voltar aparece desabilitado | Voltar ausente quando não aplicável | RECONCILE | MEDIUM | não renderizar na etapa 0 |
| Tablet/mobile save-exit | footer do rail some em `<=980px` | Salvar e sair sempre disponível no contrato | RECONCILE | HIGH | mover para StickyFormActions |
| Mobile discard | ações iniciais somem em `<=460px` | Descartar continua disponível/seguro | RECONCILE | HIGH | reorganizar, não ocultar |
| `biometrics:manage` | texto diz que é requerido, JS não modela permissão | CTA proibido ausente | RECONCILE | HIGH | adicionar variante de permissão; manager não recebe captura |
| Dependência estrutural | mudar relação remove conclusão só da etapa atual | downstream compatível preservado e incompatível vira NEEDS_REVIEW | RECONCILE | HIGH | implementar invalidação dirigida |
| Estados de etapa | FUTURE/CURRENT/completa; erro só via badge local | FUTURE/CURRENT/VALID/ERROR/NEEDS_REVIEW | RECONCILE | HIGH | materializar NEEDS_REVIEW e ERROR no stepper |
| Dados condicionais ocultos | `serialize()` guarda campos ocultos se não estiverem disabled | hidden retained não entra no payload ativo | RECONCILE | HIGH | separar retenção local de payload ativo |
| Estado do wizard | editing/saving/saved/save-error implícitos | máquina canônica completa | RECONCILE | HIGH | materializar estados críticos source-level |
| Conflito | inexistente | CONFLICT persistente e bloqueante | RECONCILE | HIGH | criar superfície de contrato, sem backend real |
| Offline | inexistente | OFFLINE persistente, não toast-only | RECONCILE | HIGH | criar superfície de contrato |
| Submit desconhecido | conclusão local sempre “sucesso demo” | OUTCOME_UNKNOWN distinto | RECONCILE | HIGH | criar contrato visual; submit real continua futuro |
| Mudança de permissão | inexistente | runtime revalidation futura; CTA some | RECONCILE | HIGH | modelar affordance demonstrativa; enforcement backend diferido |
| FieldGroup | labels/ajuda/erro visuais; `data-required` custom | semântica required + aria-describedby + estados | RECONCILE | HIGH | associar ajuda/erro e obrigatório semanticamente |
| ErrorSummary | inexistente | resumo de múltiplos erros por etapa | RECONCILE | HIGH | adicionar contrato source-level |
| EntityPicker | selects locais de empresa/unidade/setor/cargo/gestor/jornada | SearchableCombobox/EntityPicker por ID e dependência | RECONCILE | HIGH | materializar UX de picker; backend remoto diferido |
| FormSection | seções sempre abertas salvo condicionais | progressive disclosure para secundário | RECONCILE | MEDIUM | aplicar apenas onde conteúdo secundário justificar |
| CSS local | `px` extensivo, colunas `285px`/`270px` | rem/fr/minmax/clamp/container-first | RECONCILE | MEDIUM | normalizar camada local em L2 |
| Responsividade | breakpoints 1260/980/760/460 dominam estrutura | espaço real + container query quando apropriado | RECONCILE | MEDIUM | trocar dependências rígidas tocadas em L2 |
| Browser back/forward | wizard não integra history | histórico deve respeitar etapa | RECONCILE | MEDIUM | definir source contract; integração real futura |
| Navigation guard | inexistente | somente quando houver risco real de perda | RECONCILE | MEDIUM | demonstrar apenas se houver estado não persistido |
| Reduced motion JS | CSS reduz transições, `scrollTo(...smooth)` continua | movimento não essencial reduzido | RECONCILE | MEDIUM | respeitar media query no JS |
| Camera states | mock reduzido a pendente/processando/sucesso | aguardando/permissão/indisponível/captura/qualidade/processando/sucesso/falha | RECONCILE | MEDIUM | ampliar contratos demonstrativos |
| Backend draft/revision | localStorage somente | revisão/versionamento real | DEFER | — | implementação futura |
| Submit transacional/idempotente | não existe por isolamento | obrigatório em produção | DEFER | — | contrato permanece documentado |
| EntityPicker remoto | inexistente | debounce/async/escopo/ID | DEFER | — | apenas contrato visual em L2 |
| Câmera real/template | não existe | backend/biometria real | DEFER | — | não implementar em NF-01 |
| Runtime RBAC real | não existe | backend é autoridade | DEFER | — | não implementar em NF-01 |
| Validação browser/a11y completa | não executada | 360/768/1024/1440 + zoom/sr/a11y | DEFER | — | Fase N |
| Legal/LGPD especializado | não declarado | gate especializado separado | DEFER | — | manter limite |

---

# 2. Gaps HIGH que L2 deve resolver

## L1-H1 — Stepper estrutural é a direção anterior

Current:

```text
wizard-rail vertical
+ oito nomes permanentes
+ coluna dedicada
```

Canonical:

```text
HorizontalStepper icon-first
+ Etapa X de 8
+ Ver etapas sob demanda
```

O documento canônico determina explicitamente que o HorizontalStepper **substitui completamente** a coluna vertical de etapas.

## L1-H2 — Contexto ainda ocupa uma coluna permanente

Current:

```text
wizard-workspace = form + 270px side
wizard-side = resumo + regra + permissão
```

Canonical:

```text
formulario amplo
+ [Resumo] trigger
+ ContextDrawer fechado por padrão
```

A coluna lateral atual reduz permanentemente a área útil do formulário e conflita com o `CONTEXT_DRAWER=FROZEN`.

## L1-H3 — StickyFormActions está fragmentado

Current:

```text
rail footer: Salvar e sair
barra inferior: Descartar | Voltar | Continuar/Concluir
```

Além disso, o footer do rail desaparece abaixo de 980px e o grupo de `Descartar` desaparece abaixo de 460px.

Canonical:

```text
0–6: Descartar | Salvar e sair | Voltar | Continuar
7:   Descartar | Salvar e sair | Voltar | Concluir cadastro
```

Na etapa 0, `Voltar` não deve ser renderizado.

## L1-H4 — Biometria declara permissão, mas não possui variante real de affordance

A tela informa `Requer biometrics:manage`, porém `new-employee-v2.js` não lê papel/permissões. O caminho `Cadastrar agora` e a captura ficam disponíveis no mock sem um contrato de visibilidade equivalente ao RBAC real.

L2 deve demonstrar pelo menos:

```text
admin/super_admin + biometrics:manage => agora/depois
manager sem biometrics:manage        => configurar depois; sem CTA proibido
auditor/operator                     => não recebem ação proibida
```

Isto continua sendo UI demonstrativa; backend permanece autoridade real.

## L1-H5 — Dependências não produzem NEEDS_REVIEW

O JS atual, ao editar um campo, faz essencialmente:

```text
completedSteps.delete(currentStep)
```

Mas alterar relação, empresa ou unidade pode invalidar etapas posteriores. O contrato exige:

```text
mudança estrutural
→ calcular impacto
→ preservar compatível
→ inativar incompatível
→ marcar etapas afetadas NEEDS_REVIEW
```

Reset global indiscriminado também é proibido.

## L1-H6 — Campo oculto continua serializado

`serialize()` percorre controles e ignora somente campos `disabled`; campos dentro de condicionais ocultos podem continuar no draft serializado.

O contrato congela:

```text
VISIBLE_ACTIVE
HIDDEN_RETAINED
CLEARED
```

Dados `HIDDEN_RETAINED` podem existir no rascunho para restauração, mas não podem ser tratados como payload ativo da decisão atual.

## L1-H7 — Estados críticos do wizard não estão materializados

O mock possui `Salvando`, `Rascunho salvo` e `Falha ao salvar`, mas ainda não possui superfícies persistentes para:

```text
CONFLICT
OFFLINE
PERMISSION_ERROR / PERMISSION_REMOVED
OUTCOME_UNKNOWN
```

Esses estados não podem ser representados apenas por toast. L2 deve materializar o contrato visual sem fingir backend real.

## L1-H8 — FieldGroup/ErrorSummary incompletos semanticamente

Há labels, mensagens e foco no primeiro erro, o que deve ser preservado. Porém:

- obrigatório é majoritariamente indicado por `*` + `data-required`, não pela semântica HTML/ARIA congelada;
- ajuda e erro não estão sistematicamente associados por `aria-describedby`;
- múltiplos erros não produzem `ErrorSummary` da etapa.

L2 deve corrigir a estrutura local sem transformar a NF-01 em implementação de validação remota.

## L1-H9 — Cadastros mestres ainda são selects estáticos

Empresa, unidade, setor, cargo, gestor e jornada aparecem como `<select>` de fixtures. O contrato congelado define `SearchableCombobox / EntityPicker` com dependências, seleção por ID, estados loading/empty/error e proteção contra troca incompatível silenciosa.

L2 deve implementar a **experiência source-level** do picker no Design Lab; busca remota, RBAC real e persistência por ID continuam futuros.

---

# 3. Gaps MEDIUM

```text
L1-M1 CSS local usa px extensivamente e colunas fixas da arquitetura antiga
L1-M2 responsividade depende principalmente de viewport breakpoints e não do container real
L1-M3 seções secundárias não usam progressive disclosure de forma canônica
L1-M4 browser back/forward não acompanha estado da etapa
L1-M5 navigation guard não existe para eventual risco real de perda
L1-M6 scroll suave do JS não consulta prefers-reduced-motion
L1-M7 CameraPanel não demonstra todo o vocabulário de estados canônicos
```

---

# 4. Itens PRESERVE

```text
P1  AppShell compartilhado
P2  breadcrumb + page title
P3  aviso explícito de Design Lab
P4  oito etapas e ordem funcional
P5  quatro tipos de relação
P6  cobertura principal de dados pessoais
P7  endereço Brasil/rural/exterior
P8  vínculo e modalidades de relação
P9  pagamento estruturado e exceção de terceiro
P10 acesso ao sistema opt-in e perfis existentes
P11 biometria agora/depois + transparência + câmera-only
P12 revisão consolidada + editar + pendências
P13 autosave/restauração local, descarte confirmado e foco no heading/primeiro erro
```

---

# 5. Itens REMOVE na próxima implementação aprovada

```text
R1 wizard-rail vertical como navegação principal
R2 wizard-side permanente
R3 card fixo “Permissão simulada / Administrador”
```

As capacidades não desaparecem: etapas viram HorizontalStepper + `Ver etapas`; resumo/permissões migram para ContextDrawer e affordances permission-aware.

---

# 6. Itens DEFER

```text
D1 persistência real de draft/revision no backend
D2 submit transacional/idempotente real
D3 EntityPicker remoto/async real
D4 câmera/template biométrico real
D5 enforcement RBAC real no backend
D6 homologação visual/a11y/responsiva completa → Fase N
D7 conformidade legal/LGPD especializada
```

---

# 7. Escopo implementável proposto para L2

```text
L2_ONBOARDING_CANONICAL_RECONCILIATION

TARGETS=
  docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
  docs/nf-01/prototype/assets/new-employee-v2.css
  docs/nf-01/prototype/assets/new-employee-v2.js

GOALS=
  preserve eight-stage functional content
  replace vertical rail with HorizontalStepper
  add textual Ver etapas surface
  replace permanent right column with ContextDrawer
  unify StickyFormActions
  hide Back on first step
  keep Save and exit + Discard available across responsive states
  add source-level role/permission metadata
  make biometrics:manage affordance permission-aware
  add NEEDS_REVIEW downstream invalidation contract
  separate retained hidden draft data from active payload semantics
  materialize CONFLICT|OFFLINE|PERMISSION_ERROR|OUTCOME_UNKNOWN surfaces
  add ErrorSummary and FieldGroup aria-describedby/required semantics
  materialize local EntityPicker UX for master-data fields
  normalize touched local CSS toward rem/fr/minmax/clamp/container-query
  preserve reduced-motion and make JS scroll behavior motion-aware
  expand CameraPanel state contract without real camera access

DO_NOT=
  change app-shell.css/js
  rewrite components.css globally
  implement backend draft persistence
  implement real RBAC enforcement
  implement real camera/biometric storage
  implement production submit
  start Phase M
  start Phase N
  start NF02
  merge PR
```

---

# 8. Testes derivados para L2+

## Unitários futuros

```text
step 0 => Back absent
step 0–6 => Continue present; Complete absent
step 7 => Complete present; Continue absent
Save and exit remains available at mobile/tablet layouts
Discard remains available and requires confirmation
manager without biometrics:manage => biometric-now action absent
admin with biometrics:manage => biometric-now action present
relation change invalidates only affected downstream steps
company change marks dependent stages NEEDS_REVIEW
hidden retained field != active payload field
CONFLICT blocks completion and pauses autosave contract
OFFLINE != SAVE_ERROR
OUTCOME_UNKNOWN != ERROR
multiple field errors => ErrorSummary + focus first invalid
ContextDrawer Escape => closed + focus returned
HorizontalStepper future step => cannot jump past prerequisites
prefers-reduced-motion => no smooth programmatic scroll
```

## Integração futura

```text
Funcionários → Novo Funcionário preserves shared AppShell
start draft → advance/back → refresh → same draft and step
completed step → revisit → change structural dependency → downstream NEEDS_REVIEW
manager create flow → no biometric affordance
admin create flow → biometric now/defer choices
ContextDrawer open/close preserves form
Ver etapas → select allowed completed step → form preserved
conditional payment/access/relation hidden values do not become active payload
SAVE_ERROR / OFFLINE / CONFLICT remain persistent and recoverable
review → submit outcome unknown → reconciliation before success
```

Nenhum desses testes é declarado executado em L1.

---

# 9. Limites do L1

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
L1_COMPLETE != PHASE_L_COMPLETE
L1_COMPLETE != VISUAL_HOMOLOGATION
L1_COMPLETE != AUTOMATED_TEST_PASS
L1_COMPLETE != PRODUCTION_READY
```

---

# 10. Próxima fronteira

```text
NEXT_OFFICIAL_PHASE=L_ONBOARDING_RECONCILIATION
NEXT_OFFICIAL_ITEM=L2_DEFINITION_GATE
```

L2 deve executar somente a reconciliação comprovada por esta matriz. Nenhuma aprovação de L2 é inferida deste gate.
