# NF-01 — Catálogo de Componentes

## 1. Regra geral

Componentes são contratos de UI para a NF-02. Nenhum componente deste catálogo está sendo implementado nesta NF.

Estados semânticos possíveis: `LOADING`, `EMPTY`, `READY`, `SUCCESS`, `WARNING`, `DEGRADED`, `ERROR`, `OFFLINE`, `NO_PERMISSION`, `TELEMETRY_UNAVAILABLE`.

## 2. Catálogo obrigatório

| Componente | Função | Variantes | Estados relevantes | Acessibilidade | Responsividade | Uso permitido | Uso proibido |
|---|---|---|---|---|---|---|---|
| **AppShell** | estrutura do admin | default, compact | ready, no_permission | landmarks `nav/main/header`, skip link | sidebar fixa ≥1024; drawer <1024 | admin/suporte | envolver Registrar Ponto |
| **Sidebar** | navegação primária | expanded, collapsed, drawer | ready | lista semântica, item ativo textual, teclado | some em drawer no mobile | áreas autorizadas | exibir item sem permissão |
| **Header** | contexto + ações globais | admin, support | ready, warning | ordem de foco previsível | empilha contexto em 360 | empresa/unidade/usuário | status técnico sem fonte |
| **Breadcrumb** | localização hierárquica | full, compact | ready | `nav aria-label`, página atual | compacta pais intermediários | admin | tela de ponto simples |
| **StatusBadge** | estado curto | success, warning, error, degraded, offline, unknown | todos semânticos | texto + ícone; nunca só cor | não truncar estado | estado com fonte | “OK” inferido/branding |
| **HealthCard** | estado de componente técnico | API, DB, station, backup, AI futura | loading, ready, degraded, error, telemetry_unavailable | heading, fonte/última atualização legível | 1 col mobile; grid desktop | sinais objetivos | verde por ausência de dado |
| **MetricCard** | número com contexto | count, duration, rate | loading, ready, empty, telemetry_unavailable | rótulo + unidade + período | quebra em 1/2/4 colunas | métrica com período/fonte | zero inventado para dado ausente |
| **DataTable** | conjunto tabular | standard, compact | loading, empty, ready, error | headers, caption, foco em ações, sort aria | scroll controlado/colunas prioritárias | dados densos | transformar cada linha em minúsculo desktop no mobile sem hierarquia |
| **Search** | busca textual | inline, standalone | ready, loading | label, clear button nomeado | 100% width mobile | listas grandes | substituir filtro estruturado |
| **FilterBar** | filtros combinados | inline, drawer mobile | ready, loading | fieldset/labels, resumo de filtros | drawer/stack mobile | registros/funcionários | esconder filtro ativo |
| **EmptyState** | consulta válida vazia | neutral, actionable | empty | heading + descrição | central/compact | ausência real | usar em erro/permissão |
| **ErrorState** | falha recuperável | inline, page, panel | error | `role=alert` quando apropriado, foco gerenciado | sem overflow | falha + próximo passo | expor stack trace/segredo |
| **Skeleton** | reserva de layout | text, card, table | loading | `aria-hidden`, região principal informa loading | acompanha layout final | espera perceptível | shimmer infinito/reduced motion ignorado |
| **DegradationBanner** | avisar função parcial | warning, degraded, offline | warning, degraded, offline | mensagem textual, link/ação | full width | impacto global ou de área | usar para sucesso |
| **EventTimeline** | sequência de eventos | operational, audit | loading, empty, ready, error | lista ordenada, timestamp textual | cards verticais mobile | suporte/auditoria | inventar causalidade |
| **DetailDrawer** | detalhe sem perder contexto | right, full-mobile | ready, loading, error | focus trap, título, close, retorno de foco | full-screen <768 | detalhe de registro/evento | fluxo crítico longo no mobile |
| **ConfirmationModal** | confirmar ação sensível | destructive, consequential | ready, loading, error | `dialog`, foco inicial seguro, Escape, retorno | full-ish mobile | remoção biométrica etc. | confirmação genérica sem entidade/consequência |
| **Toast** | feedback transitório | success, info, warning, error | success/warning/error | live region adequada; não conter única informação crítica | largura fluida | confirmação suplementar | erro que exige ação apenas em toast |
| **Pagination** | navegar páginas | numbered, next-prev | ready, loading | labels por página, atual via aria-current | prev/next + resumo mobile | tabela server-side | paginação falsa client-side sobre amostra parcial |
| **LastUpdated** | mostrar recência | relative+absolute | ready, telemetry_unavailable | `<time datetime>`, texto explícito | inline/wrap | health/metrics | substituir fonte do dado |
| **FormField** | label + controle + ajuda/erro | text, select, password, textarea | ready, error, disabled | label persistente, `aria-describedby`, erro associado | full width mobile | todos formulários | placeholder como único label |
| **Button** | ação textual | primary, secondary, tertiary, destructive | ready, loading, disabled | nome acessível, foco, loading anunciado | 100% opcional mobile | ações claras | usar cor como único significado |
| **IconButton** | ação compacta conhecida | neutral, destructive | ready, disabled | `aria-label`, tooltip complementar | ≥44×44 | fechar/copiar/mais opções | ação destrutiva ambígua sem rótulo/contexto |
| **Tabs** | alternar subvisões locais | line, contained | ready, loading | padrão ARIA tabs + setas | scroll horizontal controlado | visões pares | navegação principal do produto |
| **CameraPanel** | câmera + orientação + etapa | punch, enrollment | ready, loading, warning, error, offline | label do preview, status live, instrução textual, fallback acessível | 100% width; proporção estável | ponto/biometria | upload da galeria no fluxo vivo |
| **PunchResult** | confirmação/falha da batida | success, retryable-error, warning | success, error, warning, offline | live region, heading claro, sem depender de cor | destaque grande em 360 | fim de tentativa | exibir “sucesso” antes da persistência confirmada |

