# NF-01 — Design Lab

Laboratório visual isolado para materializar e auditar a NF-01 antes da NF-02.

## Fonte canônica

Antes de alterar qualquer tela do laboratório, ler:

```text
../12_NF01_CANONICAL_DECISIONS_2026-08-11.md
../05_DESIGN_SYSTEM.md
../06_COMPONENT_CATALOG.md
../07_WIREFRAMES.md
../08_RESPONSIVE_ACCESSIBILITY.md
../09_TEST_AND_ACCEPTANCE_STRATEGY.md
../46_NF01_CATALOG_COMPLETENESS_H10_CLOSEOUT_2026-08-17.md
../47_NF01_DESIGN_LAB_I1_APPSHELL_2026-08-17.md
../48_NF01_DESIGN_LAB_I2_APPSHELL_ADOPTION_CONTRACT_2026-08-17.md
../49_NF01_DESIGN_LAB_I3_SHARED_APPSHELL_SUBSTRATE_2026-08-17.md
```

`DECISOES_CONGELADAS.md` permanece inalterado e superior quando aplicável.

## Regra de isolamento

```text
PROTOTYPE_SCOPE=docs/nf-01/prototype/**
PRODUCTION_TEMPLATES_CHANGED=NO
FLASK_ROUTES_CHANGED=NO
BACKEND_CHANGED=NO
NF02_STARTED=NO
MERGE_AUTHORIZED=NO
```

Durante auditoria, usar **somente dados fictícios**. Não inserir dados pessoais reais no Design Lab.

## Estrutura atual

```text
prototype/
├── index.html
├── README.md
├── NEW_EMPLOYEE_V2_UX_SPEC.md
├── assets/
│   ├── app-shell.css
│   └── app-shell.js
├── components/
└── screens/
    ├── 01.01-app-shell.html
    ├── 02.01-dashboard.html
    ├── 03.01-funcionarios.html
    ├── 03.03-novo-funcionario.html
    └── 03.04-novo-funcionario-v2.html
```

Os arquivos históricos `app-shell-i1.css` e `app-shell-i1.js` foram substituídos pelo substrato compartilhado I3 e não devem voltar a ser usados em novas telas.

## Como abrir localmente

```bash
python3 -m http.server 4173 -d docs/nf-01/prototype
```

Depois:

```text
http://localhost:4173/
```

## Fase I — AppShell

```text
I1_DESIGN_LAB_APPSHELL=COMPLETE
I2_APPSHELL_ADOPTION_CONTRACT=COMPLETE
I3_SHARED_APPSHELL_SUBSTRATE=COMPLETE
REFERENCE_SCREEN=screens/01.01-app-shell.html
CANONICAL_APPSHELL=ONE
PRODUCTION_CHANGE=NO
```

### I1 — baseline visual

I1 materializou a referência inicial de:

- `CollapsibleSidebar` em desktop largo, com preferência local não sensível persistida;
- sidebar compacta na faixa intermediária para devolver largura ao workspace;
- navegação overlay em mobile, com backdrop, `Escape`, foco e `inert`;
- `TopHeader` com contexto demonstrativo separado do valor de empresa do vínculo;
- `Breadcrumb`, `PageHeader`, skip link e um único `main`;
- targets interativos confortáveis;
- reduced motion;
- reflow sem alterar ordem semântica;
- `Registrar ponto` como saída para jornada independente, sem envolver `/punch` no shell administrativo.

### I2 — contrato de adoção

I2 congelou:

```text
CANONICAL_APPSHELL=ONE
PAGE_CONTENT != SHELL_IMPLEMENTATION
SHARED_APPSHELL_STRUCTURE=REQUIRED
SHARED_APPSHELL_BEHAVIOR=REQUIRED
COPY_PASTE_SHELL_PER_SCREEN=PROHIBITED
LEGACY_APP_SHELL=SUPERSEDED_FOR_NEW_WORK
```

Dashboard, Funcionários e Novo Funcionário continuam preservados e ainda não foram declarados reconciliados.

### I3 — substrato reutilizável

I3 substitui a implementação temporária `.i1-*` por uma interface interna neutra do Design Lab:

```text
assets/app-shell.css
+
assets/app-shell.js
```

A página consumidora fornece:

```text
BODY METADATA
+
<main id="conteudo" data-app-shell-content>
  Breadcrumb
  PageHeader
  PageContent
</main>
```

O bootstrap compartilhado materializa:

```text
CollapsibleSidebar
+
TopHeader
+
MainWorkspace wrapper
+
mobile overlay / inert / focus / Escape
+
preferência compacta
+
active nav state
```

