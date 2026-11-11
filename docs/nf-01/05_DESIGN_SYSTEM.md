# NF-01 — Design System

> **Fonte canônica complementar:** `12_NF01_CANONICAL_DECISIONS_2026-08-11.md`.
> Em caso de conflito entre versões anteriores deste arquivo e o registro canônico de 11/08/2026, prevalece o registro canônico, sem alterar `DECISOES_CONGELADAS.md`.

## 1. Direção visual

```text
BASE=VERDE_INSTITUCIONAL
SUPERFICIES=NEUTROS_CLAROS
ACENTO_PREMIUM=DOURADO_MODERADO
DADOS=GRAFITE
STATUS=CORES_SEMANTICAS_INDEPENDENTES_DA_MARCA
FONT=MANROPE
ICON_FAMILY=LUCIDE
```

Regra central:

```text
VERDE_DA_MARCA != SISTEMA_SAUDAVEL
TELEMETRY_UNAVAILABLE != HEALTHY
DEGRADED != DOWN
OFFLINE != ERROR
NOT_IMPLEMENTED != ERROR
```

## 2. Princípios

1. clareza operacional antes de decoração;
2. formulário/tarefa como protagonista;
3. menos estrutura permanente, mais área útil;
4. foco de teclado sempre visível;
5. estado nunca depende apenas de cor;
6. responsividade reorganiza, não apenas reduz;
7. componentes adaptam-se preferencialmente ao container disponível;
8. movimento é funcional e dispensável;
9. dado inexistente não vira valor ilustrativo;
10. ícone complementa significado e nunca é a única fonte semântica.

## 3. Política oficial de dimensionamento

```text
DIMENSIONING_POLICY=FROZEN

rem            → unidade-base do Design System
fr/minmax      → distribuição e grids
clamp          → crescimento fluido com limites
vw/dvh         → viewport quando necessário e preferencialmente limitado
container query→ adaptação ao espaço real do componente
cqi            → dimensão relativa ao container quando útil
ch             → limite de legibilidade textual
%              → relações locais
px             → exceções técnicas, como borda de 1px
```

Os alvos `360 / 768 / 1024 / 1440` são pontos mínimos de teste, não quatro interfaces rígidas.

```text
RESPONSIVO != DIMINUIR_TUDO
RESPONSIVO = REORGANIZAR + REDISTRIBUIR + LIMITAR + EXPANDIR + COLAPSAR
```

## 4. Tipografia

```text
font-family: Manrope
fallback: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace
```

Tokens de referência:

```text
text-small      = 0.875rem
text-body       = 1rem
text-large      = 1.125rem
heading-sm      = 1.25rem
heading-md      = 1.5rem
heading-lg      = clamp(1.75rem, valor fluido, 2.25rem)
```

Textos longos devem possuir limite de leitura, preferencialmente em `ch` quando aplicável.

## 5. Cores institucionais de referência

```text
verde-profundo      #0B3D2B
verde-base          #1B3D2A
verde-suave         #E8F0EB
dourado             #D4AF37
grafite             #2B2B2B
fundo                #F6F8F5
texto-secundario     #68736D
borda                #DDE4DF
```

Estados semânticos são independentes da marca:

```text
SUCCESS
WARNING
DEGRADED
ERROR
INFO
OFFLINE
NO_PERMISSION
TELEMETRY_UNAVAILABLE
```

Os contrastes reais serão validados sobre combinações finais; a especificação não declara conformidade apenas por intenção.

## 6. Espaçamento

```text
space-1 = 0.25rem
space-2 = 0.5rem
space-3 = 0.75rem
space-4 = 1rem
space-6 = 1.5rem
space-8 = 2rem
```

Não congelar medidas de layout em `px` como política geral.

## 7. Raios

```text
radius-sm   = 0.5rem
radius-md   = 0.75rem
radius-lg   = 1rem
radius-pill = pill/full
```

## 8. Bordas

Bordas podem usar `1px` como exceção técnica quando necessário. Sua função é separar superfícies e estados, não substituir hierarquia.

## 9. Sombras

