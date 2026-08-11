# Novo Funcionário — UX Specification Canônica da NF-01

## Estado

```text
PHASE=NF01_UX_UI_NEW_EMPLOYEE
FUNCTIONAL_CONTRACT=FROZEN
STRUCTURAL_CONTRACT=FROZEN
RC_TRANSVERSAL=COMPLETE
IMPLEMENTATION_SCOPE=PROTOTYPE_ONLY
PRODUCTION_CODE_CHANGED=NO
BACKEND_CHANGED=NO
NF02_STARTED=NO
MERGE_AUTHORIZED=NO
HUMAN_VISUAL_AUDIT=PENDING
```

> **Fonte canônica integral:** `../12_NF01_CANONICAL_DECISIONS_2026-08-11.md`.
>
> Este arquivo especifica como o Design Lab deve materializar o onboarding. Se houver conflito com uma versão antiga deste documento/protótipo, prevalece o registro canônico.

---

# 1. Princípio do fluxo

O cadastro funciona como uma linha de montagem:

```text
0 Tipo de relação
  ↓
1 Dados pessoais
  ↓
2 Endereço
  ↓
3 Vínculo
  ↓
4 Pagamento
  ↓
5 Acesso ao sistema
  ↓
6 Biometria
  ↓
7 Revisão e conclusão
```

Uma ação executada não significa automaticamente conclusão válida. Cada etapa possui validação, estado e dependências.

---

# 2. Shell canônico

A direção antiga com stepper vertical e painel contextual fixo está substituída.

```text
┌───────┬──────────────────────────────────────────────────────────────┐
│ SIDE  │ TOP HEADER                                                   │
│ BAR ↔ ├──────────────────────────────────────────────────────────────┤
│       │ Breadcrumb / PageHeader                       [ℹ Resumo]    │
│       │                                                             │
│       │ ○  ●  ○  ○  ○  ○  ○  ○        Etapa X de 8 [Ver etapas]  │
│       │                                                             │
│       │ TÍTULO DA ETAPA                                             │
│       │ descrição curta                                             │
│       │                                                             │
│       │                   FORMULÁRIO                                │
│       │                                                             │
│       ├─────────────────────────────────────────────────────────────┤
│       │ Descartar | Salvar e sair | Voltar | Continuar             │
└───────┴──────────────────────────────────────────────────────────────┘
```

Componentes:

```text
AppShell
CollapsibleSidebar
TopHeader
Breadcrumb
PageHeader
HorizontalStepper
ResponsiveFormGrid
FormSection
FieldGroup
EntityPicker
Date/Time components
ContextDrawer
StickyFormActions
```

---

# 3. Regras globais do wizard

- uma etapa principal por vez;
- avançar/voltar sem perda de dados;
- etapas concluídas revisitam;
- futuras não pulam pré-requisitos;
- `Etapa X de 8` sempre disponível;
- `Ver etapas` oferece versão textual sob demanda;
- `Concluir cadastro` só é renderizado na Etapa 7;
- matrícula só é gerada/reservada na conclusão futura;
- rascunho persistente;
- `Salvar e sair`;
- autosave verificável;
- draft != funcionário ativo;
- mudança estrutural pode marcar etapas posteriores `NEEDS_REVIEW`;
- app context do header != empresa contratante do vínculo;
- permissão pode ser revalidada durante o fluxo;
- erro crítico não depende somente de toast;
- Design Lab não envia dados ao backend.

---

# 4. Estado global

Estados do wizard:

```text
EDITING
LOCAL_CHANGES
SAVING
SAVED
SAVE_ERROR
CONFLICT
VALIDATING_STEP
REVIEW
SUBMITTING
OUTCOME_UNKNOWN
SUCCESS
```

Estados por etapa:

```text
FUTURE
CURRENT
VALID
ERROR
NEEDS_REVIEW
```

Autosave:

```text
Salvando...
Salvo
Alterações ainda não salvas
Falha ao salvar
Sem conexão — alterações ainda não confirmadas no servidor
```

O protótipo pode simular esses estados, mas deve marcar claramente que não existe persistência real de produção.

---

# 5. HorizontalStepper

```text
HORIZONTAL_STEPPER=FROZEN
```

Visualmente:

- icon-first;
- sem nomes permanentes dentro da barra;
- nomes completos em tooltip/lista textual e heading da etapa;
- ícones finais da família Lucide;
- emojis somente como anotação de wireframe.

Semântica:

- `aria-label`;
- texto visualmente oculto;
- `aria-current="step"`;
- completed/current/future/error/needs-review diferenciados sem depender apenas de cor.

Mobile:

- não comprimir oito ícones até ficarem inutilizáveis;
- progresso simplificado;
- `Ver etapas` abre sheet/drawer textual.

---

# 6. ContextDrawer

```text
CONTEXT_DRAWER=FROZEN
```

Conteúdo permitido:

- nome/rascunho;
- tipo de relação;
- etapa atual;
- empresa/unidade/setor quando definidos;
- pendências;
- resumo de permissões quando relevante;
- ajuda curta;
- links `Ir para ...`.

