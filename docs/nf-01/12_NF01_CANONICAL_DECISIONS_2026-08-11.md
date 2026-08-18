# NF-01 — Registro Canônico de Decisões UX/UI — 2026-08-11

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Escopo:** documentação + Design Lab da NF-01  
**Produção:** inalterada  
**NF-02:** não iniciada  
**Merge:** não autorizado  
**Gate humano final:** LEANDRO  

---

## 0. Objetivo deste documento

Este arquivo oficializa, no repositório, **as decisões aprovadas e congeladas no ciclo de UX/UI da NF-01 realizado em 11/08/2026**, para que a continuidade do projeto não dependa da memória de um chat.

Ele deve ser lido antes de qualquer nova alteração de UX/UI relacionada à NF-01, ao onboarding de funcionário, ao shell administrativo, aos componentes compartilhados, à responsividade ou à acessibilidade.

### 0.1 Regra de precedência

```text
DECISOES_CONGELADAS.md
        ↓
regras históricas/projeto que permanecem imutáveis
        ↓
12_NF01_CANONICAL_DECISIONS_2026-08-11.md
        ↓
decisões canônicas deste ciclo de UX/UI
        ↓
demais documentos e protótipos da NF-01
```

Regras:

1. `DECISOES_CONGELADAS.md` permanece inalterado e superior a este documento quando houver matéria já congelada ali.
2. Para decisões de UX/UI tomadas neste ciclo, este documento prevalece sobre versões anteriores de `05_DESIGN_SYSTEM.md`, `06_COMPONENT_CATALOG.md`, `07_WIREFRAMES.md`, `08_RESPONSIVE_ACCESSIBILITY.md`, `09_TEST_AND_ACCEPTANCE_STRATEGY.md`, `11_RC01_UI_UX_REFINEMENTS.md`, `prototype/README.md` e `prototype/NEW_EMPLOYEE_V2_UX_SPEC.md` quando houver conflito.
3. Documento antigo conflitante deve ser corrigido; não se deve escolher silenciosamente a versão antiga.
4. Nenhuma decisão deste documento autoriza código de produção, backend, migração, deploy, IA ou NF-02.

---

# 1. Guardrails da NF-01

```text
PRODUCTION_CODE_CHANGED=NO
APP_CHANGED=NO
TEMPLATES_CHANGED=NO
STATIC_CHANGED=NO
MIGRATIONS_CHANGED=NO
FLASK_ROUTES_CHANGED=NO
BACKEND_CHANGED=NO
DECISOES_CONGELADAS_CHANGED=NO
NF02_STARTED=NO
PONTO_TO_ATTENDANCE_EVENT_MIGRATION=NO
AI_IMPLEMENTED=NO
OBSERVABILITY_BACKEND_IMPLEMENTED=NO
DEPLOY=NO
PRODUCTION_HOMOLOGATION=NO
LEGAL_CONFORMITY_DECLARED=NO
PR_32_MERGE_AUTHORIZED=NO
```

A NF-01 continua sendo **Produto + Design System + protótipo isolado**.

---

# 2. Contrato funcional canônico — Novo Funcionário

O onboarding oficial possui oito etapas:

```text
0 Tipo de relação
1 Dados pessoais
2 Endereço
3 Vínculo / relação operacional
4 Pagamento
5 Acesso ao sistema
6 Biometria
7 Revisão e conclusão
```

Princípio:

```text
cadastro = linha de montagem

entrada
  ↓
etapa contextual
  ↓
validação
  ↓
preservação de estado
  ↓
próxima etapa
  ↓
revisão final
  ↓
conclusão confirmada
```

## 2.1 Etapa 0 — Tipo de relação

Opções canônicas:

- CLT comum;
- CLT intermitente;
- Sem vínculo empregatício;
- Outros, selecionado a partir de cadastro mestre, sem texto livre improvisado.

Regras:

- a escolha dirige os campos condicionais posteriores;
- `employee` e `non-employee` seguem fluxos operacionais distintos;
- a classificação do software **não define a realidade jurídica** da relação;
- alteração posterior desta etapa pode invalidar etapas seguintes e deve acionar `NEEDS_REVIEW`.

## 2.2 Etapa 1 — Dados pessoais

### Identificação

- Nome completo — obrigatório;
- CPF — obrigatório e identificador primário da pessoa;
- Data de nascimento — obrigatória;
- RG — opcional;
- foto administrativa — opcional e separada da biometria;
- CTPS física antiga não entra por padrão;
- PIS/PASEP/NIS não entra por padrão no cadastro inicial.

