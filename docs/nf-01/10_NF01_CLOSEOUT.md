# NF-01 — Closeout / Estado Atual

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**MCF:** 1.1 / Classe C  
**Base original da NF-01:** `main@2a388fdc40817dca8f7bd96232e723c0e520702b`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Estado:** `CANONICAL_DECISIONS_DOCUMENTED__VISUAL_RECONCILIATION_PENDING`

## 1. Situação

A NF-01 permanece aberta. O ciclo de UX/UI de 11/08/2026 aprofundou o onboarding, corrigiu o shell, congelou componentes estruturais e executou uma RC transversal que encontrou e fechou lacunas críticas, altas e médias em nível de especificação.

As decisões deixaram de depender do histórico do chat e foram oficializadas em:

```text
12_NF01_CANONICAL_DECISIONS_2026-08-11.md
```

Esse arquivo é a referência canônica deste ciclo, subordinada a `DECISOES_CONGELADAS.md`.

## 2. Estado dos entregáveis

```text
01_PRODUCT_DEFINITION.md................ COMPLETE
02_UI_INVENTORY.md...................... COMPLETE
03_INFORMATION_ARCHITECTURE.md.......... EXISTING_BASELINE
04_ROLES_PERMISSIONS_AND_STATES.md...... EXISTING_BASELINE
05_DESIGN_SYSTEM.md..................... CANONICALIZED_2026_08_11
06_COMPONENT_CATALOG.md................. CANONICALIZED_2026_08_11
07_WIREFRAMES.md........................ CANONICALIZED_2026_08_11
08_RESPONSIVE_ACCESSIBILITY.md.......... CANONICALIZED_2026_08_11
09_TEST_AND_ACCEPTANCE_STRATEGY.md...... CANONICALIZED_2026_08_11
10_NF01_CLOSEOUT.md..................... UPDATED
11_RC01_UI_UX_REFINEMENTS.md............ HISTORICAL_RC01
12_NF01_CANONICAL_DECISIONS_2026-08-11.. CANONICAL_CURRENT_CYCLE
```

## 3. Contratos congelados no ciclo atual

```text
NEW_EMPLOYEE_FUNCTIONAL_CONTRACT=FROZEN
DIMENSIONING_POLICY=FROZEN
COLLAPSIBLE_SIDEBAR=FROZEN
HORIZONTAL_STEPPER=FROZEN
CONTEXT_DRAWER=FROZEN
STICKY_FORM_ACTIONS=FROZEN
RESPONSIVE_FORM_GRID=FROZEN
FORM_SECTION_PROGRESSIVE_DISCLOSURE=FROZEN
FIELD_GROUP=FROZEN
ENTITY_PICKER=FROZEN
DATE_TIME_PERIOD_PICKER=FROZEN
ICON_SYSTEM_LUCIDE=FROZEN
MOTION_SYSTEM=FROZEN
SEMANTIC_DOM_ORDER=FROZEN
TOAST_POLICY=FROZEN
```

## 4. RC transversal

```text
RC_TRANSVERSAL=COMPLETE
CRITICAL_GAPS_CLOSED=6/6
HIGH_GAPS_CLOSED=9/9
MEDIUM_GAPS_CLOSED=6/6
CRITICAL_OPEN=0
HIGH_OPEN=0
MEDIUM_OPEN=0
```

A RC fechou, entre outros:

- Wizard State + Draft/Conflict;
- Dependency Invalidation;
- Conditional Data Lifecycle;
- Submit Outcome Reconciliation;
- Runtime Permission Revalidation;
- Back/Forward/Refresh;
- Session Expiration Recovery;
- Stepper Discoverability;
- App Context vs Form Company;
- Required/Optional Policy;
- Error Hierarchy;
- Step Focus Management;
- Mobile Keyboard Safe Actions;
- Date/Time/Period;
- Design Tokens;
- Icon System;
- Motion/Reduced Motion;
- DOM semantic order;
- Toast Policy;
- Global Component Catalog.

## 5. Invariantes

```text
PRODUCTION_CODE_CHANGED=NO
APP_CHANGED=NO
TEMPLATES_CHANGED=NO
STATIC_CHANGED=NO
MIGRATIONS_CHANGED=NO
BACKEND_CHANGED=NO
DECISOES_CONGELADAS_CHANGED=NO
NF02_STARTED=NO
PONTO_MIGRATION=NO
AI_IMPLEMENTED=NO
OBSERVABILITY_BACKEND_IMPLEMENTED=NO
DEPLOY=NO
PRODUCTION_HOMOLOGATION=BLOCKED
LEGAL_CONFORMITY_DECLARED=NO
PR_32_MERGED=NO
```

## 6. Artefatos visuais

Estado conceitual:

```text
Dashboard V3.................... conteudo preservado; shell deve ser reconciliado
Funcionarios Desktop V1......... aprovado anteriormente; shell deve ser reconciliado
Novo Funcionario V1............. historico/comparacao
Novo Funcionario V2............. contrato funcional preservado; layout deve ser reconciliado
```

Direções substituídas:

```text
sidebar sempre expandida................ SUPERSEDED
stepper vertical do onboarding.......... SUPERSEDED
painel contextual direito permanente.... SUPERSEDED
larguras rígidas em px como regra geral. SUPERSEDED
emoji como iconografia de produção....... SUPERSEDED
```

## 7. Próxima sequência obrigatória

```text
1. validar documentação canônica no repositório
2. reconciliar qualquer documento residual conflitante
3. consolidar wireframe do AppShell
4. reconciliar Dashboard
5. reconciliar Funcionários
6. reconciliar Novo Funcionário
7. validar coerência entre as três telas
8. validar responsividade/a11y no Design Lab
9. atualizar evidências e revisão independente
10. solicitar Gate humano final de LEANDRO
```

## 8. Gate

```text
HUMAN_GATE_REQUIRED=YES
FINAL_HUMAN_GATE=NOT_READY
PR_32_MERGE=BLOCKED_UNTIL_EXPLICIT_APPROVAL
NF02=NOT_STARTED
```

Não iniciar NF-02 por inferência.

Não fazer merge do PR #32 sem autorização humana explícita.

Não declarar conformidade jurídica/regulatória.
