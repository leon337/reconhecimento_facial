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
│   ├── app-shell-i1.css
│   └── app-shell-i1.js
├── components/
└── screens/
    ├── 01.01-app-shell.html
    ├── 02.01-dashboard.html
    ├── 03.01-funcionarios.html
    ├── 03.03-novo-funcionario.html
    └── 03.04-novo-funcionario-v2.html
```

## Como abrir localmente

```bash
python3 -m http.server 4173 -d docs/nf-01/prototype
```

Depois:

```text
http://localhost:4173/
```

## Fase I — baseline AppShell

```text
I1_DESIGN_LAB_APPSHELL=IMPLEMENTED_IN_ISOLATED_PROTOTYPE
REFERENCE_SCREEN=screens/01.01-app-shell.html
PRODUCTION_CHANGE=NO
```

A tela `01.01-app-shell.html` é a referência canônica inicial para a materialização da Fase I. Ela demonstra:

- `CollapsibleSidebar` em desktop largo, com preferência local não sensível persistida;
- sidebar compacta na faixa intermediária para devolver largura ao workspace;
- navegação overlay em mobile, com backdrop, `Escape`, foco e `inert` quando fechada;
- `TopHeader` com contexto demonstrativo separado do valor de empresa do vínculo;
- `Breadcrumb`, `PageHeader`, skip link e um único `main`;
- targets interativos confortáveis;
- reduced motion;
- reflow sem alterar ordem semântica;
- `Registrar ponto` representado como saída para jornada independente, sem envolver `/punch` no shell administrativo.

A baseline I1 **não reconcilia ainda** Dashboard, Funcionários ou Novo Funcionário com o novo shell; essas telas históricas permanecem preservadas para as próximas etapas da Fase I/J/K/L.

## Estado visual

```text
AppShell I1...................... baseline canônica materializada no Design Lab
Dashboard Desktop V3........... conteúdo/padrão visual anterior preservado; shell a reconciliar
Funcionários Desktop V1........ aprovado anteriormente; shell a reconciliar
Novo Funcionário Desktop V1.... referência histórica
Novo Funcionário Desktop V2.... contrato funcional preservado; layout espacial a reconciliar
```

## Direções substituídas

O laboratório ainda pode conter visualmente decisões históricas. Elas **não são mais canônicas**:

```text
sidebar permanentemente expandida........ SUPERSEDED
stepper vertical do onboarding............ SUPERSEDED
painel contextual direito permanente...... SUPERSEDED
larguras fixas em px como regra geral..... SUPERSEDED
emoji como iconografia de produção......... SUPERSEDED
```

## Direção atual

```text
CollapsibleSidebar
+
TopHeader
+
Breadcrumb / PageHeader
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
→ componentes + máquinas de estado + invalidação + idempotência

INTEGRACAO
→ avançar/voltar + autosave + retomada + conflito + permissão + submit reconciliation

RESPONSIVO
→ 360 / 768 / 1024 / 1440 + intermediários + container resize

ACESSIBILIDADE
→ teclado / foco / screen reader / labels / aria / contraste / reduced motion / zoom 200%
```

O Design Lab funciona como estação de pré-montagem: a peça é auditada aqui antes de qualquer entrada na linha de produção.