Conteúdo proibido:

- campos obrigatórios editáveis;
- ação primária do onboarding;
- conteúdo que reduza permanentemente a área útil.

Comportamento:

- fechado por padrão;
- desktop lateral sob demanda;
- tablet/mobile overlay;
- Escape fecha;
- foco retorna ao trigger;
- abrir/fechar preserva formulário.

---

# 7. StickyFormActions

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
- Voltar ausente na etapa inicial quando não houver destino;
- Descartar separado + confirmação;
- loading bloqueia duplo clique;
- validação inválida mantém etapa e leva ao primeiro erro;
- mobile reorganiza;
- teclado virtual não pode cobrir campo/ação; barra pode deixar de ser sticky temporariamente.

---

# 8. Form layout

## ResponsiveFormGrid

```text
RESPONSIVE_FORM_GRID=FROZEN
```

- `fr`/`minmax()`;
- container queries;
- 1–3 colunas conforme espaço;
- largura semântica;
- limite confortável de edição;
- sem larguras rígidas por campo;
- ordem DOM lógica.

## FormSection

```text
FORM_SECTION_PROGRESSIVE_DISCLOSURE=FROZEN
```

- principal sempre visível;
- secundário recolhível;
- condicional por resposta;
- recolher não apaga;
- erro em seção fechada fica sinalizado.

## FieldGroup

```text
FIELD_GROUP=FROZEN
```

- label permanente;
- placeholder somente exemplo;
- help text curto;
- ajuda avançada sob demanda;
- estados normal/focus/filled/validating/valid/warning/error/disabled/readonly;
- local validation != remote validation;
- erro explica correção;
- máscara tolerante + normalização;
- input mode/autocomplete;
- `aria-describedby`;
- opcional marcado `(opcional)`.

---

# 9. EntityPicker

```text
ENTITY_PICKER=FROZEN
```

Usado em:

- empresa;
- unidade;
- setor;
- cargo/função;
- gestor;
- jornada;
- escala quando aplicável;
- banco;
- subtipos/cadastros mestres.

Regras:

- salvar ID;
- busca tolerante;
- contexto em nomes ambíguos;
- RBAC na consulta;
- ativo/inativo;
- draft detecta entidade inativada;
- dependências entre pickers;
- loading/empty/error separados;
- debounce;
- resposta antiga não substitui nova;
- não autoselecionar resultado único;
- sem criação improvisada inline;
- teclado/ARIA.

---

# 10. Date / Time / Period

```text
DATE_TIME_PERIOD_PICKER=FROZEN
```

Variantes:

```text
DateField
TimeField
DateTimeField
DateRange
```

- digitação + seletor;
- data civil sem timezone arbitrário;
- timestamp real com timezone quando aplicável;
- início/fim relacionados;
- período aberto quando permitido;
- sem data fictícia de término;
- passado/futuro contextual;
- Hoje não preenche silenciosamente;
- acessível/mobile.

---

# 11. Etapa 0 — Tipo de relação

```text
( ) CLT comum
( ) CLT intermitente
( ) Sem vínculo empregatício
( ) Outros [cadastro mestre]
```

- sem texto livre improvisado para categoria mestre;
- decisão muda campos posteriores;
- alterar depois pode exigir `NEEDS_REVIEW`;
- classificação do software não é conclusão jurídica.

---

# 12. Etapa 1 — Dados pessoais

## Identificação

- Nome completo — obrigatório;
- CPF — obrigatório;
- Data de nascimento — obrigatória;
- RG — opcional;
- foto administrativa — opcional/separada da biometria.

## Dados civis

- sexo;
- raça/cor autodeclarada;
- instrução;
- nacionalidade;
- país de nascimento;
- estado civil opcional;
- naturalidade opcional;
- nome social opcional/condicional.

## Contatos

- telefone principal obrigatório operacionalmente;
- WhatsApp opcional;
- e-mail opcional;
- contato de recados/emergência obrigatório em pelo menos uma função.

## Complementares

- dependentes condicionais;
- PcD/reabilitação restrito/condicional;
- estrangeiro abre campos específicos;
- anexos opcionais.

## Integridade

- CPF duplicado bloqueia nova pessoa;
- nome+nascimento semelhante apenas alerta;
- readmissão reutiliza pessoa + novo vínculo.

---

# 13. Etapa 2 — Endereço

- país primeiro, Brasil padrão;
- Brasil/exterior;
- urbano/rural;
- CEP urbano + lookup/fallback/manual edit;
- rural pode não ter CEP;
- um endereço residencial vigente por padrão;
- histórico/vigência/auditoria preservados.

---

# 14. Etapa 3 — Vínculo

