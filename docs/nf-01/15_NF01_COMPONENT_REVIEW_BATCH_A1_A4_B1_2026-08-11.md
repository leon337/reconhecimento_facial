# NF-01 — Revisão individual em lote — A1–A4 + B1

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-11  
**Autoridade humana:** LEANDRO  
**Modo:** validação conceitual / documentação  

---

## 0. Gate humano e escopo

Leandro autorizou explicitamente que os cinco primeiros itens pendentes fossem revisados em uma única etapa e, após a apresentação dos contratos, aprovou o lote.

```text
BATCH_REVIEW_EXCEPTION_APPROVED_BY_LEANDRO=YES
APPROVAL_SCOPE=A1+A2+A3+A4+B1
PRODUCTION_IMPLEMENTATION=NO
DESIGN_LAB_VISUAL_VALIDATION=NO
AUTOMATED_TESTS_EXECUTED=NO
NF02_STARTED=NO
MERGE_AUTHORIZED=NO
```

A aprovação desta revisão congela individualmente os contratos conceituais dos cinco componentes. Não autoriza aplicação visual às telas, código de produção, NF-02 ou merge.

---

# 1. A1 — AppShell

```text
APPSHELL_COMPONENT=FROZEN_INDIVIDUALLY
```

## Propósito

Estrutura administrativa única e compartilhada para as superfícies de administração/suporte. `/punch` permanece fora do shell administrativo.

## Anatomia

```text
AppShell
├─ SkipLink
├─ CollapsibleSidebar
├─ TopHeader
└─ MainWorkspace
   ├─ GlobalFeedbackRegion
   ├─ Breadcrumb
   ├─ PageHeader
   └─ main único
      └─ conteúdo da página
```

## Variantes permitidas

```text
DESKTOP_EXPANDED
DESKTOP_COMPACT
TABLET_COMPACT
OVERLAY_NAVIGATION
MOBILE_OVERLAY
```

Não existe `AppShellPunch`.

## Estados aplicáveis

```text
READY
LOADING_CONTEXT
DEGRADED
OFFLINE
NO_PERMISSION
```

Ausência de telemetria/informação não pode ser convertida em estado saudável.

## Comportamento, RBAC e responsividade

- sidebar expandida/compacta/overlay conforme contrato já congelado;
- largura liberada pela sidebar retorna imediatamente ao conteúdo;
- menu e ações respeitam RBAC real;
- usuário com apenas capacidade operacional de ponto não recebe shell administrativo por consequência;
- 360/768/1024/1440 permanecem alvos de validação, com reorganização conforme conteúdo;
- um único `main` e landmarks semânticos;
- skip link leva ao conteúdo principal;
- overlay gerencia foco quando aplicável.

## Anti-padrões

```text
NO_MULTIPLE_MAIN
NO_PAGE_SPECIFIC_DUPLICATED_SHELLS
NO_ADMIN_SHELL_ON_PUNCH
NO_DEAD_SPACE_AFTER_SIDEBAR_COLLAPSE
NO_GLOBAL_LOADING_WHEN_ONLY_LOCAL_REGION_LOADS
NO_INVENTED_HEALTH_STATE
```

## Contrato de testes futuro

- landmarks e `main` único;
- skip link;
- persistência da sidebar;
- overlay mobile;
- RBAC;
- reflow/zoom;
- navegação por teclado e foco.

## RC rápida

Melhoria incorporada: `GlobalFeedbackRegion` semântica e requisito explícito de `main` único.

```text
A1_RC=PASS
A1_NEW_CRITICAL_GAP=NO
```

---

# 2. A2 — TopHeader

```text
TOP_HEADER=FROZEN_INDIVIDUALLY
```

## Propósito

Exibir contexto global da aplicação, identidade do usuário e ações globais realmente disponíveis.

## Anatomia

```text
TopHeader
├─ MobileNavigationTrigger quando necessário
├─ AppContext
│  ├─ Empresa
│  └─ Unidade
├─ GlobalActions quando existirem
├─ Notifications quando existirem
└─ UserMenu
```

## Regra crítica

```text
APP_CONTEXT != EMPRESA_DO_VINCULO
```

Trocar empresa/unidade no header nunca altera silenciosamente o draft ou a empresa contratante do vínculo em criação.

## Estados

```text
CONTEXT_LOADING
CONTEXT_READY
CONTEXT_ERROR
CONTEXT_UNAVAILABLE
```

Não usar contexto padrão inventado quando a consulta falhar.

