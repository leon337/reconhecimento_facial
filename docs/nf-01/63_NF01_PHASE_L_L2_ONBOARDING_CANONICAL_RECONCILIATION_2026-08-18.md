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

## Recuperação do incidente de execução

A primeira tentativa de L2 foi interrompida antes da implementação real e deixou dois artefatos incorretos. A recuperação foi executada antes do aceite final:

```text
RECOVERY_INCIDENT_DETECTED=YES
ROADMAP_PLACEHOLDER_INCIDENT=REPAIRED
ROADMAP_RESTORED_TO_PRE_L2_BLOB=03202d8bd21ca4ccda0daaefd87ef4f02ed67c86
PREMATURE_L2_CHECKPOINT=CORRECTED_BEFORE_FINAL_ACCEPTANCE
HISTORY_REWRITE=NO
FORCE_PUSH=NO
```

O histórico foi preservado. O erro foi corrigido por commits normais e posteriormente a implementação real foi aplicada.

## Escopo efetivamente implementado

```text
docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
docs/nf-01/prototype/assets/new-employee-v2.css
docs/nf-01/prototype/assets/new-employee-v2.js
```

Blobs verificados após a implementação:

```text
03.04-novo-funcionario-v2.html = 470b03b915fc960dd996023dabd63692ad5f209d
new-employee-v2.css             = 7a1003aa2329ef7ddf18280c7a31494f2d3a4219
new-employee-v2.js              = 2590868979cacc49e03c348bd4138e4f9f463b19
```

O AppShell compartilhado e a sequência funcional das oito etapas foram preservados.

## Verificação Current × contrato L1

```text
L1-H1  vertical wizard rail -> HorizontalStepper + Ver etapas ................. PASS_SOURCE_LEVEL
L1-H2  permanent right context column -> ContextDrawer sob demanda ............ PASS_SOURCE_LEVEL
L1-H3  StickyFormActions fragmentadas -> barra única e responsiva .............. PASS_SOURCE_LEVEL
L1-H4  biometrics:manage sem variante -> affordance permission-aware ........... PASS_SOURCE_LEVEL
L1-H5  downstream invalidation ausente -> NEEDS_REVIEW ......................... PASS_SOURCE_LEVEL
L1-H6  hidden retained conflado -> draftData + activePayloadPreview ............ PASS_SOURCE_LEVEL
L1-H7  estados críticos ausentes -> superfícies persistentes ................... PASS_SOURCE_LEVEL
L1-H8  FieldGroup/ErrorSummary incompletos -> semântica source-level ........... PASS_SOURCE_LEVEL
L1-H9  master-data selects -> EntityPicker local demonstrativo ................. PASS_SOURCE_LEVEL
```

## H1 — HorizontalStepper

- existem oito etapas canônicas;
- a navegação principal é horizontal e icon-first;
- `aria-current="step"` identifica a etapa atual;
- `CURRENT`, `COMPLETED`, `FUTURE`, `NEEDS_REVIEW` e `ERROR` possuem representação source-level;
- em espaço estreito a barra vira progresso compacto + `Etapa X de 8` + `Ver etapas` textual.

O antigo rail vertical não pertence mais ao HTML ativo.

## H2 — ContextDrawer

O antigo painel contextual permanente foi removido. `Resumo` abre um `ContextDrawer` sob demanda com:

- resumo do rascunho;
- permissões demonstrativas;
- estados críticos demonstrativos;
- contagem do payload ativo;
- regra explícita de que rascunho não é funcionário ativo.

Ele não reduz permanentemente a largura do formulário.

## H3 — StickyFormActions

O contrato de ações agora é único:

```text
Etapas 0–6: Descartar | Salvar e sair | Voltar quando aplicável | Continuar
Etapa 7:   Descartar | Salvar e sair | Voltar | Concluir cadastro
```

`Concluir cadastro` só aparece na revisão. Em espaço estreito, viewport baixo ou coarse pointer, a barra pode voltar ao fluxo para não cobrir o conteúdo/teclado.

## H4 — RBAC demonstrativo

```text
users:create       -> acesso demonstrativo à superfície de criação
biometrics:manage  -> affordance “Cadastrar agora”
```

Perfis locais demonstrativos:

```text
admin    = users:create + biometrics:manage
manager  = users:create
auditor  = sem criação
```

Sem `biometrics:manage`, a opção `Cadastrar agora` não é renderizada como affordance disponível e o fluxo permanece em `Configurar depois`. Sem `users:create`, a superfície entra em `PERMISSION_ERROR` demonstrativo. O backend continua sendo a autoridade real.

## H5 — Dependency Invalidation / NEEDS_REVIEW

