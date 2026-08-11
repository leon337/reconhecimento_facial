# NF-01 — Catálogo Canônico de Componentes

> **Fonte canônica complementar:** `12_NF01_CANONICAL_DECISIONS_2026-08-11.md`.
> Este catálogo substitui a direção anterior quando houver conflito de UX/UI.

## 1. Regra geral

Componentes são contratos de UI para a futura implementação. A NF-01 não implementa produção.

Estados semânticos globais quando aplicáveis:

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

Princípios compartilhados:

- nenhuma ação proibida deve aparecer apenas desabilitada quando a permissão determina que ela não deve existir na UI;
- estado crítico não depende só de cor;
- loading, empty e error são estados diferentes;
- componentes devem respeitar teclado, foco e reduced motion;
- responsividade reorganiza o componente conforme o espaço disponível;
- ordem DOM permanece semântica;
- `rem`, `fr`, `minmax`, `clamp` e container queries seguem `05_DESIGN_SYSTEM.md`.

---

# 2. Shell e navegação

## 2.1 AppShell

Estrutura administrativa única:

```text
AppShell
├─ CollapsibleSidebar
├─ TopHeader
└─ MainWorkspace
   ├─ Breadcrumb
   ├─ PageHeader
   └─ Conteudo
```

Regras:

- `main` único;
- landmarks semânticos;
- skip link;
- usado no admin/suporte;
- **não usado em `/punch`**.

## 2.2 CollapsibleSidebar

```text
COLLAPSIBLE_SIDEBAR=FROZEN
```

Variantes:

- expanded;
- compact;
- overlay-mobile.

Regras:

- desktop nunca some completamente;
- estado persiste entre telas;
- conteúdo recupera largura liberada;
- item ativo por indicador + superfície/contraste + `aria-current`;
- tooltip obrigatório compacta;
- expandir/recolher por botão explícito;
- grupos textuais na expandida; separação visual na compacta;
- mobile vira overlay;
- Enter/Space, `aria-expanded`, foco visível e target adequado.

## 2.3 TopHeader

Função:

- contexto global de empresa/unidade;
- usuário;
- ações globais permitidas;
- notificações quando existirem.

Regra crítica:

```text
APP_CONTEXT != EMPRESA_DO_VINCULO
```

Trocar contexto do header nunca altera silenciosamente dados de formulário.

## 2.4 Breadcrumb

- localização hierárquica;
- não substitui o título da página;
- compacta quando necessário;
- `nav aria-label` apropriado.

## 2.5 PageHeader

- título;
- descrição curta quando necessária;
- ação principal da página;
- não duplicar informação desnecessária do breadcrumb.

---

# 3. Wizard / Novo Funcionário

## 3.1 HorizontalStepper

```text
HORIZONTAL_STEPPER=FROZEN
```

- substitui stepper vertical;
- ícones como linguagem visual principal;
- sem nomes permanentes dentro da barra;
- título completo fica abaixo/fora;
- `Etapa X de 8`;
- tooltip + `aria-label` + texto acessível;
- estados: `COMPLETED`, `CURRENT`, `FUTURE`, `ERROR`, `NEEDS_REVIEW`;
- concluídas podem ser revisitadas;
- futuras não podem ser puladas indevidamente;
- mobile oferece visão simplificada + `Ver etapas` textual sob demanda.

## 3.2 ContextDrawer

```text
CONTEXT_DRAWER=FROZEN
```

- substitui painel direito permanente;
- fechado por padrão;
- abre sob demanda;
- resumo/contexto/pendências/permissões/ajuda;
- sem campos obrigatórios editáveis;
- atalho para etapa relacionada permitido;
- preserva formulário;
- Escape fecha;
- focus management + retorno ao trigger;
- overlay em tablet/mobile;
- largura fluida limitada.

## 3.3 StickyFormActions

```text
STICKY_FORM_ACTIONS=FROZEN
```

Etapas 0–6:

```text
Descartar | Salvar e sair | Voltar | Continuar
```

Etapa 7:

```text
Descartar | Salvar e sair | Voltar | Concluir cadastro
```

- uma ação primária;
- `Voltar` ausente na etapa inicial quando não aplicável;
- `Concluir cadastro` não renderiza antes da revisão;
- `Descartar` separado + confirmação;
- autosave visível;
- mobile reorganiza;
- keyboard-safe; nunca cobre campo ativo.

## 3.4 ResponsiveFormGrid