### Dados civis

- sexo — obrigatório;
- raça/cor autodeclarada — obrigatória;
- grau de instrução — obrigatório;
- nacionalidade — obrigatória;
- país de nascimento — obrigatório;
- estado civil — opcional;
- naturalidade — opcional;
- nome social — opcional/condicional.

### Contato

- telefone principal — obrigatório operacionalmente;
- WhatsApp — opcional;
- e-mail pessoal — opcional;
- ao menos um contato de recados/emergência;
- pode ser a mesma pessoa para recado e emergência.

### Complementares

- dependentes — opcionais/condicionais, podem gerar pendência administrativa;
- PcD/reabilitação — condicional, sensível e de acesso restrito;
- não usar campo livre de diagnóstico por padrão;
- trabalhador estrangeiro abre campos específicos;
- anexos são opcionais/condicionais e com finalidade definida.

### Integridade

- CPF duplicado bloqueia nova **PESSOA**;
- nome + nascimento semelhante gera aviso, não bloqueio;
- readmissão reutiliza a pessoa e cria novo vínculo;
- uma pessoa pode possuir vários vínculos históricos.

## 2.3 Etapa 2 — Endereço

- país primeiro, com Brasil como padrão;
- suportar Brasil, exterior e rural/localidade;
- Brasil urbano: CEP, logradouro, número ou S/N, complemento, bairro, cidade, UF, referência;
- CEP urbano obrigatório;
- busca automática por CEP com fallback manual e possibilidade de correção;
- provedor de CEP não fica hardcoded no contrato de produto;
- rural: CEP pode não existir; localidade/município/UF formam núcleo obrigatório;
- referência rural é recomendada;
- um endereço residencial vigente por padrão;
- preservar histórico, vigência e auditoria;
- não sobrescrever histórico silenciosamente;
- múltiplos endereços residenciais ativos não são padrão.

## 2.4 Etapa 3 — Vínculo / relação operacional

- empresa contratante — cadastro mestre;
- matrícula — gerada automaticamente somente na confirmação final;
- unidade base — cadastro mestre;
- setor/departamento — cadastro mestre;
- cargo/função — cadastro mestre pesquisável;
- gestor — suportado; ausência pode gerar pendência administrativa;
- jornada/horário — cadastro mestre e com vigência;
- jornada e escala são conceitos separados;
- unidade base é diferente de alocação temporária futura em obra/evento;
- remuneração contratual pertence à Etapa 3;
- Etapa 4 trata destino/forma de pagamento;
- benefícios e vale-transporte habitual pertencem ao vínculo;
- transporte eventual de obra/evento fica fora do onboarding.

### CLT comum

Subtipos:

- prazo indeterminado;
- experiência;
- prazo determinado.

Datas aparecem dinamicamente conforme o subtipo.

### CLT intermitente

- fluxo próprio;
- data de admissão;
- valor/hora;
- jornada/regra própria.

### Sem vínculo

- natureza/subtipo selecionado em cadastro mestre;
- formulário condicional por categoria;
- início/vigência da relação em vez de linguagem de admissão quando inadequado;
- nomenclatura não deve transformar categoria de software em parecer jurídico.

### Ciclo de vida do vínculo

```text
RASCUNHO
PENDENTE
PROGRAMADO
ATIVO
AFASTADO
ENCERRADO
```

Pessoa, vínculo, conta e biometria possuem estados diferentes.

## 2.5 Etapa 4 — Pagamento

- forma principal configurável: conta bancária, conta-salário, PIX ou outra forma permitida pela empresa;
- campos bancários estruturados;
- titularidade própria é padrão;
- terceiro é excepcional, com justificativa, revisão, histórico e auditoria;
- PIX possui tipo de chave estruturado, validação de formato e titularidade;
- não afirmar verificação bancária real sem integração correspondente;
- comprovante bancário é opcional, restrito, auxiliar e vinculado à versão dos dados.

Estados:

```text
INCOMPLETO
PENDENTE_DE_VALIDACAO
VERIFICADO
INCONSISTENTE
INATIVO
```

Qualquer alteração relevante retorna o dado a estado que exija nova validação quando aplicável.

## 2.6 Etapa 5 — Acesso ao sistema

Regra padrão:

```text
FUNCIONARIO != CONTA_DE_USUARIO
DEFAULT_ACCOUNT=NAO_CRIADA
```

