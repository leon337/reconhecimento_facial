# NF-01 — Estratégia de Testes e Critérios de Aceite

## 1. Escopo de validação desta NF

NF-01 não altera código de produção. Portanto:

```text
NEW_DESIGN_UNIT_TESTS_EXECUTED=NO
NEW_DESIGN_INTEGRATION_TESTS_EXECUTED=NO
PRODUCTION_E2E_EXECUTED=NO
```

O que é aplicável nesta NF:
- consistência conceitual;
- inventário versus código real;
- matriz papel/permissão;
- matriz de estados;
- rastreabilidade tela → componente → estado → requisito;
- checagem dos principais contrastes de tokens;
- revisão de acessibilidade da especificação;
- contrato dos testes que a NF-02 deverá transformar em automação/evidência.

## 2. Linha de montagem da qualidade

Como numa linha de montagem, uma peça não pula diretamente do desenho para “pronta”. Cada estação valida uma característica antes de passar adiante.

```text
REQUISITO
  ↓
DESIGN
  ↓
ARQUITETURA
  ↓
IMPLEMENTAÇÃO
  ↓
UNITÁRIO
  ↓
INTEGRAÇÃO
  ↓
CONTRATO
  ↓
REGRESSÃO
  ↓
UX / RESPONSIVIDADE / ACESSIBILIDADE
  ↓
SEGURANÇA
  ↓
OBSERVABILIDADE
  ↓
VALIDAÇÃO OPERACIONAL
  ↓
EVIDÊNCIA
  ↓
GATE
```

## 3. Critérios de aceite da NF-01

| ID | Critério | Evidência esperada |
|---|---|---|
| NF01-AC-01 | definição de produto preserva decisões congeladas | `01_PRODUCT_DEFINITION.md` |
| NF01-AC-02 | inventário diferencia UI viva, legado e futuro | `02_UI_INVENTORY.md` |
| NF01-AC-03 | árvore oficial de navegação fechada | `03_INFORMATION_ARCHITECTURE.md` |
| NF01-AC-04 | RBAC atual não é reinventado | `04_ROLES_PERMISSIONS_AND_STATES.md` |
| NF01-AC-05 | estados obrigatórios têm significado inequívoco | `04_*` |
| NF01-AC-06 | tokens de tipografia, cor, spacing, grid, radius, shadow, focus, motion, breakpoints e ícones definidos | `05_DESIGN_SYSTEM.md` |
| NF01-AC-07 | componentes obrigatórios especificados | `06_COMPONENT_CATALOG.md` |
| NF01-AC-08 | oito wireframes mínimos cobertos | `07_WIREFRAMES.md` |
| NF01-AC-09 | 360/768/1024/1440 especificados | `08_RESPONSIVE_ACCESSIBILITY.md` |
| NF01-AC-10 | acessibilidade cobre contraste, teclado, foco, labels, cor, live, motion, erros, câmera e baixo letramento | `08_*` |
| NF01-AC-11 | contrato de testes da NF-02 definido | este documento |
| NF01-AC-12 | nenhuma mudança de produção/migração/IA/deploy | diff da PR |
| NF01-AC-13 | revisão independente executada | `10_NF01_CLOSEOUT.md` + PRF |

## 4. Testes unitários que a NF-02 deverá criar/ajustar

### Componentes/estado

- `StatusBadge` renderiza texto correto para todos os estados;
- `TELEMETRY_UNAVAILABLE` nunca recebe semântica success;
- `HealthCard` exige fonte/recência para estado healthy;
- `EmptyState` e `ErrorState` não são intercambiáveis;
- `Button loading` bloqueia duplo submit preservando label acessível;
- `FormField` associa label, ajuda e erro;
- `ConfirmationModal` recebe entidade/consequência;
- `LastUpdated` renderiza datetime legível e valor absoluto acessível.

### Permissões visuais