Mudanças estruturais em `relation_type`, `company` e `unit` podem marcar etapas posteriores já alcançadas como `NEEDS_REVIEW`. Dados compatíveis são preservados e a revisão final bloqueia conclusão enquanto existir etapa pendente de revalidação.

## H6 — Conditional Data Lifecycle

O rascunho local separa:

```text
draftData             -> valores locais preservados
activePayloadPreview  -> somente dados atualmente ativos
```

Blocos condicionais recebem:

```text
VISIBLE_ACTIVE
HIDDEN_RETAINED
```

A verificação corrigiu um erro intermediário importante: a seleção do payload ativo não depende da visibilidade da etapa atual do wizard. Apenas dados `HIDDEN_RETAINED`, campos desabilitados ou affordances sem permissão ficam fora de `activePayloadPreview`.

## H7 — estados críticos persistentes

O Design Lab materializa superfícies persistentes para:

```text
PERMISSION_ERROR
OFFLINE
CONFLICT
SAVE_ERROR
SUBMIT_OUTCOME_UNKNOWN
```

`CONFLICT` pausa o autosave demonstrativo. `OFFLINE`, `CONFLICT`, `PERMISSION_ERROR` e `SUBMIT_OUTCOME_UNKNOWN` bloqueiam avanço/conclusão. Toast permanece feedback secundário e não substitui estados críticos.

## H8 — FieldGroup + ErrorSummary

- campos marcados como obrigatórios recebem `aria-required` em source-level;
- ajuda e erro recebem IDs e são ligados via `aria-describedby` quando presentes;
- `aria-invalid` é aplicado em erro;
- há `ErrorSummary` persistente com links de retorno aos campos;
- mudança de etapa foca o heading e anuncia `Etapa X de 8`;
- reduced motion é respeitado no scroll e nas transições locais.

## H9 — EntityPicker local

Empresa, Unidade, Setor, Cargo/Função, Gestor e Jornada usam seleção local demonstrativa por ID, progressivamente enriquecida com:

```text
role=combobox
role=listbox
role=option
aria-expanded
ArrowUp / ArrowDown / Enter / Escape
busca textual local
EMPTY local distinto de falha remota
```

Nenhuma API remota, criação de cadastro mestre ou persistência real é afirmada.

## Responsividade e dimensionamento local

A camada local de L2 usa predominantemente:

```text
rem
fr
minmax()
clamp()
cqi / container query
dvh
safe-area
```

A busca source-level do CSS local não encontrou uso de `px`. A política de responsividade reorganiza o formulário, stepper e ações conforme espaço disponível em vez de apenas reduzir tamanhos.

## CameraPanel demonstrativo

A captura continua sem câmera real, upload ou armazenamento. A máquina visual demonstra:

```text
AGUARDANDO_CAMERA
CAPTURANDO
VALIDANDO_QUALIDADE
PROCESSANDO
SUCESSO
```

Falhas físicas, permissões reais de câmera e armazenamento biométrico permanecem no contrato futuro de testes/implementação.

## Evidência de escopo

A comparação entre o estado pré-L2 `4e66826ba43f9fc2cc897f3a1215bea41613098e` e a implementação verificada mostrou somente:

```text
docs/nf-01/63_NF01_PHASE_L_L2_ONBOARDING_CANONICAL_RECONCILIATION_2026-08-18.md
docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
docs/nf-01/prototype/assets/new-employee-v2.css
docs/nf-01/prototype/assets/new-employee-v2.js
```

O roadmap não aparece no diff líquido porque foi restaurado byte-a-byte antes da implementação.

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

## Testes futuros derivados

Unitários futuros:

- transições `CURRENT/COMPLETED/NEEDS_REVIEW`;
- dependency invalidation;
- `draftData` versus `activePayloadPreview`;
- runtime permission variants;
- ErrorSummary/field semantics;
- EntityPicker local/assíncrono no contrato definitivo;
- submit idempotente real quando existir backend.

Integração futura:

- duas abas/revision conflict;
- sessão expirada + retomada;
- mudança de permissão durante wizard;
- mudança de relação/empresa/unidade e revisão downstream;
- teclado mobile + StickyFormActions;
- câmera real e biometria;
- backend draft/revision e submit transacional.

Esses testes foram derivados, não executados em L2.

## Próximo gate

```text
NEXT_OFFICIAL_PHASE=L_ONBOARDING_RECONCILIATION
NEXT_OFFICIAL_ITEM=L3_ONBOARDING_POST_RECONCILIATION_ACCEPTANCE_GATE
L3_APPROVAL_INFERRED=NO
```

L3 deverá reauditar o resultado de L2 antes de qualquer fechamento da Fase L.