## RBAC / privacidade

- somente empresas/unidades autorizadas aparecem;
- ações proibidas não aparecem;
- notificações não revelam dados fora do escopo;
- não reservar superfícies para notificações/ações fictícias ainda inexistentes.

## Responsividade e acessibilidade

- desktop pode mostrar contexto completo;
- mobile compacta sem perder nome acessível/contexto;
- seletor de contexto possui teclado, foco visível, nome acessível e erro explícito.

## Anti-padrões

```text
NO_HEADER_MUTATING_DRAFT
NO_OUT_OF_SCOPE_CONTEXT_OPTIONS
NO_INVENTED_FALLBACK_COMPANY
NO_FAKE_NOTIFICATIONS
NO_DUPLICATED_PAGE_HEADER_ROLE
NO_ICON_ONLY_CONTEXT_ON_MOBILE
```

## Testes futuros

- loading/ready/error/unavailable;
- RBAC do contexto;
- mudança de AppContext com draft aberto;
- `APP_CONTEXT != EMPRESA_DO_VINCULO` preservado.

## RC rápida

A lacuna transversal de contexto global versus empresa do vínculo foi aplicada integralmente ao componente.

```text
A2_RC=PASS
A2_NEW_CRITICAL_GAP=NO
```

---

# 3. A3 — Breadcrumb

```text
BREADCRUMB=FROZEN_INDIVIDUALLY
```

## Propósito

Informar localização hierárquica no produto sem substituir o `PageHeader`/`h1`.

## Anatomia e variantes

```text
FULL
COMPACT
```

Exemplo:

```text
Dashboard > Funcionários > Novo funcionário
```

A página atual usa `aria-current="page"` e não precisa linkar para si mesma.

## RBAC / privacidade

- ancestral proibido não vira link acessível por breadcrumb;
- pode permanecer como contexto textual quando necessário;
- evitar dados pessoais/identificadores desnecessários na trilha.

## Responsividade e acessibilidade

- compactar antes de gerar overflow horizontal;
- compactação visual preserva semântica completa;
- `nav` com nome acessível apropriado;
- apenas ancestrais navegáveis entram na sequência de Tab.

## Anti-padrões

```text
NO_BREADCRUMB_AS_H1
NO_CURRENT_PAGE_SELF_LINK
NO_UNBOUNDED_DEEP_TRAIL_WITHOUT_COMPACTION
NO_COMPLETE_HIERARCHY_LOSS_ON_MOBILE
NO_RBAC_LEAK_BY_LINK
NO_UNNECESSARY_PERSONAL_IDENTIFIERS
```

## Testes futuros

- hierarquia;
- `aria-current`;
- links permitidos;
- RBAC;
- compactação;
- teclado;
- zoom 200%.

## RC rápida

Melhoria incorporada: compactação visual não pode reduzir a semântica oferecida a tecnologia assistiva.

```text
A3_RC=PASS
A3_NEW_CRITICAL_GAP=NO
```

---

# 4. A4 — PageHeader

```text
PAGE_HEADER=FROZEN_INDIVIDUALLY
```

## Propósito e anatomia

```text
PageHeader
├─ H1
├─ Description opcional
├─ Metadata/Status quando necessário
└─ Actions
   ├─ Secondary
   └─ Primary
```

Responsabilidades: título, descrição curta quando necessária e ação principal da página, sem duplicação desnecessária do breadcrumb.

## Variantes

```text
STANDARD
WITH_PRIMARY_ACTION
READ_ONLY
WITH_STATUS
```

## Hierarquia e RBAC

- uma ação primária dominante por região;
- ações sem permissão não aparecem apenas desabilitadas;
- uma página possui um título principal claro;
- PageHeader permanece estrutural mesmo enquanto regiões de conteúdo carregam.

## Responsividade

Desktop pode alinhar contexto e ações horizontalmente. Mobile empilha título/descrição/ações e pode ampliar a ação primária sem reduzir touch target.

## Acessibilidade

- `h1` representa a página;
- ordem lógica: contexto textual antes das ações;
- status não depende somente de cor.

## Anti-padrões

```text
NO_DUPLICATED_BREADCRUMB_AND_H1_WEIGHT
NO_MULTIPLE_H1
NO_COMPETING_PRIMARY_ACTIONS
NO_ACTION_DUMP_IN_HEADER
NO_UNNECESSARY_PRIMARY_ACTION_HIDDEN_IN_OVERFLOW
NO_COLOR_ONLY_STATUS
```