- `manager` vê funcionários e criar, mas não biometria;
- `auditor` vê leitura e não vê ações de criação/biometria;
- `operator` não recebe shell admin só por possuir `punch:create`;
- ausência de permissão remove ação da UI;
- backend continua autoridade final independentemente da UI.

### Estado de câmera

- câmera negada → mensagem acionável;
- `busy` desabilita dupla submissão;
- capture/progress atualiza texto acessível;
- timeout → erro recuperável;
- resultado só vira success após resposta confirmada do servidor.

## 5. Testes de integração da NF-02

- login → shell → funcionário conforme permissão;
- `users:view` retorna lista e EmptyState correto;
- `users:create` salva e encaminha para biometria sem regressão;
- biometria ao vivo mantém challenge + multiframe + duplicidade;
- remoção biométrica mantém POST, CSRF, RBAC e auditoria;
- Registrar Ponto mantém challenge, liveness, reconhecimento, duplicate rule e persistência atual;
- erro 403 vira experiência segura sem revelar dados;
- erro 500 exibe mensagem segura e request ID quando apropriado;
- `/health` não é reinterpretado como health global de componentes sem sinal.

## 6. Testes de contrato

### UI ↔ `/punch`

Preservar/validar:
- `status`;
- `message`;
- `processing_ms`;
- `target_met`;
- `retry_after_seconds` para duplicidade;
- códigos de erro usados para mensagens determinísticas.

### UI ↔ Admin

- CSRF presente em mutações;
- redirects após cadastro/biometria não quebram navegação;
- flash success/error é convertido para componente normalizado sem perder mensagem.

### UI ↔ Health

Enquanto o backend não mudar:

```text
/health.status=ok
/health.database=ok
```

significa apenas os sinais que a rota realmente testa. A UI não pode criar `camera=healthy`, `backup=healthy` ou `station=healthy` a partir desse payload.

## 7. Regressão obrigatória

A NF-02 deverá rodar a suíte existente e proteger:
- login/admin;
- RBAC;
- isolamento Company/Worksite;
- cadastro biométrico;
- criptografia e storage privado;
- câmera ao vivo;
- challenge de uso único;
- liveness passivo;
- identificação automática;
- bloqueio de duplicidade;
- gravação atual em `Ponto` enquanto essa baseline permanecer;
- auditoria;
- headers de segurança/CSRF.

O redesign não é justificativa para alterar o domínio de jornada.

## 8. Testes responsivos

Mínimo obrigatório por tela crítica:

| Largura | Verificações |
|---:|---|
| 360 | sem overflow de página, menu acessível, touch target, câmera/resultado visíveis |
| 768 | filtros/formulários sem colisão, drawer/modal íntegro |
| 1024 | sidebar + tabela legíveis, ordem de foco coerente |
| 1440 | grid equilibrado, conteúdo não esticado, dados sem espaços mortos abusivos |

Telas mínimas:
- login;
- dashboard;
- funcionários;
- novo funcionário;
- biometria;
- registros;
- saúde/eventos quando materializados;
- Registrar Ponto.

## 9. Testes de acessibilidade

Automáticos + manuais:

### Automáticos
- axe/engine equivalente sem violações críticas/serious;
- contraste de tokens/combinações reais;
- labels/form landmarks;
- nomes acessíveis de botões.

### Manuais
- fluxo completo só com teclado;
- 200% zoom/reflow;
- leitor de tela em login, formulário, modal e PunchResult;
- reduced motion;
- foco após modal/drawer/erro;
- câmera com permissão negada e câmera indisponível;
- mensagem compreensível sem depender de cor.

## 10. Testes de UX

### Cenário UX-01 — Registrar ponto

Usuário deve identificar:
1. onde olhar;
2. qual ação executar;
3. que etapa está ocorrendo;
4. se concluiu;
5. o que fazer se falhar.

### Cenário UX-02 — Funcionário sem biometria

Gestor autorizado deve localizar pessoa e chegar ao cadastro biométrico sem interpretar código técnico.

