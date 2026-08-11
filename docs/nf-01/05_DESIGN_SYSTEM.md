# NF-01 — Design System

## 1. Direção visual

A direção visual segue as decisões congeladas:

```text
BASE=VERDE_INSTITUCIONAL
SUPERFICIES=NEUTROS_CLAROS
ACENTO_PREMIUM=DOURADO_MODERADO
DADOS=GRAFITE
STATUS=CORES_SEMANTICAS_INDEPENDENTES_DA_MARCA
```

Regra crítica:

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
10. ícones complementam rótulos; não substituem texto em ações críticas.

## 3. Tipografia

### Família

```text
Primary: Manrope
Fallback: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
Mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace
```

A implementação da NF-02 deve escolher carregamento que não torne a UI dependente de uma CDN para funcionar.

### Escala

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

`DEGRADED` usa semântica de warning com texto explícito `Degradado`. `TELEMETRY_UNAVAILABLE` usa neutro/unknown, nunca success.

## 7. Contraste validado dos pares principais

Cálculo WCAG relativo realizado na NF-01:

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

A NF-02 deve repetir a checagem quando combinar tokens em superfícies diferentes.

## 8. Foco

```text
focus.color = #7A5C00
focus.width = 3px
focus.offset = 2px
focus.style = solid
```

Regras:
- não remover outline sem substituto equivalente;
- foco deve ser visível em branco, canvas e brand surfaces;
- foco e hover são estados distintos;
- componente desabilitado não recebe foco se não for interativo.

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
- conteúdo principal: `max-width: 1440px` para dados; formulários de edição limitados a largura legível;
- sidebar não conta como coluna de conteúdo.

### Registrar Ponto

- composição central;
- câmera ocupa largura útil disponível;
- limite de leitura: aproximadamente 640–720 px em desktop;
- ação primária nunca afastada da câmera/resultado por colunas laterais.

## 11. Raios

| Token | Valor | Uso |
|---|---:|---|
| `radius-sm` | 6 px | input/tag |
| `radius-md` | 10 px | botão/card pequeno |
| `radius-lg` | 14 px | card/painel |
| `radius-full` | 999 px | badge/avatar |

Evitar excesso de cápsulas em controles comuns.

## 12. Bordas

```text
border.default = 1px solid #DCE3DE
border.strong = 1px solid #AAB7B0
border.error = 1px solid #B42318
```

Inputs em erro também exibem mensagem e ícone/label, não apenas borda vermelha.

## 13. Sombras

Sombras são auxiliares, nunca únicas para separar regiões.

```text
shadow-sm = 0 1px 2px rgba(31,41,51,.08)
shadow-md = 0 6px 18px rgba(31,41,51,.10)
shadow-overlay = 0 16px 40px rgba(31,41,51,.16)
```

Borda continua obrigatória em overlays quando necessária para contraste.

## 14. Motion

| Token | Duração | Uso |
|---|---:|---|
| `motion-fast` | 120 ms | hover/foco visual |
| `motion-base` | 180 ms | expansão curta |
| `motion-slow` | 250 ms | drawer/modal |

Curva sugerida: `cubic-bezier(.2,0,0,1)`.

`prefers-reduced-motion: reduce`:
- remover animações não essenciais;
- evitar movimento de câmera/UI;
- preservar apenas mudança instantânea de estado.

## 15. Breakpoints

| Token | Largura | Intenção |
|---|---:|---|
| `xs` | 360 px | telefone mínimo de aceite |
| `md` | 768 px | tablet/telefone amplo |
| `lg` | 1024 px | notebook/tablet landscape |
| `2xl` | 1440 px | desktop de dados |

Implementação pode incluir pontos intermediários, mas não pode deixar de validar exatamente essas quatro larguras.

## 16. Densidade e touch targets

- alvo mínimo: 44×44 px;
- ação primária da câmera/ponto: mínimo 48 px de altura; preferível 52 px;
- distância mínima entre ações destrutiva e primária: `space-2` ou maior;
- admin pode usar densidade compacta em tabela somente a partir de 1024 px;
- mobile prioriza uma coluna e ações essenciais.

## 17. Ícones

Direção:
- SVG outline consistente, caixa 20×20 ou 24×24;
- stroke coerente;
- `aria-hidden="true"` quando decorativo;
- `aria-label`/texto visível em IconButton;
- não usar ícone isolado para ação destrutiva crítica;
- não usar check verde para estado técnico sem fonte.

A biblioteca concreta será decisão de implementação da NF-02; a NF-01 não adiciona dependência.

## 18. Gráficos e dados

- cor de marca não representa automaticamente “bom”;
- série de dados usa escala separada da semântica de status;
- tooltip não pode ser único meio de acesso ao valor;
- tabelas são fonte textual acessível quando gráfico existir;
- valores sem fonte devem ser omitidos, não preenchidos com zero.

## 19. Tokens de z-index

```text
base = 0
sticky = 20
dropdown = 40
drawer = 60
modal = 80
toast = 100
```

Evitar números arbitrários por tela.

## 20. Decisão

```text
DESIGN_TOKENS=COMPLETE
BRAND_GREEN_IS_NOT_HEALTH=ENFORCED
CONTRAST_BASELINE=CHECKED
BREAKPOINTS=FROZEN
FOCUS_CONTRACT=FROZEN
MOTION_REDUCED=SUPPORTED_BY_SPEC
```