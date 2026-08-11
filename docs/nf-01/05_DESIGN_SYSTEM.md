# NF-01 — Design System

## 1. Direção visual

```text
BASE=VERDE_INSTITUCIONAL
SUPERFICIES=NEUTROS_CLAROS
ACENTO_PREMIUM=DOURADO_MODERADO
DADOS=GRAFITE
STATUS=CORES_SEMANTICAS_INDEPENDENTES_DA_MARCA
```

> O verde institucional é marca. Ele **não** significa automaticamente sistema saudável.

## 2. Princípios

1. clareza operacional antes de decoração;
2. alta legibilidade e contraste;
3. componentes densos no admin, simples no ponto;
4. espaços consistentes em múltiplos de 4 px;
5. uma cor semântica nunca é a única forma de comunicar estado;
6. foco de teclado sempre visível;
7. motion curto e dispensável;
8. superfícies claras; dados e texto em grafite;
9. dourado usado como acento, não como cor universal de CTA;
10. ícones complementam rótulos; não substituem texto em ações críticas;
11. o Design System define as telas; uma tela isolada não redefine o Design System.

## 3. Tipografia

```text
Primary: Manrope
Fallback: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
Mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace
```

| Token | Tamanho | Line-height | Peso sugerido | Uso |
|---|---:|---:|---:|---|
| `text-xs` | 12 px | 16 px | 500 | metadado curto |
| `text-sm` | 14 px | 20 px | 400/500 | suporte e labels secundários |
| `text-md` | 16 px | 24 px | 400/500 | corpo e inputs |
| `text-lg` | 18 px | 28 px | 600 | subtítulo/card |
| `text-xl` | 20 px | 28 px | 600/700 | seção |
| `text-2xl` | 24 px | 32 px | 700 | título de tela |
| `text-3xl` | 32 px | 40 px | 700/800 | destaque de painel |
| `text-4xl` | 40 px | 48 px | 800 | uso excepcional em ponto/kiosk |

Corpo padrão nunca abaixo de 16 px no fluxo de Registrar Ponto.

## 4. Cores institucionais

| Token | Valor | Uso permitido |
|---|---|---|
| `brand-900` | `#143D2B` | header/ênfase escura |
| `brand-800` | `#1B4D37` | botão primário institucional |
| `brand-700` | `#236647` | links/ênfase quando contraste permitir |
| `brand-600` | `#2E7D57` | decoração, ícone não textual, gráficos de marca |
| `brand-100` | `#E8F2EC` | fundo institucional suave |
| `premium-700` | `#7A5C00` | texto/acento dourado acessível |
| `premium-500` | `#C7A33D` | borda/decorativo, nunca texto pequeno em branco |
| `premium-100` | `#F8F1D9` | fundo suave |

## 5. Neutros e superfícies

| Token | Valor | Uso |
|---|---|---|
| `surface-canvas` | `#F6F8F6` | fundo da aplicação |
| `surface-default` | `#FFFFFF` | cards, formulários |
| `surface-subtle` | `#F1F4F2` | cabeçalhos de tabela/áreas secundárias |
| `text-primary` | `#1F2933` | texto principal/dados |
| `text-secondary` | `#5F6B66` | texto secundário |
| `text-disabled` | `#7D8883` | somente elemento realmente desabilitado |
| `border-default` | `#DCE3DE` | divisores/bordas |
| `border-strong` | `#AAB7B0` | controle/ênfase |

## 6. Cores semânticas independentes

| Semântica | Texto/ícone forte | Fundo suave | Uso |
|---|---|---|---|
| success | `#1B5E20` | `#EAF6EC` | ação confirmada |
| warning | `#7A4B00` | `#FFF4DB` | atenção/risco |
| error | `#B42318` | `#FDECEC` | falha |
| info | `#175CD3` | `#EEF4FF` | informação neutra |
| offline | `#475467` | `#F2F4F7` | conectividade offline |
| unknown/telemetry | `#475467` | `#F2F4F7` | estado não conclusivo |

`DEGRADED` usa warning com texto explícito. `TELEMETRY_UNAVAILABLE` usa neutro/unknown, nunca success.

## 7. Contraste de referência

| Par | Contraste aproximado | Resultado |
|---|---:|---|
| branco / `brand-800` | 9.71:1 | AAA texto normal |
| branco / `brand-700` | 6.86:1 | AA texto normal |
| `text-primary` / branco | 14.76:1 | AAA |
| `text-secondary` / branco | 5.55:1 | AA |
| `premium-700` / branco | 6.25:1 | AA |
| success / branco | 7.87:1 | AAA |
| warning / branco | 7.41:1 | AAA |
| error / branco | 6.57:1 | AA |
| info / branco | 5.99:1 | AA |
| offline / branco | 7.69:1 | AAA |

## 8. Foco

```text
focus.color = #7A5C00
focus.width = 3px
focus.offset = 2px
focus.style = solid
```

## 9. Espaçamento

Base: 4 px.

| Token | px |
|---|---:|
| `space-0` | 0 |
| `space-1` | 4 |
| `space-2` | 8 |
| `space-3` | 12 |
| `space-4` | 16 |
| `space-6` | 24 |
| `space-8` | 32 |
| `space-10` | 40 |
| `space-12` | 48 |
| `space-16` | 64 |