### Cenário UX-03 — Auditor

Auditor deve conseguir consultar dados permitidos sem visualizar CTAs de edição/cadastro biométrico.

### Cenário UX-04 — Telemetria ausente

Usuário de suporte deve ver `Telemetria indisponível`, nunca `OK`, para estação sem heartbeat.

## 11. Testes de segurança ligados ao redesign

- nenhuma mutação muda de GET para facilitar UI;
- CSRF preservado;
- UI não expõe segredo/token/template biométrico;
- erros não exibem stack traces;
- permissões não são confiadas somente ao frontend;
- Content Security Policy deve ser revisada caso novas dependências visuais sejam propostas;
- eventual biblioteca de ícones/fontes deve ser auditada antes da inclusão;
- ação destrutiva continua auditada.

## 12. Testes de observabilidade da UI

Mesmo antes da NF-04, a NF-02 deve garantir que:
- request ID de erro, quando disponível, pode ser apresentado/copied em suporte;
- ausência de telemetria não é success;
- timestamp de última atualização não é inventado;
- loading expirado vira estado terminal recuperável;
- erro de rede e 5xx não são descritos como mesma causa quando puderem ser distinguidos.

NF-02 não deve criar backend de observabilidade novo.

## 13. Matriz de rastreabilidade mínima

| Tela | Componentes-chave | Estados obrigatórios | Requisitos |
|---|---|---|---|
| Login | FormField, Button, ErrorState | ready, loading, error | RBAC/auth, a11y |
| Funcionários | AppShell, Search, FilterBar, DataTable, EmptyState, Pagination | loading, empty, ready, error, no_permission | users:view/create |
| Biometria | CameraPanel, Button, ErrorState, Toast | ready, loading, success, warning, error | biometrics:manage, live camera |
| Registros | DataTable, FilterBar, DetailDrawer | loading, empty, ready, error, no_permission | punch:view |
| Saúde | HealthCard, StatusBadge, LastUpdated, DegradationBanner | loading, ready, degraded, error, telemetry_unavailable | false-green policy |
| Eventos | FilterBar, EventTimeline, DetailDrawer | loading, empty, ready, error | audit/log access futuro |
| Registrar Ponto | CameraPanel, Button, PunchResult | ready, loading, success, warning, error, offline | punch flow |

## 14. Validações realizadas na NF-01

### Consistência com código atual

- templates/rotas atuais inventariados;
- RBAC atual transcrito da fonte;
- upload legado separado de fluxo vivo;
- `Ponto` live write mantido explícito;
- telemetria existente versus ausente diferenciada.

### Contraste de tokens

Pares principais calculados em `05_DESIGN_SYSTEM.md`; todos os pares de texto base escolhidos atendem pelo menos WCAG AA para texto normal nas combinações documentadas.

### Revisão de acessibilidade conceitual

Checklist especificado em `08_RESPONSIVE_ACCESSIBILITY.md`; execução automatizada sobre UI nova fica para NF-02 porque a UI nova ainda não existe.

## 15. Gate da NF-02

A implementação futura só pode considerar a especificação aceita se:

```text
UNIT_TESTS=PASS
INTEGRATION_TESTS=PASS
EXISTING_REGRESSION_SUITE=PASS
RESPONSIVE_360_768_1024_1440=PASS
ACCESSIBILITY_CRITICAL_SERIOUS=0
SECURITY_CHECKS=PASS
PUNCH_FLOW_REGRESSION=PASS
RBAC_REGRESSION=PASS
NO_FALSE_GREEN=PASS
PRODUCTION_HOMOLOGATION=STILL_SEPARATE_GATE
```

## 16. Decisão

```text
NF02_TEST_CONTRACT=COMPLETE
NF01_CONCEPTUAL_VALIDATION=DEFINED_AND_EXECUTABLE
NEW_UI_TESTS_CLAIMED_AS_EXECUTED=NO
```