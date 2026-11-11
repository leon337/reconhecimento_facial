# NF-01 — Estratégia Canônica de Testes e Critérios de Aceite

> **Fonte canônica complementar:** `12_NF01_CANONICAL_DECISIONS_2026-08-11.md`.

## 1. Escopo desta NF

NF-01 continua sem alterar produção.

```text
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

O que esta NF entrega é o **contrato verificável** que a implementação futura deverá transformar em testes automatizados, manuais e evidências.

---

# 2. Linha de montagem da qualidade

```text
REQUISITO
  ↓
DESIGN
  ↓
ARQUITETURA
  ↓
IMPLEMENTACAO
  ↓
UNITARIO
  ↓
INTEGRACAO
  ↓
CONTRATO
  ↓
REGRESSAO
  ↓
UX / RESPONSIVIDADE / ACESSIBILIDADE
  ↓
SEGURANCA
  ↓
EVIDENCIA
  ↓
GATE
```

Nenhuma peça passa diretamente de “desenhada” para “pronta”.

---

# 3. Critérios de aceite documentais da NF-01

| ID | Critério | Evidência |
|---|---|---|
| NF01-AC-01 | definição de produto preservada | `01_PRODUCT_DEFINITION.md` |
| NF01-AC-02 | inventário distingue real/legado/futuro | `02_UI_INVENTORY.md` |
| NF01-AC-03 | arquitetura de informação fechada | `03_INFORMATION_ARCHITECTURE.md` |
| NF01-AC-04 | RBAC atual não reinventado | `04_ROLES_PERMISSIONS_AND_STATES.md` |
| NF01-AC-05 | Design System canônico reconciliado | `05_DESIGN_SYSTEM.md` |
| NF01-AC-06 | catálogo canônico de componentes | `06_COMPONENT_CATALOG.md` |
| NF01-AC-07 | wireframes reconciliados ao shell canônico | `07_WIREFRAMES.md` |
| NF01-AC-08 | responsividade/a11y canônicas | `08_RESPONSIVE_ACCESSIBILITY.md` |
| NF01-AC-09 | contrato de testes completo | este documento |
| NF01-AC-10 | registro integral das decisões deste ciclo | `12_NF01_CANONICAL_DECISIONS_2026-08-11.md` |
| NF01-AC-11 | `DECISOES_CONGELADAS.md` inalterado | diff da PR |
| NF01-AC-12 | produção/backend/migrations inalterados | diff da PR |
| NF01-AC-13 | final human gate explícito antes de merge | PR #32 |

---

# 4. Testes unitários futuros — shell

## CollapsibleSidebar

- expanded → compact → expanded;
- persistência da preferência entre telas;
- item ativo;
- `aria-expanded`;
- tooltip no modo compacto;
- mobile overlay;
- conteúdo recupera largura sem espaço morto.

## HorizontalStepper

- `CURRENT`;
- `COMPLETED`;
- `FUTURE`;
- `ERROR`;
- `NEEDS_REVIEW`;
- `aria-current="step"`;
- `Ver etapas` textual;
- bloquear salto indevido para etapa futura.

## ContextDrawer

- open/closed;
- conteúdo contextual correto;
- Escape;
- retorno de foco;
- `aria-expanded`/`aria-controls`;
- formulário preservado.

---

# 5. Testes unitários futuros — formulários

## StickyFormActions

- etapa 0 não renderiza Voltar quando não aplicável;
- etapas 0–6 renderizam Continuar;
- etapa 7 renderiza Concluir cadastro;
- `Concluir cadastro` não existe antes da revisão;
- loading bloqueia duplo envio;
- discard exige confirmação;
- estado de autosave coerente.

## ResponsiveFormGrid

- adapta 1/2/3 colunas conforme container;
- não depende de assert de pixels rígidos salvo exceção técnica;
- ordem DOM permanece lógica.

## FormSection

- abrir/fechar;
- estado condicional;
- recolher preserva dados;
- seção fechada com erro sinaliza e abre quando necessário.

## FieldGroup

- label/ajuda/erro associados;
- local validation separada da remota;
- `VALIDATING`;
- erro específico;
- máscara tolerante/normalização;
- opcional/obrigatório/condicional;
- input mode/autocomplete.

## EntityPicker

- busca tolerante;
- seleção por ID;
- nomes ambíguos exibem contexto;
- RBAC filtra resultados;
- entidade inativa não entra em novo vínculo;
- draft detecta entidade que ficou inativa;
- dependência Empresa → Unidade → Setor;
- mudança incompatível não é silenciosa;
- debounce;
- resposta assíncrona antiga é ignorada;
- loading != empty != error;
- teclado/ARIA.

## Date/Time

- parsing;
- normalização;
- data civil sem timezone arbitrário;
- DATE != DATETIME;
- validação de início/fim;
- período aberto;
- passado/futuro contextual;
- Hoje não preenche silenciosamente.

---

# 6. Testes unitários futuros — máquina de estados

## Wizard State

Cobrir transições:

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

E estados de etapa:

```text
FUTURE
CURRENT
VALID
ERROR
NEEDS_REVIEW
```

## Draft / Version Conflict

- revision antiga não sobrescreve nova;
- autosave pausa no conflito;
- dados locais preservados;
- conclusão bloqueada;
- não há merge automático silencioso.

## Dependency Invalidation

- alterar relação/empresa/unidade recalcula impacto;
- dados compatíveis preservados;
- incompatíveis saem do estado ativo;
- etapas afetadas viram `NEEDS_REVIEW`;
- reset global indiscriminado proibido.

## Conditional Data Lifecycle

Estados:

```text
VISIBLE_ACTIVE
HIDDEN_RETAINED
CLEARED
```

Validar que campo oculto retido não entra no payload ativo.

## Submit Reconciliation

- `submission_id` estável para mesma tentativa lógica;
- duplo clique não duplica;
- timeout → `OUTCOME_UNKNOWN`;
- reconciliação `COMMITTED / NOT_FOUND / PROCESSING`;
- success somente após confirmação.

## Runtime Permission Revalidation

- permissão muda durante wizard;
- ação sensível revalida;
- CTA proibido desaparece;
- conteúdo restrito não vaza;
- dados permitidos são preservados.

---

# 7. Testes de integração futuros — onboarding

- iniciar draft;
- avançar/voltar sem perda;
- revisitar etapa concluída;
- clicar em etapa concluída pelo stepper;
- bloquear salto inválido para etapa futura;
- alterar Tipo de relação e invalidar campos/etapas posteriores;
- alterar empresa/unidade e recalcular dependências;
- esconder condicional sem enviá-lo como ativo;
- autosave + retomar;
- `Salvar e sair` + retomar na mesma etapa;
- refresh sem criar novo draft;
- browser back/forward;
- duas abas;
- dois administradores;
- sessão expirada → login → retomada;
- queda de rede → alterações locais → reconexão → salvar ou conflito;
- mudança de permissão durante o fluxo;
- ContextDrawer → atalho para etapa → formulário preservado;
- app context diferente da empresa contratante;
- biometria agora/depois;
- manager sem `biometrics:manage` não recebe CTA proibido;
- revisão consolidada;
- submit idempotente;
- resposta perdida → outcome unknown → reconciliação.

---

# 8. Testes de integração futuros — shell e páginas

- Dashboard → Funcionários preserva preferência da sidebar;
- Funcionários → Novo Funcionário mantém AppShell compartilhado;
- contexto de empresa/unidade do header não altera formulário em aberto;
- filtros/pesquisa preservados conforme navegação prevista;
- DetailDrawer não perde contexto da lista;
- EmptyState e ErrorState corretos;
- Toast somente suplementar.

---

# 9. RBAC / segurança visual

- `manager` pode ver/criar funcionário conforme permissões reais e não recebe biometria proibida;
- `auditor` não recebe CTAs de mutação que não possui;
- `operator` não recebe shell admin apenas por `punch:create`;
- ausência de permissão remove ação da UI;
- backend continua autoridade final;
- busca de EntityPicker não revela entidade fora do escopo;
- erro de permissão não vaza dados restritos;
- template biométrico não aparece como conteúdo baixável/visualizável;
- frames brutos não entram em recuperação local genérica.

---

# 10. Câmera / biometria

Testes unitários/integrados futuros:

- aguardando permissão;
- permissão negada;
- câmera indisponível;
- pronta;
- capturando multiquadro;
- qualidade insuficiente;
- processando;
- timeout;
- sucesso;
- falha recuperável;
- retry;
- configurar depois;
- nenhum upload/galeria no fluxo normal;
- notice/transparência antes da captura;
- conflito biométrico não é rotulado como fraude.

---

# 11. Registrar Ponto — regressão

Preservar o fluxo real existente enquanto a baseline técnica não mudar:

- challenge;
- câmera ao vivo;
- multiframe/liveness atual;
- reconhecimento;
- bloqueio de duplicidade;
- tipo Entrada/Saída;
- persistência atual;
- resultado final somente após confirmação;
- erro seguro;
- sem shell administrativo.

NF-01 não migra `Ponto → AttendanceEvent`.

---

# 12. Responsividade

Validar por tela crítica:

```text
360
768
1024
1440
larguras intermediarias
zoom 200%
containers estreitos/largos independentes do viewport quando aplicável
```

Verificações:

- sem overflow indevido;
- sidebar/overlay;
- stepper simplificado no mobile;
- `Ver etapas`;
- ContextDrawer;
- StickyFormActions keyboard-safe;
- 1–3 colunas conforme espaço;
- ordem DOM/foco preservada;
- texto sem clipping;
- touch targets adequados.

---

# 13. Acessibilidade

Automático + manual:

- labels;
- nomes acessíveis;
- `aria-current`, `aria-expanded`, `aria-controls`, `aria-describedby`;
- landmarks;
- foco visível;
- teclado completo;
- screen reader;
- contraste real;
- estado não dependente só de cor;
- reduced motion;
- zoom/reflow 200%;
- foco após step change;
- foco após drawer/modal;
- ErrorSummary;
- CameraPanel;
- PunchResult;
- tooltips acessíveis.

---

# 14. Motion

- FAST 120ms;
- NORMAL 180ms;
- SLOW 240ms;
- reduced motion remove movimento não essencial;
- nenhuma informação pode depender de animação.

---

# 15. Toast / mensagens

Validar que:

- `Rascunho salvo` pode ser toast;
- conflito não é somente toast;
- permissão removida não é somente toast;
- offline persistente não é somente toast;
- `OUTCOME_UNKNOWN` não é somente toast;
- erro crítico permanece visível e oferece recuperação.

---

# 16. Acceptance gate futuro da implementação

Antes de qualquer implementação ser considerada pronta:

```text
UNIT_TESTS=PASS
INTEGRATION_TESTS=PASS
EXISTING_REGRESSION_SUITE=PASS
RESPONSIVE_TARGETS=PASS
INTERMEDIATE_WIDTHS=PASS
ZOOM_200=PASS
ACCESSIBILITY_CRITICAL_SERIOUS=0
SECURITY_CHECKS=PASS
RBAC_REGRESSION=PASS
PUNCH_FLOW_REGRESSION=PASS
NO_FALSE_GREEN=PASS
NO_SILENT_DATA_LOSS=PASS
NO_SILENT_VERSION_OVERWRITE=PASS
IDEMPOTENT_FINAL_SUBMIT=PASS
```

Homologação de produção permanece gate separado.

---

# 17. Estado

```text
NF01_TEST_CONTRACT=CANONICALIZED
RC_CRITICAL_TESTS=SPECIFIED
RC_HIGH_TESTS=SPECIFIED
RC_MEDIUM_TESTS=SPECIFIED
NEW_UI_TESTS_CLAIMED_AS_EXECUTED=NO
PRODUCTION_HOMOLOGATION=SEPARATE
```