- funcionário não recebe acesso administrativo automaticamente;
- conta só é criada quando necessária;
- inicia como convite pendente;
- o próprio usuário ativa sua credencial;
- RH não define senha permanente;
- perfis canônicos existentes: `super_admin`, `admin`, `manager`, `operator`, `auditor`;
- mostrar resumo de permissões efetivas;
- não criar checkboxes de permissões individuais no onboarding;
- perfil = o que pode fazer;
- escopo = onde pode fazer;
- transferência deve revisar escopo;
- desligamento programa/desativa conta conforme política;
- readmissão não reativa conta antiga automaticamente.

Estados:

```text
NAO_CRIADA
CONVITE_PENDENTE
ATIVA
BLOQUEADA_TEMPORARIAMENTE
DESATIVACAO_PROGRAMADA
DESATIVADA
```

## 2.7 Etapa 6 — Biometria

- cadastrar agora ou depois;
- adiar biometria não bloqueia onboarding quando a política permitir;
- usuário sem `biometrics:manage` não recebe CTA proibido nem CTA apenas desabilitado;
- fluxo normal usa câmera ao vivo;
- multiquadro;
- validação guiada de qualidade;
- não usar upload, galeria ou foto administrativa como captura biométrica normal;
- frames brutos são temporários e descartados após processamento;
- template biométrico protegido/criptografado, versionado e auditável;
- template não é conteúdo comum para download/visualização pela UI;
- re-enrollment cria nova versão; não sobrescreve silenciosamente;
- aviso de transparência é obrigatório antes da câmera;
- registrar versão/data/hora/ator do aviso;
- não rotular automaticamente o aviso como “consentimento LGPD”;
- base legal e retenção dependem de validação especializada;
- conflito de unicidade biométrica bloqueia ativação automática e permite recaptura/revisão autorizada;
- conflito biométrico não equivale a fraude confirmada;
- desligamento inativa uso;
- readmissão não reativa biometria automaticamente.

Estados:

```text
NAO_CADASTRADA
PENDENTE
EM_CADASTRO
ATIVA
COM_PROBLEMA
INATIVA
```

Estados de captura:

```text
AGUARDANDO_CAMERA
CAPTURANDO
VALIDANDO_QUALIDADE
PROCESSANDO
SUCESSO
FALHA
```

## 2.8 Etapa 7 — Revisão e conclusão

- revisão consolidada é obrigatória;
- cada seção possui resumo + ação `Editar`;
- erro bloqueante impede conclusão;
- pendência administrativa pode permitir conclusão quando a regra correspondente permitir;
- informação opcional ausente não bloqueia;
- `Concluir cadastro` existe **somente** na Etapa 7;
- matrícula é gerada/reservada na confirmação final;
- operação futura deve ser transacional e idempotente;
- duplo clique/retry não pode criar pessoa, vínculo ou matrícula duplicados;
- falha obrigatória deve preservar o formulário e evitar estado parcial;
- sucesso mostra matrícula, status, pendências e próximas ações.

## 2.9 Rascunho persistente

- autosave + `Salvar e sair` + retomada;
- rascunho não é funcionário ativo;
- não possui matrícula definitiva;
- não possui vínculo ativo;
- não aparece em ponto/relatórios como funcionário ativo;
- não ativa convite nem biometria operacional;
- biometria eventualmente capturada em rascunho permanece staged/não operacional;
- descarte exige confirmação;
- descarte e limpeza futura devem ser auditáveis;
- retenção de rascunhos será política posterior.

---

# 3. Shell administrativo canônico

A correção estrutural aprovada elimina excesso de estrutura permanente.

```text
SIDEBAR COMPACTAVEL
+
TOP HEADER
+
BREADCRUMB / PAGE HEADER
+
STEPPER HORIZONTAL quando houver wizard
+
GRANDE AREA DE TRABALHO
+
DRAWER CONTEXTUAL SOB DEMANDA
```

Estrutura:

```text
AppShell
├─ CollapsibleSidebar
├─ TopHeader
└─ MainWorkspace
   ├─ Breadcrumb
   ├─ PageHeader
   └─ Conteudo da tela
```

O mesmo shell deve governar Dashboard, Funcionários, Empresas/Obras, Registros, Saúde, Eventos/Logs e Configurações.

`/punch` permanece fora do shell administrativo.

---

# 4. Política oficial de dimensionamento

```text
DIMENSIONING_POLICY=FROZEN
```