```text
RESPONSIVE_FORM_GRID=FROZEN
```

- `fr`/`minmax()`;
- container queries;
- 1–3 colunas conforme espaço real;
- largura semântica do campo;
- sem larguras rígidas por campo;
- limite confortável de leitura;
- ordem DOM preservada.

## 3.5 FormSection

```text
FORM_SECTION_PROGRESSIVE_DISCLOSURE=FROZEN
```

- informação principal sempre visível;
- secundária recolhível;
- condicionais por resposta;
- estado preservado;
- recolher não apaga;
- erro em seção fechada fica visível e pode abrir a seção.

## 3.6 FormField / FieldGroup

```text
FIELD_GROUP=FROZEN
```

Anatomia:

```text
Label permanente
[ controle ]
Ajuda curta opcional
Ajuda avancada sob demanda
Erro/estado específico
```

Estados:

```text
NORMAL
FOCUS
FILLED
VALIDATING
VALID
WARNING
ERROR
DISABLED
READONLY
```

Regras:

- placeholder só como exemplo;
- validação local != remota;
- remote validation com debounce quando necessário;
- erro explica como corrigir;
- resumo de erros da etapa;
- foco no primeiro erro;
- máscara tolerante + normalização;
- input mode/autocomplete adequados;
- `aria-describedby`.

### Obrigatório/opcional

- obrigatório segue contrato do campo e semântica HTML;
- opcional recebe `(opcional)`;
- condicional explica quando passa a ser obrigatório.

## 3.7 SearchableCombobox / EntityPicker

```text
ENTITY_PICKER=FROZEN
```

- valor persistido por ID;
- busca tolerante a caixa/acentos/parcial;
- resultados ambíguos mostram contexto;
- RBAC aplicado à própria busca;
- entidade inativa não aparece para novos vínculos, mas histórico continua legível;
- draft retomado detecta entidade que ficou inativa;
- dependências como Empresa → Unidade → Setor → Gestor;
- mudança incompatível não é silenciosa;
- loading/empty/error separados;
- debounce;
- resposta assíncrona obsoleta não vence resposta nova;
- paginação/virtualização quando necessária;
- não autoselecionar resultado único;
- teclado completo/ARIA;
- mobile pode usar sheet/drawer de seleção;
- sem criação improvisada de cadastro mestre dentro do onboarding.

## 3.8 DateField / TimeField / DateTimeField / DateRange

```text
DATE_TIME_PERIOD_PICKER=FROZEN
```

- componentes pequenos, não mega-picker;
- digitação + seletor visual;
- apresentação regional + valor estruturado;
- `DATE != DATETIME`;
- data civil sem timezone arbitrário;
- timestamp real com timezone apropriado;
- períodos validam início/fim;
- período aberto permitido quando domínio permitir;
- sem data final fictícia;
- regra de passado/futuro contextual;
- Hoje apenas quando útil e nunca preenchido silenciosamente;
- navegação rápida mês/ano;
- acessível e mobile-friendly.

---

# 4. Dados e feedback

## 4.1 StatusBadge

- texto + ícone + semântica;
- variantes success/warning/error/degraded/offline/unknown;
- nunca `OK` por inferência ou branding.

## 4.2 HealthCard

Campos mínimos:

```text
componente
estado textual
fonte/sinal
ultima atualizacao
impacto quando degradado
acao de investigacao quando permitida
```

Sem sinal:

```text
state = TELEMETRY_UNAVAILABLE
```

Nunca healthy.

## 4.3 MetricCard

- número + unidade + período/contexto;
- loading/ready/empty/telemetry unavailable;
- não inventar zero.

## 4.4 LastUpdated

- recência explícita;
- valor relativo + absoluto quando útil;
- `<time datetime>`;
- nunca substitui fonte do dado.

## 4.5 DegradationBanner

- problema persistente e impacto operacional;
- warning/degraded/offline;
- não usar para sucesso.

---

# 5. Listas e exploração

## 5.1 DataTable

- cabeçalhos semânticos;
- sorting com `aria-sort`;
- ações nomeadas e focáveis;
- density adequada ao espaço;
- mobile não espreme todas as colunas; pode usar resumo + detalhe;
- loading/empty/error distintos.

## 5.2 Search

- label;
- limpar busca nomeado;
- cancelável;
- largura adaptável;
- não substitui filtro estruturado.

## 5.3 FilterBar