## 10. Grid e largura

### Shell administrativo

- 4 colunas em mobile;
- 8 colunas em tablet;
- 12 colunas em desktop;
- gutter: 16 px mobile, 24 px tablet, 32 px desktop;
- conteúdo principal: `max-width: 1440px` para dados;
- formulários de edição limitados a largura legível;
- sidebar não conta como coluna de conteúdo.

### Registrar Ponto

- composição central;
- câmera ocupa largura útil disponível;
- limite de leitura: aproximadamente 640–720 px em desktop;
- ação primária permanece imediatamente relacionada à câmera e ao resultado.

## 11. Microtokens congelados pela RC-01

Estes valores completam a fundação necessária para mockups consistentes e poderão ser revisados somente se a auditoria visual demonstrar problema concreto.

### Shell

```text
sidebar.expanded.width = 248px
sidebar.collapsed.width = 72px
topbar.height = 64px
content.desktop.max = 1440px
content.page.padding.mobile = 16px
content.page.padding.tablet = 24px
content.page.padding.desktop = 32px
```

### Controles

```text
control.height.sm = 40px
control.height.md = 44px
control.height.lg = 48px
button.primary.height = 44px
button.kiosk.height = 56px
input.default.height = 44px
touch.target.min = 44px
```

### Tabelas

```text
table.row.default = 56px
table.row.compact = 48px
table.header = 44px
table.cell.padding.x = 16px
table.cell.padding.y = 12px
```

### Ícones

```text
icon.sm = 16px
icon.md = 20px
icon.lg = 24px
icon.navigation = 20px
icon.stroke = 1.75–2px
```

Direção visual: família outline consistente. A biblioteca de implementação permanece decisão da NF-02; o mockup da NF-01 deve usar uma única família coerente.

### Frame de auditoria

```text
desktop.reference = 1440x1024
mobile.reference = 360px width
export.audit.desktop = 2x quando aplicável
```

## 12. Raios

| Token | Valor | Uso |
|---|---:|---|
| `radius-sm` | 6 px | input/tag |
| `radius-md` | 10 px | botão/card pequeno |
| `radius-lg` | 14 px | card/painel |
| `radius-full` | 999 px | badge/avatar |

## 13. Bordas

```text
border.default = 1px solid #DCE3DE
border.strong = 1px solid #AAB7B0
border.error = 1px solid #B42318
```

## 14. Sombras

```text
shadow-sm = 0 1px 2px rgba(31,41,51,.08)
shadow-md = 0 6px 18px rgba(31,41,51,.10)
shadow-overlay = 0 16px 40px rgba(31,41,51,.16)
```

Sombras são auxiliares, nunca a única separação entre regiões.

## 15. Estados de interação dos controles

Todo controle interativo deverá ter especificação visual para:

```text
DEFAULT
HOVER
FOCUS_VISIBLE
PRESSED
DISABLED
LOADING quando aplicável
ERROR quando aplicável
```

Regras:
- hover não substitui foco;
- pressed deve ser visualmente distinto de hover;
- disabled não usa apenas redução extrema de opacidade que comprometa legibilidade;
- loading preserva largura e rótulo contextual (`Salvando…`, `Registrando…`).

## 16. Motion

| Token | Duração | Uso |
|---|---:|---|
| `motion-fast` | 120 ms | hover/foco visual |
| `motion-base` | 180 ms | expansão curta |
| `motion-slow` | 250 ms | drawer/modal |

Curva sugerida: `cubic-bezier(.2,0,0,1)`.

`prefers-reduced-motion: reduce` remove animações não essenciais.

## 17. Breakpoints

| Token | Largura | Intenção |
|---|---:|---|
| `xs` | 360 px | telefone mínimo de aceite |
| `md` | 768 px | tablet/telefone amplo |
| `lg` | 1024 px | notebook/tablet landscape |
| `2xl` | 1440 px | desktop de dados |

## 18. Densidade e touch targets

- alvo mínimo: 44×44 px;
- CTA principal do ponto: 56 px;
- distância mínima entre ação destrutiva e primária: 8 px;
- admin pode usar tabela compacta somente a partir de 1024 px;
- mobile prioriza uma coluna e ações essenciais.

## 19. Gráficos e dados

- cor de marca não representa automaticamente “bom”;
- tooltip não pode ser único meio de acesso ao valor;
- tabelas continuam sendo fonte textual acessível quando gráfico existir;
- valores sem fonte são omitidos ou declarados indisponíveis, nunca preenchidos com zero ilustrativo.

## 20. Tokens de z-index

```text
base = 0
sticky = 20
dropdown = 40
drawer = 60
modal = 80
toast = 100
```

## 21. Decisão RC-01

```text
DESIGN_TOKENS=COMPLETE_WITH_MICROTOKENS
MANROPE=PRESERVED_FOR_VISUAL_AUDIT
SHELL_DIMENSIONS=FROZEN_FOR_MOCKUP
CONTROL_DIMENSIONS=FROZEN_FOR_MOCKUP
TABLE_DENSITY=FROZEN_FOR_MOCKUP
ICON_SCALE=FROZEN_FOR_MOCKUP
INTERACTION_STATES=REQUIRED
BRAND_GREEN_IS_NOT_HEALTH=ENFORCED
BREAKPOINTS=FROZEN
```