- `rem` = unidade-base para tipografia, espaçamento, controles e ícones;
- `fr` + `minmax()` = distribuição de grid;
- `clamp()` = crescimento fluido com limite mínimo/máximo;
- `vw`/`dvh` = somente quando relação com viewport fizer sentido e preferencialmente com limites;
- Container Queries e `cqi` = adaptação do componente ao espaço que ele realmente recebe;
- `ch` = limite de leitura textual;
- `%` = relações locais específicas;
- `px` = exceções técnicas, como borda de 1px, quando necessário.

Breakpoints 360/768/1024/1440 são **alvos de teste**, não quatro interfaces rígidas.

Princípio:

```text
RESPONSIVO != DIMINUIR_TUDO
RESPONSIVO = REORGANIZAR + REDISTRIBUIR + LIMITAR + EXPANDIR + COLAPSAR
```

---

# 5. Componentes estruturais congelados

## 5.1 CollapsibleSidebar

```text
COLLAPSIBLE_SIDEBAR=FROZEN
```

- desktop possui expandida e compacta;
- compacta funcional em torno de `4.5rem`;
- expandida deve usar largura fluida limitada, não valor rígido universal;
- não desaparece totalmente no desktop;
- largura liberada vai imediatamente para o conteúdo;
- estado escolhido persiste entre telas;
- item ativo continua inequívoco no modo compacto;
- indicador ativo não depende apenas de cor;
- tooltip obrigatório no modo compacto;
- grupos de navegação aparecem por texto na expandida e por separação espacial na compacta;
- botão de expandir/recolher é explícito;
- 1440+: escolha expandida/compacta;
- ~1024: compacta por padrão/preferência;
- ~768: compacta e expansão overlay;
- ~360: menu overlay, sem coluna permanente de 4.5rem;
- `aria-expanded`, `aria-current`, foco visível, Enter/Space e alvos adequados.

## 5.2 HorizontalStepper

```text
HORIZONTAL_STEPPER=FROZEN
```

- substitui completamente a coluna vertical de etapas;
- oito ícones intuitivos como linguagem visual principal;
- nomes das etapas não ficam permanentemente dentro da barra;
- título completo da etapa aparece abaixo/fora do stepper;
- manter `Etapa X de 8`;
- tooltip desktop + `aria-label` + texto visualmente oculto;
- concluída, atual, futura, erro e `NEEDS_REVIEW` têm estados distintos e não dependem só de cor;
- etapa concluída pode ser revisitada;
- etapa futura não pode ser pulada se pré-requisitos não permitirem;
- mobile usa progresso simplificado e pode abrir `Ver etapas` em lista textual sob demanda.

Vocabulário conceitual:

```text
0 Tipo de relação
1 Dados pessoais
2 Endereço
3 Vínculo
4 Pagamento
5 Acesso
6 Biometria
7 Revisão
```

Em produção, usar ícones da família oficial, não emojis.

## 5.3 ContextDrawer

```text
CONTEXT_DRAWER=FROZEN
```

- substitui painel direito fixo;
- fechado por padrão;
- abre sob demanda;
- não reduz permanentemente a largura do formulário;
- desktop largo: drawer lateral;
- tablet/mobile: overlay;
- contém resumo, contexto, pendências, permissões e ajuda curta;
- não contém campos editáveis obrigatórios;
- pode possuir atalho `Ir para ...`;
- abrir/fechar nunca perde formulário;
- Escape fecha;
- foco retorna ao trigger;
- overlay gerencia foco adequadamente;
- largura segue política fluida, sem número rígido congelado antes da validação visual.

## 5.4 StickyFormActions

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

Regras:

- uma única ação primária;
- `Voltar` não é renderizado na primeira etapa quando não houver destino anterior;
- `Concluir cadastro` não é renderizado antes da Etapa 7;
- `Descartar` fica visualmente separado e exige confirmação;
- autosave mostra status discreto (`Salvando...`, `Salvo`, falha);
- barra não cobre campos;
- mobile reorganiza, não espreme;
- teclado virtual ativa modo seguro; pode deixar de ser sticky se necessário;
- usar `dvh`, safe-area, scroll padding e scroll-to-field quando aplicável.

## 5.5 ResponsiveFormGrid

```text
RESPONSIVE_FORM_GRID=FROZEN
```

- `fr`, `minmax`, container queries;
- 1 coluna quando necessário;
- 2–3 colunas quando houver espaço real;
- largura do campo deve sugerir o tipo de informação;
- não usar larguras rígidas por campo;
- formulário possui limite confortável de edição/leitura em monitores muito grandes;
- ordem DOM permanece lógica e não é reordenada artificialmente por CSS.

