# NF-01 — Fase L — L3 — Aceite pós-reconciliação do Novo Funcionário V2

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-18  
**Autoridade humana:** LEANDRO

## Gate e estado

```text
L3_ONBOARDING_POST_RECONCILIATION_ACCEPTANCE=APPROVED_BY_LEANDRO
L3_STATUS=COMPLETE
L3_ACCEPTANCE=PASS_SOURCE_LEVEL_WITH_TWO_HARDENING_FIXES_AND_ONE_CONTINUITY_FIX
PHASE_L_ONBOARDING_RECONCILIATION=COMPLETE
PHASE_L_CLOSEOUT_BASIS=SOURCE_LEVEL

L3_BLOCKING_GAPS_FOUND=2
L3_BLOCKING_GAPS_FIXED=2
L3_CONTINUITY_DRIFT_FOUND=1
L3_CONTINUITY_DRIFT_FIXED=1
UNRESOLVED_ONBOARDING_BLOCKING_GAPS=0
L4_REQUIRED=NO

ONBOARDING_HTML_CHANGED_IN_L3=NO
ONBOARDING_CSS_CHANGED_IN_L3=YES_HARDENING_ONLY
ONBOARDING_JS_CHANGED_IN_L3=YES_HARDENING_ONLY
PROTOTYPE_INDEX_CHANGED_IN_L3=YES_CONTINUITY_METADATA_ONLY
APPSHELL_CHANGED=NO
PRODUCTION_CHANGE=NO
PHASE_M=NOT_STARTED
PHASE_N=NOT_STARTED
NF02=NOT_STARTED
PR_MERGE=NOT_AUTHORIZED
```

A aprovação deste gate foi consumida somente para L3. Nenhuma autorização de Fase M, Fase N, NF-02, produção, deploy ou merge é inferida.

## Objetivo

Reauditar o resultado de L2 contra as decisões canônicas e a matriz de gaps de L1, corrigindo somente defeitos objetivos encontrados durante o aceite. L3 não autoriza novo redesign.

Fontes principais:

```text
docs/nf-01/12_NF01_CANONICAL_DECISIONS_2026-08-11.md
docs/nf-01/62_NF01_PHASE_L_L1_ONBOARDING_CANONICAL_GAP_AUDIT_2026-08-18.md
docs/nf-01/63_NF01_PHASE_L_L2_ONBOARDING_CANONICAL_RECONCILIATION_2026-08-18.md
docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html
docs/nf-01/prototype/assets/new-employee-v2.css
docs/nf-01/prototype/assets/new-employee-v2.js
docs/nf-01/prototype/index.html
```

## Reauditoria dos nove temas HIGH de L1

```text
L1-H1  HorizontalStepper + Ver etapas ........................ PASS_AFTER_HARDENING
L1-H2  ContextDrawer sob demanda .............................. PASS
L1-H3  StickyFormActions unificadas ........................... PASS
L1-H4  biometrics:manage permission-aware ..................... PASS
L1-H5  dependency invalidation + NEEDS_REVIEW ................. PASS
L1-H6  draftData separado de activePayloadPreview ............. PASS
L1-H7  estados críticos persistentes .......................... PASS
L1-H8  FieldGroup/ErrorSummary source-level ................... PASS_AFTER_HARDENING
L1-H9  EntityPicker local demonstrativo ....................... PASS_AFTER_HARDENING
```

## L3-F1 — estado ERROR do stepper era inalcançável

L2 possuía estilo visual para `data-step-status="ERROR"`, mas o controlador retornava apenas `CURRENT`, `NEEDS_REVIEW`, `COMPLETED` e `FUTURE`. Uma falha real de validação alterava apenas o badge local da etapa e nunca materializava `ERROR` no HorizontalStepper.

Correção de hardening:

```text
errorSteps = Set persistente no rascunho local
validation failure -> errorSteps.add(step)
stepStatus priority -> ERROR > CURRENT > NEEDS_REVIEW > COMPLETED > FUTURE
editing/valid success -> clear ERROR
step list + aria-label -> representação textual de erro
```

O CSS local recebeu somente os estilos necessários para o badge e a lista textual de etapas em `ERROR`.

## L3-F2 — semântica do EntityPicker estava dividida entre select oculto e combobox visível

O enriquecimento progressivo de L2 criava um `input role="combobox"`, porém o `label`, `aria-required`, `aria-describedby`, foco de ErrorSummary e `aria-invalid` continuavam ligados primariamente ao `<select>` visualmente oculto. Isso deixava a affordance visível com semântica incompleta.

Correção de hardening:

```text
visible combobox gets stable id
label for -> visible combobox
aria-required -> mirrored to combobox
aria-describedby -> mirrored to combobox
aria-invalid -> mirrored to combobox
ErrorSummary -> focuses visible combobox
source select -> tabindex=-1 + aria-hidden=true
source select remains data/value authority for the local fixture
```

Nenhuma integração remota ou cadastro mestre real foi introduzido.

## L3-C1 — drift de continuidade no índice do Design Lab

O tile de `03.04-novo-funcionario-v2.html` ainda descrevia a tela como `I6`, enquanto Dashboard e Funcionários já estavam indexados pelos seus respectivos gates de fechamento. L3 corrige somente essa metainformação para refletir a Fase L reconciliada.

## Evidência de CI disponível

Após os hardenings, o workflow padrão de CI executou o job `tests` com sucesso, incluindo `Verificar sintaxe` e `Executar testes`.

Isso **não** equivale aos testes específicos de aceitação de Design Lab, que continuam diferidos:

```text
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

## Limites do aceite

```text
L3_PASS_SOURCE_LEVEL != FULL_VISUAL_ACCEPTANCE
L3_PASS_SOURCE_LEVEL != FULL_ACCESSIBILITY_ACCEPTANCE
L3_PASS_SOURCE_LEVEL != PRODUCTION_READY

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

O estado de captura `FALHA`, history/back-forward real, foco modal completo e integrações remotas permanecem fora do fechamento source-level e serão cobertos pelos gates de coerência/validação aplicáveis.

## Resultado da Fase L

```text
L1=COMPLETE_AUDIT
L2=COMPLETE_RECONCILIATION
L3=COMPLETE_POST_RECONCILIATION_ACCEPTANCE
PHASE_L_RESULT=COMPLETE_SOURCE_LEVEL
UNRESOLVED_ONBOARDING_BLOCKING_GAPS=0
L4_REQUIRED=NO
```

A Fase L encerra a reconciliação source-level do Novo Funcionário V2. Isso não encerra a NF-01.

## Próximo gate

```text
NEXT_OFFICIAL_PHASE=M_CROSS_SCREEN_COHERENCE
NEXT_OFFICIAL_ITEM=M1_CROSS_SCREEN_COHERENCE_AUDIT_GATE
M1_APPROVAL_INFERRED=NO
```

A Fase M permanece não iniciada até novo HUMAN_GATE de LEANDRO.

## Invariantes

```text
app/**=UNCHANGED
templates/**=UNCHANGED
static/**=UNCHANGED
migrations/**=UNCHANGED
DECISOES_CONGELADAS.md=UNCHANGED
backend/routes=UNCHANGED
NF02=NOT_STARTED
Ponto_to_AttendanceEvent=NOT_EXECUTED
AI=NOT_IMPLEMENTED
OBSERVABILITY_BACKEND=NOT_IMPLEMENTED
DEPLOY=NO
PRODUCTION_HOMOLOGATION=NO
LEGAL_CONFORMITY_DECLARED=NO
FINAL_HUMAN_GATE=NOT_READY
PR_MERGE=BLOCKED_UNTIL_EXPLICIT_APPROVAL
```