```text
shadow-sm → cards/elevação mínima
shadow-md → popovers/menus
shadow-lg → drawers/modais
```

Sombras devem ser discretas e nunca a única forma de separação.

## 10. Foco

```text
FOCUS_RING
→ claramente visível
→ contraste independente da superfície
→ nunca removido sem substituição
→ coerente em mouse e teclado
```

## 11. Iconografia

```text
ICON_SYSTEM=FROZEN
FAMILY=LUCIDE
STYLE=SVG_MONOLINE
SIZE_UNIT=rem
COLOR=currentColor/token
EMOJI_PRODUCTION=NO
MIX_ICON_FAMILIES=NO
```

Regras:

- ícone decorativo → `aria-hidden`;
- ação por ícone → nome acessível (`aria-label`) e tooltip quando necessário;
- informação/estado → texto acessível + ícone;
- emojis são permitidos somente em wireframe explicativo, nunca como linguagem final do produto.

## 12. Shell

### Sidebar

- expandida: largura fluida limitada, conceitualmente em torno de `clamp(14rem, 17vw, 16rem)` até validação visual;
- compacta: largura funcional aproximadamente `4.5rem`;
- main workspace: `1fr`;
- largura liberada pela sidebar pertence imediatamente ao conteúdo.

### ContextDrawer

- largura fluida limitada;
- desktop: drawer lateral sob demanda;
- tablet/mobile: overlay;
- não consumir largura permanentemente.

### Formulários

- `fr`/`minmax()`;
- container queries quando o componente puder aparecer em superfícies distintas;
- formulários de edição possuem limite confortável de leitura, mesmo em monitores muito largos.

## 13. Motion

```text
motion-fast   = 120ms
motion-normal = 180ms
motion-slow   = 240ms
```

Permitido:

- sidebar expandir/recolher;
- drawer/modal/popover;
- accordion;
- mudança discreta de estado.

Proibido:

- animação decorativa contínua;
- pulsação sem necessidade;
- bouncing;
- movimento que atrasa a tarefa.

`prefers-reduced-motion: reduce` remove deslocamentos/animações não essenciais sem remover informação.

## 14. Ordem semântica

```text
READING_ORDER = FOCUS_ORDER = TASK_LOGIC
```

Grid pode reorganizar de 3→2→1 colunas, mas CSS não pode reordenar semanticamente o fluxo só para fins visuais.

## 15. Touch targets

Alvos interativos devem manter área confortável equivalente ao padrão de aproximadamente 44 CSS px quando aplicável, mas o Design System expressa controles preferencialmente em `rem`.

## 16. Estados globais de UI

```text
LOADING
EMPTY
READY
SUCCESS
WARNING
DEGRADED
ERROR
OFFLINE
NO_PERMISSION
TELEMETRY_UNAVAILABLE
```

`EMPTY` significa consulta válida vazia. `ERROR` significa falha de execução. Não são intercambiáveis.

## 17. Política de toast

```text
TOAST             → feedback secundario/transitorio
BANNER/ERRORSTATE → problema persistente/importante
MODAL             → decisao que exige confirmacao
```

Conflito, permissão removida, sessão, sistema offline ou resultado de submit desconhecido não podem depender apenas de toast.

## 18. Breakpoints / alvos de validação

```text
360  → telefone mínimo de teste
768  → tablet/telefone amplo
1024 → notebook/tablet landscape
1440 → desktop de dados
```

Esses valores não congelam a estrutura do componente; container queries e comportamento guiado pelo conteúdo permanecem preferidos quando adequados.

## 19. Decisão canônica

```text
DESIGN_SYSTEM=FROZEN_FOR_NF01
DIMENSIONING_POLICY=FROZEN
MANROPE=FROZEN
LUCIDE=FROZEN
MOTION_SYSTEM=FROZEN
SEMANTIC_DOM_ORDER=FROZEN
TOAST_POLICY=FROZEN
BRAND_GREEN_IS_NOT_HEALTH=ENFORCED
RESPONSIVE_MEANS_REORGANIZE=ENFORCED
```