- filtros comuns permanecem acessíveis;
- filtros secundários podem migrar para popover/drawer quando crescerem;
- filtro ativo nunca fica invisível.

## 5.4 Pagination

- páginas ou prev/next conforme contexto;
- `aria-current`;
- preservar busca/filtros;
- não fingir paginação sobre amostra parcial.

## 5.5 EventTimeline

- lista temporal;
- timestamp textual;
- operational/audit;
- não inventar causalidade.

## 5.6 DetailDrawer

- detalhe sem perder contexto;
- foco gerenciado;
- mobile pode ocupar tela inteira;
- não usar para fluxo crítico longo quando isso prejudicar a tarefa.

---

# 6. Estados vazios, erros e confirmações

## 6.1 EmptyState

```text
EMPTY = consulta valida retornou 0
```

- explica ausência;
- oferece próxima ação quando permitida;
- nunca usado para erro/permissão.

## 6.2 ErrorState

```text
ERROR = operacao nao pôde ser concluida
```

- erro seguro;
- recuperação possível;
- sem stack trace/segredo;
- request ID apenas quando apropriado.

## 6.3 ErrorSummary

Hierarquia:

```text
SISTEMA/WIZARD
→ ETAPA
→ SECAO
→ CAMPO
```

Taxonomia:

```text
VALIDATION_ERROR
BUSINESS_RULE_ERROR
PERMISSION_ERROR
CONFLICT_ERROR
NETWORK_ERROR
SYSTEM_ERROR
SUBMIT_OUTCOME_UNKNOWN
```

## 6.4 Skeleton

- reserva formato previsível;
- `aria-hidden` no desenho e loading anunciado na região;
- reduced motion remove shimmer;
- não simula dado inexistente.

## 6.5 ConfirmationModal

- destrutivo/alto impacto;
- entidade e consequência explícitas;
- foco inicial seguro;
- Escape;
- retorno de foco.

## 6.6 Toast

```text
TOAST = feedback secundario/transitorio
```

Permitido:

- rascunho salvo;
- preferência atualizada;
- filtro aplicado.

Proibido como única superfície:

- conflito;
- submit desconhecido;
- permissão removida;
- offline persistente;
- erro crítico.

---

# 7. Controles

## 7.1 Button

Variantes:

```text
PRIMARY
SECONDARY
TERTIARY
DESTRUCTIVE
```

Estados:

```text
DEFAULT
HOVER
FOCUS_VISIBLE
PRESSED
LOADING
DISABLED quando semanticamente aplicável
```

- uma ação primária dominante por região;
- loading preserva contexto/rótulo;
- cor não é significado único.

## 7.2 IconButton

- ação compacta conhecida;
- `aria-label` obrigatório;
- tooltip quando necessário;
- não usar para destruição ambígua sem contexto.

## 7.3 Tooltip

- informação complementar curta;
- acessível por teclado;
- nunca guardar informação obrigatória.

## 7.4 Tabs

- subvisões equivalentes;
- padrão ARIA tabs;
- não usar como wizard nem navegação principal.

---

# 8. Câmera e ponto

## 8.1 CameraPanel

Estados:

```text
AGUARDANDO_PERMISSAO
CAMERA_INDISPONIVEL
PRONTA
CAPTURANDO
VALIDANDO_QUALIDADE
PROCESSANDO
SUCESSO
FALHA
```

Regras:

- preview ao vivo associado ao status textual;
- não mostrar frame congelado como câmera ativa;
- onboarding biométrico usa câmera ao vivo;
- upload/galeria fora do fluxo normal;
- progresso textual e live region adequada;
- timeout/falha recuperável.

## 8.2 PunchResult

Success somente após persistência confirmada.

Exemplo conceitual:

```text
Registro concluido
Entrada · horario confirmado
[ Finalizar / Proxima pessoa ]
```

Erro:

```text
Nao foi possivel registrar
motivo em linguagem simples
[ Tentar novamente ]
```

Funcionário não recebe logs/códigos técnicos na superfície principal.

---

# 9. Estado do catálogo

```text
COMPONENT_CATALOG=CANONICALIZED
STRUCTURAL_COMPONENTS=FROZEN
WIZARD_COMPONENTS=FROZEN
GLOBAL_COMPONENTS=DEFINED
ACCESSIBILITY_CONTRACT=DEFINED
RESPONSIVE_CONTRACT=DEFINED
PRODUCTION_IMPLEMENTATION=NOT_STARTED
```