## 5.6 FormSection + Progressive Disclosure

```text
FORM_SECTION_PROGRESSIVE_DISCLOSURE=FROZEN
```

- informação principal sempre visível;
- conteúdo secundário pode recolher;
- conteúdo condicional aparece conforme resposta;
- abrir/fechar preserva estado;
- recolher não apaga dados;
- seção fechada com erro deve indicar o problema e pode abrir automaticamente;
- informação obrigatória não pode ficar escondida sem contexto.

## 5.7 FieldGroup / Validation

```text
FIELD_GROUP=FROZEN
```

- label permanente;
- placeholder apenas como exemplo;
- ajuda curta quando agrega valor;
- ajuda avançada sob demanda;
- estados padronizados: normal, focus, preenchido, validando, válido, atenção, erro, disabled, read-only;
- validação local separada da validação remota;
- remote validation não dispara a cada tecla;
- sucesso visual somente quando informa algo relevante;
- mensagens explicam como corrigir;
- resumo de erros da etapa;
- foco no primeiro erro;
- máscaras tolerantes;
- normalização antes de validar/persistir;
- teclado/input/autocomplete adequados ao dado;
- `aria-describedby` e associação correta;
- não depender apenas de cor.

Padrão obrigatório/opcional:

- campo ativo é obrigatório por padrão quando o contrato assim definir;
- opcional recebe texto `(opcional)`;
- condicional explica sua condição;
- semântica HTML usa `required`/`aria-required` quando aplicável.

## 5.8 SearchableCombobox / EntityPicker

```text
ENTITY_PICKER=FROZEN
```

- cadastro mestre selecionado por ID;
- busca tolera caixa, acentos e termos parciais;
- resultados ambíguos mostram contexto;
- somente entidades autorizadas aparecem na própria pesquisa;
- novos vínculos selecionam entidades ativas;
- histórico preserva entidade antiga/inativa;
- rascunho retomado detecta entidade que ficou inativa;
- não apagar seleção silenciosamente;
- dependências Empresa → Unidade → Setor → Gestor etc.;
- troca de entidade estrutural revalida dependências;
- loading, empty e error são estados diferentes;
- debounce em busca remota;
- respostas assíncronas obsoletas não podem substituir as novas;
- paginação/virtualização quando catálogos crescerem;
- não autoselecionar só porque existe um resultado;
- teclado completo e padrão ARIA apropriado;
- mobile pode usar superfície de seleção maior;
- não criar entidade improvisada dentro do onboarding sem fluxo administrativo autorizado.

## 5.9 Date / Time / Period

```text
DATE_TIME_PERIOD_PICKER=FROZEN
```

Variantes pequenas:

```text
DateField
TimeField
DateTimeField
DateRange
```

- digitação + seletor visual;
- datas civis exibidas regionalmente e armazenadas estruturadamente;
- `DATE != DATETIME`;
- data civil não recebe timezone arbitrário;
- timestamps reais tratam timezone adequadamente;
- períodos validam início/fim;
- período aberto é permitido quando o domínio permitir;
- não inventar data final fictícia na UI;
- regras passado/futuro dependem do significado do campo;
- botão Hoje somente quando útil;
- não preencher hoje silenciosamente;
- navegação rápida por mês/ano;
- acessível por teclado e adaptável ao mobile.

---

# 6. RC transversal — lacunas críticas fechadas

```text
CRITICAL_GAPS_CLOSED=6/6
CRITICAL_GAPS_OPEN=0
```

## 6.1 Wizard State Controller

Estados globais coordenam os componentes; nenhum componente decide sozinho a situação geral.

Estados relevantes incluem:

```text
EDITING
LOCAL_CHANGES
SAVING
SAVED
SAVE_ERROR
OFFLINE_TEMPORARY
CONFLICT
VALIDATING_STEP
REVIEW
SUBMITTING
OUTCOME_UNKNOWN
SUCCESS
```

Etapas possuem:

```text
FUTURE
CURRENT
VALID
ERROR
NEEDS_REVIEW
```

## 6.2 Draft / Version Conflict

- draft possui identidade e revisão conceitual (`draft_id`, `revision`, `last_saved_at`);
- duas abas/dois usuários não usam last-write-wins silencioso;
- versão antiga não sobrescreve nova;
- conflito pausa autosave;
- dados locais são preservados temporariamente;
- conclusão é bloqueada enquanto o conflito não for resolvido;
- não fazer merge automático silencioso.

## 6.3 Dependency Invalidation