## Testes futuros

- `h1` único;
- descrição;
- ações por RBAC;
- hierarquia de ação;
- wrap/stack responsivo;
- teclado;
- zoom/reflow.

## RC rápida

Melhoria incorporada: identidade da página permanece presente durante loading local do conteúdo.

```text
A4_RC=PASS
A4_NEW_CRITICAL_GAP=NO
```

---

# 5. B1 — Button

```text
BUTTON=FROZEN_INDIVIDUALLY
```

## Semântica

```text
BUTTON = executar acao
LINK = navegar
```

Não simular botão com `div` quando um elemento nativo é adequado.

## Variantes

```text
PRIMARY
SECONDARY
TERTIARY
DESTRUCTIVE
```

## Estados

```text
DEFAULT
HOVER
FOCUS_VISIBLE
PRESSED
LOADING
DISABLED
```

`LOADING` preserva rótulo/contexto e impede repetição visual da mesma ação; idempotência futura continua responsabilidade também do backend quando aplicável.

## RBAC

```text
NO_PERMISSION != DISABLED
```

Sem permissão: ação não aparece. `disabled` é permitido quando a ação existe semanticamente, mas está temporariamente indisponível por estado da interface/domínio.

## Responsividade e acessibilidade

- botão não encolhe até perder alvo de toque;
- mobile pode usar largura maior/full-width quando apropriado;
- elemento nativo `button` preferido;
- Enter/Space naturais;
- foco visível consistente;
- Lucide para ícone opcional; ícone decorativo com `aria-hidden`.

## Erro/offline

Botão sozinho não comunica indisponibilidade persistente. Banner/ErrorState/mensagem contextual deve explicar a causa quando necessário.

## Anti-padrões

```text
NO_DIV_AS_BUTTON
NO_COLOR_ONLY_MEANING
NO_COMPETING_PRIMARY_ACTIONS
NO_AMBIGUOUS_DESTRUCTIVE_LABEL
NO_CONTEXTLESS_LOADING
NO_LAYOUT_JUMP_ON_LOADING
NO_PERMISSION_AS_DISABLED_ONLY
NO_BUTTON_FOR_SEMANTIC_NAVIGATION
```

## Testes futuros

### Unitários

- variantes;
- hover/focus/pressed;
- loading;
- disabled;
- ícone/rótulo/nome acessível.

### Integração

- loading impede repetição visual;
- integração com StickyFormActions;
- destructive → ConfirmationModal quando exigido;
- RBAC remove ação;
- submit idempotente quando aplicável.

### Responsivo/a11y

- touch target;
- teclado;
- foco;
- zoom 200%;
- screen reader.

## RC rápida

Melhorias incorporadas: distinções formais `BUTTON != LINK` e `NO_PERMISSION != DISABLED`.

```text
B1_RC=PASS
B1_NEW_CRITICAL_GAP=NO
```

---

# 6. RC conjunta do lote

```text
A1_APPSHELL=FROZEN_INDIVIDUALLY
A2_TOPHEADER=FROZEN_INDIVIDUALLY
A3_BREADCRUMB=FROZEN_INDIVIDUALLY
A4_PAGEHEADER=FROZEN_INDIVIDUALLY
B1_BUTTON=FROZEN_INDIVIDUALLY

BATCH_RC_RESULT=PASS
NEW_CRITICAL_GAPS=0
STRUCTURAL_CONFLICTS=0
```

Integração conceitual:

```text
AppShell
  ↓
TopHeader       → contexto global
  ↓
Breadcrumb      → localização
  ↓
PageHeader      → identidade/tarefa
  ↓
Button          → ação
```

Não foi encontrado conflito com `CollapsibleSidebar`, `HorizontalStepper`, `ContextDrawer`, `StickyFormActions`, Design System, responsividade/a11y ou contrato do Novo Funcionário.

---

# 7. Classificação de validação

```text
VALIDACAO_CONCEITUAL=EXECUTADA
CONTRATO_DE_TESTES_FUTURO=DEFINIDO
VALIDACAO_VISUAL_DESIGN_LAB=NAO_EXECUTADA
TESTE_AUTOMATIZADO_REAL=NAO_EXECUTADO
PRODUCTION_CODE_CHANGED=NO
NF02_STARTED=NO
MERGE_AUTHORIZED=NO
```

A próxima ação deve ser obtida de `13_NF01_REMAINING_WORK_ROADMAP.md`, após atualização do status deste lote.