## 3. Contratos detalhados dos componentes críticos

### 3.1 AppShell

Estrutura:

```text
┌──────── Sidebar ────────┬──────── Header ─────────┐
│ navegação               │ contexto empresa/unid. │
│                         ├─────────────────────────┤
│                         │ Breadcrumb              │
│                         │ Main                    │
└─────────────────────────┴─────────────────────────┘
```

Regras:
- `main` único por página;
- skip link antes da navegação;
- sidebar não existe na estação de ponto;
- estado de menu não pode ocultar título da página.

### 3.2 HealthCard

Campos mínimos:

```text
nome do componente
estado textual
fonte/sinal
última atualização
impacto, se degradado
link de investigação, se permitido
```

Proibição:

```text
if signal is missing:
    state != HEALTHY
    state = TELEMETRY_UNAVAILABLE
```

### 3.3 DataTable

Contrato:
- cabeçalho fixo apenas quando não prejudicar leitura;
- ordenação deve anunciar direção;
- seleção em massa não entra na NF-02 sem caso aprovado;
- ações por linha ficam em menu ou grupo curto;
- em 360 px, priorizar campos essenciais e abrir detalhe; não espremer todas as colunas.

### 3.4 FormField

Anatomia:

```text
Label obrigatório
[ controle ]
Ajuda opcional
Erro específico
```

O formulário `users_new` atual usa placeholders como rótulo; NF-02 deverá corrigi-lo.

### 3.5 CameraPanel

Etapas visuais:

```text
CAMERA_PERMISSION_REQUIRED
→ CAMERA_READY
→ CAPTURE_PREPARING
→ CAPTURING
→ PROCESSING
→ SUCCESS | CAPTURE_REJECTED | ERROR
```

Nunca mostrar quadro congelado como se a câmera estivesse ativa. O preview precisa permanecer associado ao status textual.

### 3.6 PunchResult

Success deve conter:
- `Registro concluído`;
- nome reconhecido quando permitido;
- tipo (Entrada/Saída);
- horário confirmado pelo servidor;
- CTA para nova tentativa/pessoa somente após estado final.

Erro recuperável deve conter:
- motivo em linguagem simples;
- próxima ação;
- tempo de espera quando `duplicate_punch`;
- request ID apenas em detalhe de suporte, se disponível.

## 4. Convenção de variantes

### Primary

A ação principal de uma tela, no máximo uma dominante por região.

### Secondary

Ações importantes sem competir com a principal.

### Tertiary

Ações contextuais/baixa ênfase.

### Destructive

Somente para efeitos destrutivos reais; nunca usar vermelho como decoração.

## 5. Loading

- Button: preservar largura, spinner + texto `Salvando…`/`Registrando…`;
- Table: skeleton de linhas ou região loading, não tabela vazia piscando;
- Camera: progresso por etapa, não skeleton sobre vídeo;
- Health: skeleton inicialmente; depois `TELEMETRY_UNAVAILABLE` quando sinal faltar.

## 6. Empty vs Error

```text
EMPTY = consulta executou e retornou 0
ERROR = consulta não pôde ser concluída
```

Exemplo Funcionários:
- zero funcionários → `EmptyState` + “Cadastrar funcionário” se `users:create`;
- consulta falhou → `ErrorState` + retry; não mostrar “Nenhum funcionário”.

## 7. Ações destrutivas

Remover biometria deixa de depender de `window.confirm()` na especificação visual e passa a usar `ConfirmationModal` com:

```text
Título: Remover biometria facial?
Entidade: nome do funcionário
Consequência: será necessário novo cadastro facial para usar a identificação
Ações: Cancelar | Remover biometria
```

NF-01 não altera a rota atual.

## 8. Decisão

```text
COMPONENT_CATALOG=COMPLETE
REQUIRED_COMPONENTS=26_SPECIFIED
COMPONENT_STATES=DEFINED
ACCESSIBILITY_CONTRACT=DEFINED
RESPONSIVE_BEHAVIOR=DEFINED_AT_COMPONENT_LEVEL
```