Alteração estrutural:

```text
calcular impacto
→ informar usuário
→ confirmar mudança
→ preservar dados compatíveis
→ retirar dados incompatíveis do estado ativo
→ marcar etapas afetadas NEEDS_REVIEW
```

Nenhum reset total indiscriminado.

## 6.4 Conditional Data Lifecycle

Estados conceituais:

```text
VISIBLE_ACTIVE
HIDDEN_RETAINED
CLEARED
```

Campo oculto não participa automaticamente do payload ativo. Retenção temporária pode permitir desfazer a mudança quando seguro.

## 6.5 Submit Outcome Reconciliation

- conclusão futura usa `submission_id`/chave idempotente;
- duplo clique é bloqueado;
- timeout não significa automaticamente falha;
- `OUTCOME_UNKNOWN` exige reconciliação antes de novo submit;
- success somente após confirmação;
- retry não pode duplicar cadastro.

## 6.6 Runtime Permission Revalidation

- permissão é revalidada em ações sensíveis, salvamento restrito e submit;
- permissão alterada durante o fluxo é tratada;
- ação proibida desaparece da UI;
- conteúdo restrito não vaza em mensagens;
- preservar o máximo possível dos dados permitidos.

---

# 7. RC transversal — lacunas altas fechadas

```text
HIGH_GAPS_CLOSED=9/9
HIGH_GAPS_OPEN=0
```

## 7.1 Browser navigation

- refresh mantém draft e mesma etapa;
- back/forward respeitam histórico do wizard;
- não cria novo draft;
- navigation guard só aparece com risco real de perda;
- link direto para etapa futura respeita pré-requisitos.

## 7.2 Session expiration recovery

- sessão expirada interrompe operação protegida;
- draft permanece identificável;
- login novamente → revalidar identidade, permissão e revisão → retomar;
- conflito de versão e mudança de permissão continuam valendo;
- frames biométricos brutos não entram em recuperação local genérica.

## 7.3 Stepper discoverability

- icon-first permanece;
- `Ver etapas` fornece lista textual sob demanda;
- estados concluída/atual/futura/erro/needs-review têm semântica textual/acessível.

## 7.4 App context vs form company

```text
APP_CONTEXT != EMPRESA_DO_VINCULO
```

- header informa contexto em que o administrador está operando;
- formulário informa empresa contratante do vínculo;
- trocar contexto do header nunca altera silenciosamente o draft;
- opção fora do escopo nem aparece no seletor.

## 7.5 Required / optional

Padrão descrito em `FieldGroup`: opcional explícito, obrigatório por contrato/semântica, condicional explicado.

## 7.6 Error hierarchy

Hierarquia:

```text
SISTEMA/WIZARD
  ↓
ETAPA
  ↓
SECAO
  ↓
CAMPO
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

Erro crítico não é comunicado somente por toast.

## 7.7 Step focus management

- avançar/voltar/navegar para etapa move foco programaticamente para heading da etapa;
- leitor anuncia `Etapa X de 8 — Nome`;
- erro múltiplo anuncia resumo e leva ao primeiro erro quando apropriado;
- `prefers-reduced-motion` respeitado.

## 7.8 Mobile keyboard safe actions

- teclado virtual não pode cobrir campo ativo ou ações essenciais;
- sticky pode reorganizar ou voltar ao fluxo normal temporariamente;
- `dvh`, safe area, scroll padding e scroll-to-field devem ser considerados.

## 7.9 Date/Time/Period

Contrato consolidado no componente canônico acima.

---

# 8. RC transversal — lacunas médias fechadas

```text
MEDIUM_GAPS_CLOSED=6/6
MEDIUM_GAPS_OPEN=0
```

## 8.1 Design Tokens

### Tipografia

```text
font-family: Manrope
body: 1rem
small: 0.875rem
large: 1.125rem
heading-sm: 1.25rem
heading-md: 1.5rem
heading-lg: clamp(1.75rem, valor fluido, 2.25rem)
```

### Espaçamento

```text
space-1: .25rem
space-2: .5rem
space-3: .75rem
space-4: 1rem
space-6: 1.5rem
space-8: 2rem
```

### Raios

```text
radius-sm: .5rem
radius-md: .75rem
radius-lg: 1rem
radius-pill: pill/full
```

### Cores institucionais de referência

```text
verde-profundo: #0B3D2B
verde-base: #1B3D2A
verde-suave: #E8F0EB
dourado: #D4AF37
grafite: #2B2B2B
fundo: #F6F8F5
texto-secundario: #68736D
borda: #DDE4DF
```

Estados semânticos permanecem independentes da marca:

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

Regra:

```text
VERDE_DA_MARCA != HEALTHY
TELEMETRY_UNAVAILABLE != HEALTHY
DEGRADED != DOWN
OFFLINE != ERROR
NOT_IMPLEMENTED != ERROR
```

Contraste final deve ser verificado sobre combinações reais; não declarar conformidade apenas por intenção.

## 8.2 Icon System

```text
ICON_SYSTEM=FROZEN
FAMILY=LUCIDE
STYLE=SVG_MONOLINE
EMOJI_PRODUCTION=NO
MIX_ICON_FAMILIES=NO
```

- decorativo → `aria-hidden`;
- ação → `aria-label`;
- estado/informação → texto acessível + ícone;
- ícone não é significado único.

## 8.3 Motion

```text
FAST=120ms
NORMAL=180ms
SLOW=240ms
```

Motion serve a transições funcionais. Animação contínua/decorativa/pulsante sem necessidade é proibida. `prefers-reduced-motion` remove movimento não essencial sem remover informação.

## 8.4 Semantic DOM Order

```text
READING_ORDER = FOCUS_ORDER = TASK_LOGIC
```

CSS não pode reordenar semanticamente campos só para acomodar grid responsivo.

## 8.5 Toast Policy

```text
TOAST = feedback secundario/transitorio
BANNER_OR_ERRORSTATE = problema persistente/importante
MODAL = decisao que exige confirmacao
```

Toast não pode ser a única superfície para conflito, sessão, submit desconhecido, permissão removida ou erro crítico.

## 8.6 Catálogo global de componentes

Componentes canônicos mínimos:

```text
AppShell
CollapsibleSidebar
TopHeader
Breadcrumb
PageHeader
HorizontalStepper
ContextDrawer
StatusBadge
HealthCard
MetricCard
DataTable
Search
FilterBar
EmptyState
ErrorState
Skeleton
DegradationBanner
EventTimeline
DetailDrawer
ConfirmationModal
Toast
Pagination
LastUpdated
FormField / FieldGroup
ResponsiveFormGrid
FormSection
EntityPicker
DateField / DateRange / TimeField / DateTimeField
Button
IconButton
StickyFormActions
Tabs
Tooltip
CameraPanel
PunchResult
```

Todos herdam estados globais quando aplicável:

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

### CameraPanel

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

No onboarding biométrico: câmera ao vivo, sem galeria/upload no fluxo normal.

### PunchResult

A experiência do funcionário é simples:

```text
Funcionou?
Por que não funcionou?
O que fazer agora?
```

Não expor logs/códigos técnicos na superfície principal do funcionário.

---

# 9. Acessibilidade e responsividade canônicas

- teclado completo: Tab/Shift+Tab, Enter/Space quando aplicável;
- foco visível sempre;
- `aria-current`, `aria-expanded`, `aria-controls`, `aria-describedby` conforme componente;
- foco de drawer/modal retorna ao disparador;
- target interativo adequado, equivalente a aproximadamente 44 CSS px sem transformar esse número em unidade-base do Design System;
- zoom/reflow a 200% sem perda funcional;
- leitor de tela em wizard, modal/drawer, erros e PunchResult;
- cor nunca é única fonte de estado;
- reduced motion;
- linguagem curta e direta;
- tooltips não guardam informação obrigatória;
- mobile não depende de hover;
- 360/768/1024/1440 são cenários mínimos de validação, além de larguras intermediárias e container queries;
- orientação e teclado virtual devem ser testados onde relevantes.

---

# 10. Contrato de testes futuro

A NF-01 especifica. A NF-02/fases posteriores implementam e executam.

Linha de montagem:

```text
REQUISITO
→ DESIGN
→ ARQUITETURA
→ IMPLEMENTACAO
→ UNITARIO
→ INTEGRACAO
→ CONTRATO
→ REGRESSAO
→ RESPONSIVO/UX/A11Y
→ SEGURANCA
→ EVIDENCIA
→ GATE
```

## 10.1 Unitários

Cobrir, quando implementados:

- CollapsibleSidebar: expanded/collapsed/persistência/ativo;
- HorizontalStepper: current/completed/future/error/needs-review;
- ContextDrawer: open/close/context/focus;
- StickyFormActions: ações por etapa, loading e ausência do CTA final antes da revisão;
- ResponsiveFormGrid: comportamento sem depender de pixels exatos;
- FormSection: condicional/aberto/fechado/erro;
- FieldGroup: validação, ajuda, erro, aria;
- EntityPicker: busca, dependência, respostas obsoletas, RBAC, estado inativo;
- Date/Time: parsing, normalização, limites, início/fim;
- Wizard State: transições, dirty/saving/saved/error/conflict;
- Dependency Invalidation;
- Conditional Data Lifecycle;
- Submit Reconciliation;
- Runtime Permission Revalidation.

## 10.2 Integração

Cobrir:

- avançar/voltar sem perda;
- revisitar etapa concluída;
- invalidar etapa posterior após mudança estrutural;
- autosave e retomada;
- duas abas;
- dois administradores;
- refresh/back/forward;
- sessão expirada;
- queda e retorno de rede;
- mudança de permissão durante o wizard;
- contexto global diferente da empresa do vínculo;
- campo condicional escondido não persistido como ativo;
- submit final idempotente;
- timeout → `OUTCOME_UNKNOWN` → reconciliação;
- biometria agora/depois e RBAC;
- drawer → atalho para etapa → formulário preservado.

## 10.3 Responsivo

Validar 360/768/1024/1440 **e larguras intermediárias**:

- sem overflow indevido;
- sidebar/context drawer/stepper coerentes;
- mobile keyboard safe;
- formulários reorganizados, não espremidos;
- ordem DOM/foco preservada;
- zoom 200%;
- container resize independente do viewport quando o componente usar container query.

## 10.4 Acessibilidade

- teclado;
- foco;
- screen reader;
- labels;
- aria;
- contraste real;
- reduced motion;
- erros;
- tooltips;
- camera states;
- PunchResult.

---

# 11. Impacto sobre os artefatos existentes

## Preservar conteúdo/regras

```text
Dashboard V3................ conteúdo aprovado, shell deve ser reconciliado
Funcionarios Desktop V1..... conteúdo aprovado, shell deve ser reconciliado
Novo Funcionario V1......... histórico/comparação
Novo Funcionario V2......... contrato funcional preservado, shell/UX espacial deve ser revisado
```

## Substituições de direção

```text
sidebar sempre expandida.................. SUPERSEDED
stepper vertical no Novo Funcionario...... SUPERSEDED
painel contextual direito permanente...... SUPERSEDED
larguras rigidamente congeladas em px..... SUPERSEDED como politica geral
emoji como iconografia de producao........ SUPERSEDED
```

Não apagar protótipos históricos apenas para esconder evolução; marcar claramente qual direção é canônica.

---

# 12. Estado da RC transversal

```text
RC_TRANSVERSAL=COMPLETE
CRITICAL_OPEN=0
HIGH_OPEN=0
MEDIUM_OPEN=0
RETRABALHO_ESTRUTURAL=NO
CROSS_COMPONENT_CONTRACTS=FROZEN
```

Isso **não encerra a NF-01**.

Ainda faltam:

```text
reconciliar wireframes sob o shell canônico
atualizar Dashboard
atualizar Funcionários
atualizar Novo Funcionário
validar coerência visual
validar responsividade/a11y do Design Lab
atualizar evidências
revisão independente
Gate humano final de LEANDRO
```

---

# 13. Próxima sequência oficial

```text
1. Este registro canônico entra no repositório
2. Documentos contraditórios são reconciliados
3. Wireframe do shell canônico é consolidado
4. Dashboard é reconciliado
5. Funcionários é reconciliado
6. Novo Funcionário é reconciliado
7. Coerência entre telas é validada
8. Plano de implementação da NF-02 é apresentado
9. Implementação somente após gate correspondente
```

---

# 14. Gate e proibições finais

```text
FINAL_HUMAN_GATE=NOT_READY
PR_32_MERGE=BLOCKED_UNTIL_EXPLICIT_APPROVAL
NF02=NOT_STARTED
```

Não fazer merge por consequência deste documento.

Não declarar conformidade trabalhista, regulatória ou de proteção de dados.

Não transformar decisão de UX em alteração de backend sem fase e autorização próprias.

---

# 15. Regra contra esquecimento

Antes de propor qualquer mudança futura na NF-01 ou iniciar a NF-02, verificar explicitamente:

```text
DECISOES_CONGELADAS.md
+
12_NF01_CANONICAL_DECISIONS_2026-08-11.md
+
estado real atual do GitHub/PR
```

Se uma proposta contrariar este documento, deve ser tratada como **mudança de decisão**, nunca como continuação silenciosa.
