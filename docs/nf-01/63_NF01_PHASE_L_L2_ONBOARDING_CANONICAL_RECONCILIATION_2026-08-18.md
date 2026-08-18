# NF-01 — Fase L — L2 — Reconciliação canônica do Novo Funcionário V2

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-18  
**Autoridade humana:** LEANDRO

## Gate e estado

```text
L2_ONBOARDING_CANONICAL_RECONCILIATION=APPROVED_BY_LEANDRO
L2_STATUS=COMPLETE
L2_ACCEPTANCE=PASS_SOURCE_LEVEL
L1_HIGH_GAPS_RECONCILED_SOURCE_LEVEL=9/9
PHASE_L_ONBOARDING_RECONCILIATION=IN_PROGRESS

IMPLEMENTATION_SCOPE=DESIGN_LAB_ONLY
ONBOARDING_HTML_CHANGED_IN_L2=YES
ONBOARDING_CSS_CHANGED_IN_L2=YES
ONBOARDING_JS_CHANGED_IN_L2=YES
SHARED_COMPONENTS_CHANGED=NO
APPSHELL_CHANGED=NO
PRODUCTION_CHANGE=NO
PHASE_M=NOT_STARTED
PHASE_N=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate foi consumida somente para L2. Nenhuma autorização de L3, Fase M, Fase N, NF-02, produção, deploy ou merge é inferida.

## Escopo implementado

Somente:

```text
docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
docs/nf-01/prototype/assets/new-employee-v2.css
docs/nf-01/prototype/assets/new-employee-v2.js
```

O AppShell compartilhado e o conteúdo funcional das oito etapas foram preservados.

## Reconciliação dos nove temas HIGH de L1

```text
L1-H1  vertical wizard rail -> HorizontalStepper + lista textual mobile ........ PASS_SOURCE_LEVEL
L1-H2  permanent right context column -> ContextDrawer sob demanda .............. PASS_SOURCE_LEVEL
L1-H3  StickyFormActions fragmentadas -> barra unificada ........................ PASS_SOURCE_LEVEL
L1-H4  biometrics:manage sem variante -> affordance permission-aware ............. PASS_SOURCE_LEVEL
L1-H5  downstream invalidation ausente -> NEEDS_REVIEW ........................... PASS_SOURCE_LEVEL
L1-H6  hidden retained conflado com payload -> draftData + activePayloadPreview .. PASS_SOURCE_LEVEL
L1-H7  critical states ausentes -> superfícies persistentes ...................... PASS_SOURCE_LEVEL
L1-H8  FieldGroup/ErrorSummary incompletos -> semântica source-level ............. PASS_SOURCE_LEVEL
L1-H9  master-data selects -> EntityPicker local demonstrativo ................... PASS_SOURCE_LEVEL
```

### H1 — HorizontalStepper

- oito etapas permanecem canônicas;
- desktop usa stepper horizontal icon-first;
- `aria-current="step"` identifica a etapa atual;
- `COMPLETED`, `CURRENT`, `FUTURE` e `NEEDS_REVIEW` possuem estados distintos;
- mobile usa `Etapa X de 8`, barra simplificada e `Ver etapas` textual.

### H2 — ContextDrawer

O antigo painel contextual permanente foi removido da arquitetura principal. O contexto agora fica fechado por padrão e abre sob demanda, sem reduzir permanentemente a largura do formulário. O drawer expõe resumo, pendências, permissões e atalhos para etapas já alcançadas.

### H3 — StickyFormActions

O contrato visual agora permanece unificado:

```text
Etapas 0–6: Descartar | Salvar e sair | Voltar quando aplicável | Continuar
Etapa 7:   Descartar | Salvar e sair | Voltar | Concluir cadastro
```

`Voltar` não é renderizado na primeira etapa e `Concluir cadastro` só aparece na revisão.

### H4 — RBAC demonstrativo

```text
users:create       -> acesso à superfície de criação
biometrics:manage  -> opção/captura biométrica agora
```

A ausência de `biometrics:manage` remove a affordance de captura e mantém `Configurar depois`. O Design Lab apenas demonstra o contrato visual; o backend continua autoridade real.

### H5 — NEEDS_REVIEW

Mudanças estruturais podem marcar etapas posteriores como `NEEDS_REVIEW`. O estado é preservado no rascunho e aparece no stepper, lista textual e revisão.

### H6 — ciclo de dados condicionais

Blocos condicionais usam:

```text
VISIBLE_ACTIVE
HIDDEN_RETAINED
```

O rascunho local preserva valores seguros em `draftData`, enquanto `activePayloadPreview` contém apenas campos atualmente ativos. Isso demonstra o contrato sem afirmar payload/backend real.

### H7 — estados críticos persistentes

O Design Lab materializa superfícies persistentes para:

```text
PERMISSION_ERROR
OFFLINE
CONFLICT
SUBMIT_OUTCOME_UNKNOWN
SAVE_ERROR
```

Toast continua apenas suplementar. `CONFLICT` pausa autosave demonstrativo; `OFFLINE`/`CONFLICT`/`OUTCOME_UNKNOWN` bloqueiam avanço/conclusão demonstrativa.

### H8 — FieldGroup + ErrorSummary

- campos obrigatórios recebem `aria-required` em source-level;
- ajuda/erro recebem IDs e são associados por `aria-describedby` quando disponíveis;
- erro de etapa possui resumo persistente;
- o resumo oferece retorno de foco ao campo relacionado;
- estados de erro não dependem somente de cor.

### H9 — EntityPicker local

Empresa, Unidade, Setor, Cargo/Função, Gestor e Jornada usam EntityPicker demonstrativo local com:

- seleção por ID oculto separado do rótulo;
- busca textual local;
- `role=listbox`/`role=option`;
- `aria-expanded`;
- ArrowUp/ArrowDown/Enter/Escape;
- `EMPTY` distinto de erro;
- nenhuma criação improvisada de cadastro mestre.

Não existe busca remota/API em L2.

## Responsividade e dimensionamento local

A camada local de L2 usa predominantemente:

```text
rem
fr
minmax()
clamp()
container query
safe-area
```

`px` fica limitado a exceções técnicas como bordas e utilitário `sr-only`. O stepper colapsa para progresso/lista textual em espaço estreito, os grids passam para uma coluna e StickyFormActions pode voltar ao fluxo em viewport baixo/coarse pointer. `prefers-reduced-motion` também remove movimento não essencial.

## CameraPanel demonstrativo

A captura continua sem câmera real, upload ou armazenamento. A máquina visual demonstra:

```text
AGUARDANDO_CAMERA
CAPTURANDO
VALIDANDO_QUALIDADE
PROCESSANDO
SUCESSO
```

Estados de falha/indisponibilidade continuam no contrato de testes futuro e não são evidência de integração real.

## Limites do aceite

```text
BACKEND_DRAFT_REVISION=NOT_IMPLEMENTED
REAL_TRANSACTIONAL_IDEMPOTENT_SUBMIT=NOT_IMPLEMENTED
REMOTE_ENTITY_PICKER=NOT_IMPLEMENTED
REAL_CAMERA_OR_BIOMETRIC_STORAGE=NOT_IMPLEMENTED
RUNTIME_BACKEND_RBAC=NOT_IMPLEMENTED
LEGAL_LGPD_SPECIALIST_VALIDATION=NOT_EXECUTED

BROWSER_VISUAL_MATRIX_360_768_1024_1440=NO
INTERMEDIATE_WIDTH_VISUAL_TEST=NO
ZOOM_200_MANUAL_TEST=NO
SCREEN_READER_MANUAL_TEST=NO
AUTOMATED_A11Y_SCAN=NO
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

Logo:

```text
L2_PASS_SOURCE_LEVEL != FULL_VISUAL_ACCEPTANCE
L2_PASS_SOURCE_LEVEL != AUTOMATED_TEST_PASS
L2_PASS_SOURCE_LEVEL != PRODUCTION_READY
```

## Próximo gate

```text
NEXT_OFFICIAL_PHASE=L_ONBOARDING_RECONCILIATION
NEXT_OFFICIAL_ITEM=L3_ONBOARDING_POST_RECONCILIATION_ACCEPTANCE_GATE
L3_APPROVAL_INFERRED=NO
```

L3 deverá reauditar L2 antes de qualquer fechamento da Fase L.