- empresa contratante;
- matrícula automática na conclusão;
- unidade base;
- setor/departamento;
- cargo/função;
- gestor;
- jornada/horário;
- jornada != escala;
- remuneração contratual nesta etapa;
- benefícios habituais nesta etapa;
- CLT comum com subtipos;
- CLT intermitente com fluxo próprio;
- sem vínculo com natureza via cadastro mestre;
- lifecycle: RASCUNHO/PENDENTE/PROGRAMADO/ATIVO/AFASTADO/ENCERRADO.

---

# 15. Etapa 4 — Pagamento

- forma configurável;
- conta/conta-salário/PIX etc.;
- titularidade própria padrão;
- terceiro excepcional com justificativa/revisão;
- PIX estruturado;
- estados INCOMPLETO/PENDENTE_DE_VALIDACAO/VERIFICADO/INCONSISTENTE/INATIVO;
- comprovante opcional/restrito.

---

# 16. Etapa 5 — Acesso

```text
DEFAULT_ACCOUNT=NAO_CRIADA
FUNCIONARIO != USUARIO_ADMINISTRATIVO
```

- convite pendente;
- usuário ativa credencial;
- RH não define senha permanente;
- perfis canônicos: super_admin/admin/manager/operator/auditor;
- resumo de permissões;
- perfil != escopo;
- sem checkboxes individuais de permissão no onboarding.

---

# 17. Etapa 6 — Biometria

- agora ou depois;
- RBAC `biometrics:manage`;
- câmera ao vivo;
- multiquadro;
- qualidade;
- sem upload/galeria/foto administrativa;
- frames temporários descartados;
- template protegido/versionado;
- aviso de transparência antes da câmera;
- não rotular automaticamente como consentimento;
- conflito biométrico bloqueia ativação automática, não significa fraude;
- desligamento inativa uso;
- readmissão não reativa automaticamente.

---

# 18. Etapa 7 — Revisão

- todos os blocos resumidos com `Editar`;
- erro bloqueante vs pendência administrativa vs opcional ausente;
- `Concluir cadastro` somente aqui;
- conclusão futura transacional/idempotente;
- matrícula na confirmação;
- success mostra status/pendências/próximas ações.

---

# 19. Dependency Invalidation

Quando uma decisão estrutural muda:

```text
calcular impacto
→ informar usuário
→ confirmar
→ preservar compatível
→ remover incompatível do estado ativo
→ NEEDS_REVIEW nas etapas afetadas
```

Nada é apagado silenciosamente.

---

# 20. Conditional Data Lifecycle

```text
VISIBLE_ACTIVE
HIDDEN_RETAINED
CLEARED
```

Campo oculto pode ser preservado temporariamente no draft, mas não entra automaticamente no payload ativo.

---

# 21. Draft / Conflict

- draft_id/revision/last_saved_at conceituais;
- duas abas/dois usuários não sobrescrevem silenciosamente;
- conflito pausa autosave e bloqueia conclusão;
- dados locais preservados temporariamente;
- sessão expirada → login → revalidar identidade/permissão/revision.

---

# 22. Submit reconciliation

- chave idempotente da tentativa lógica;
- duplo clique não duplica;
- timeout pode gerar `OUTCOME_UNKNOWN`;
- verificar resultado antes de novo submit;
- success somente após confirmação.

---

# 23. Responsividade

```text
360 / 768 / 1024 / 1440 = targets de teste
```

- não layouts rígidos;
- usar rem/fr/minmax/clamp/container queries;
- mobile 1 coluna;
- stepper simplificado;
- ContextDrawer overlay;
- StickyFormActions keyboard-safe;
- zoom 200%;
- larguras intermediárias.

---

# 24. Acessibilidade

- labels persistentes;
- `fieldset/legend` onde aplicável;
- erros por `aria-describedby`;
- foco no heading após mudança de etapa;
- ErrorSummary + primeiro erro;
- `aria-current="step"`;
- estados dinâmicos anunciados sem spam;
- teclado completo;
- foco visível;
- contraste real;
- target adequado;
- reduced motion;
- ícone nunca único significado;
- tooltip não contém informação obrigatória.

---

# 25. Estratégia de testes

Unitário:

- componentes;
- transições;
- validações;
- dependency invalidation;
- conditional lifecycle;
- version conflict;
- submit reconciliation;
- runtime permission revalidation.

Integração:

- avançar/voltar;
- autosave/retomar;
- browser nav;
- duas abas/dois admins;
- sessão expirada;
- rede;
- permissão alterada;
- drawer→etapa;
- biometria agora/depois;
- submit idempotente.

Responsivo/a11y:

- 360/768/1024/1440 + intermediários;
- zoom 200%;
- teclado;
- screen reader;
- reduced motion;
- mobile keyboard safe.

---

# 26. Gate

```text
FUNCTIONAL_CONTRACT=FROZEN
STRUCTURAL_CONTRACT=FROZEN
RC_CRITICAL_OPEN=0
RC_HIGH_OPEN=0
RC_MEDIUM_OPEN=0
DESIGN_LAB_RECONCILIATION=PENDING
FINAL_HUMAN_GATE=NOT_READY
PR_32_MERGE=BLOCKED
NF02=NOT_STARTED
```