A montagem é deliberadamente idempotente: chamadas repetidas de `NF01AppShell.mount()` não devem criar outro shell. O `main` original da página é preservado e movido para o workspace, em vez de um segundo `main` ser criado.

Regra crítica:

```text
DESIGN_LAB_JS_COMPOSITION != PRODUCTION_ARCHITECTURE
```

O mecanismo JS de composição existe apenas para o laboratório estático. Ele não congela a futura arquitetura Flask/Jinja, includes, macros ou herança de templates.

## Estado visual

```text
AppShell I3...................... substrato compartilhado + referência canônica
Dashboard Desktop V3........... conteúdo/padrão visual anterior preservado; shell a reconciliar
Funcionários Desktop V1........ conteúdo anterior preservado; shell a reconciliar
Novo Funcionário Desktop V1.... referência histórica
Novo Funcionário Desktop V2.... contrato funcional preservado; layout espacial a reconciliar
```

## Direções substituídas

O laboratório ainda pode conter visualmente decisões históricas. Elas **não são mais canônicas**:

```text
sidebar permanentemente expandida........ SUPERSEDED
shell copiado por tela.................... SUPERSEDED
classes .i1-* como API permanente......... SUPERSEDED
stepper vertical do onboarding............ SUPERSEDED
painel contextual direito permanente...... SUPERSEDED
larguras fixas em px como regra geral..... SUPERSEDED
emoji como iconografia de produção......... SUPERSEDED
```

## Direção atual

```text
Shared AppShell substrate
+
CollapsibleSidebar
+
TopHeader
+
Breadcrumb / PageHeader fornecidos pela página
+
HorizontalStepper quando houver wizard
+
MainWorkspace amplo
+
ContextDrawer sob demanda
+
StickyFormActions no onboarding
```

## Novo Funcionário — contrato

O wizard continua com oito etapas:

```text
0 Tipo de relação
1 Dados pessoais
2 Endereço
3 Vínculo
4 Pagamento
5 Acesso ao sistema
6 Biometria
7 Revisão e conclusão
```

Regras canônicas principais:

- `HorizontalStepper` icon-first; sem nomes permanentes dentro da barra;
- `Ver etapas` textual sob demanda;
- `NEEDS_REVIEW` quando decisão anterior invalida etapa concluída;
- `ContextDrawer` substitui resumo lateral permanente;
- `StickyFormActions` possui uma ação primária;
- `Concluir cadastro` só existe na Etapa 7;
- autosave, draft, conflito e retomada têm estados próprios;
- EntityPicker usa catálogo mestre/ID;
- formulários usam grid fluido e progressive disclosure;
- opcionais são explicitamente identificados;
- biometria é separada da foto administrativa e respeita RBAC;
- captura biométrica normal usa câmera ao vivo, sem galeria/upload;
- conclusão futura é transacional/idempotente;
- `OUTCOME_UNKNOWN` exige reconciliação antes de retry;
- app context do header não é a empresa contratante do vínculo.

Detalhes completos: `../12_NF01_CANONICAL_DECISIONS_2026-08-11.md`.

## Design System atual

```text
FONT=Manrope
ICON_FAMILY=Lucide
BASE_UNIT=rem
GRID=fr/minmax
FLUID=clamp
COMPONENT_RESPONSIVE=container queries quando aplicável
VIEWPORT_UNITS=limitadas e contextuais
PX=exceção técnica
```

Princípio:

```text
RESPONSIVO != DIMINUIR_TUDO
RESPONSIVO = REORGANIZAR
```

## Auditoria obrigatória

- coerência com registro canônico;
- hierarquia visual;
- shell compartilhado;
- ausência de shell duplicado em dupla montagem;
- preservação de exatamente um `main`;
- legibilidade;
- densidade do onboarding;
- estados de erro/loading/conflict/offline;
- hover/focus/pressed quando aplicável;
- 360/768/1024/1440 + larguras intermediárias;
- zoom 200%;
- keyboard-only;
- reduced motion;
- mobile keyboard safe;
- ausência de dados/estados apresentados como reais sem fonte.

## Testes futuros

```text
UNITARIO
→ montagem idempotente + preferência + aria-expanded + inert + foco + reduced motion

INTEGRACAO
→ AppShell + conteúdo de página + navegação + viewport + reconciliação incremental

RESPONSIVO
→ 360 / 768 / 1024 / 1440 + intermediários + container resize

ACESSIBILIDADE
→ teclado / foco / screen reader / labels / aria / contraste / reduced motion / zoom 200%
```

O Design Lab funciona como estação de pré-montagem: a peça é auditada aqui antes de qualquer entrada na linha de produção.
