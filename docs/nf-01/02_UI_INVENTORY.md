# NF-01 — Inventário Real da Interface

**Baseline inspecionada:** `main@2a388fdc40817dca8f7bd96232e723c0e520702b`  
**Regra:** somente itens comprovados no código são classificados como existentes.

## 1. Resumo executivo

A aplicação atual possui duas superfícies vivas:

1. **Administração:** login, lista/cadastro de funcionários e biometria.
2. **Registrar Ponto:** fluxo independente com câmera ao vivo.

Não existe hoje AppShell compartilhado, sidebar, header, dashboard, tela dedicada de empresas/obras, registros recentes, saúde operacional ou eventos/logs.

Os templates `form.html` e `result.html` pertencem ao fluxo antigo de upload e não estão registrados pelo `create_app()` atual.

## 2. Templates encontrados

| Template | Rota viva associada | Função | Estado NF-01 | Decisão |
|---|---|---|---|---|
| `templates/admin/login.html` | `/admin/login` GET/POST | autenticação administrativa | REAL | REDESENHAR |
| `templates/admin/users_list.html` | `/admin/users` GET | lista de usuários/funcionários | REAL | REDESENHAR |
| `templates/admin/users_new.html` | `/admin/users/new` GET + `/admin/users` POST | cadastro | REAL | REDESENHAR |
| `templates/admin/users_biometric.html` | `/admin/users/<id>/biometric` | cadastro facial ao vivo | REAL | REDESENHAR preservando fluxo |
| `templates/punch.html` | `/punch` GET | estação de ponto | REAL | REDESENHAR preservando shell separado |
| `templates/form.html` | sem blueprint registrado na aplicação atual | upload facial legado | NÃO VIVO | DEPRECAR |
| `templates/result.html` | sem blueprint registrado na aplicação atual | resultado do upload legado | NÃO VIVO | DEPRECAR |

## 3. Rotas atuais de UI e ação

### Administração

| Método | Rota | Permissão | Interface/efeito |
|---|---|---|---|
| GET/POST | `/admin/login` | credencial com acesso administrativo | login |
| POST | `/admin/logout` | sessão administrativa | encerra sessão |
| GET | `/admin/users` | `users:view` | lista |
| GET | `/admin/users/new` | `users:create` | formulário |
| POST | `/admin/users` | `users:create` | cria Employee + User |
| GET | `/admin/users/<id>/biometric` | `biometrics:manage` | captura facial |
| GET | `/admin/users/<id>/biometric/challenge` | `biometrics:manage` | challenge da captura |
| POST | `/admin/users/<id>/biometric` | `biometrics:manage` | persiste perfil biométrico |
| POST | `/admin/users/<id>/biometric/remove` | `biometrics:manage` | remove biometria, auditado |

### Ponto

| Método | Rota | Função |
|---|---|---|
| GET | `/punch` | renderiza estação |
| GET | `/punch/challenge` | emite challenge de uso único |
| POST | `/punch` | liveness + identificação + regra duplicidade + gravação `Ponto` |
| GET | `/local-ca.crt` | certificado local quando disponível |

### Observabilidade técnica sem UI

| Rota | Estado | Limite |
|---|---|---|
| `/health` | REAL | prova app + banco, não sistema completo |
| `/metrics` | REAL | contadores em memória, não duráveis |

## 4. Estrutura visual existente

### Padrão geral

- páginas HTML independentes;
- TailwindCSS 2.2.19 via CDN em quase todos os templates;
- classes utilitárias diretamente no HTML;
- `admin/login.html` praticamente sem styling;
- não foi localizado `base.html`/AppShell compartilhado;
- não foi localizado catálogo de componentes ou tokens centralizados.

### `users_list.html`

**Existe:**
- card branco em fundo cinza;
- flash success/error;
- ação `+ Novo Funcionário`;
- tabela horizontalmente rolável;
- colunas ID, Username, Nome, Biometria, Ações;
- status biométrico `Ativa` / `Não cadastrada`;
- cadastrar/recadastrar biometria;
- remover biometria com `window.confirm()`.

**Não existe:**
- busca;
- filtros;
- paginação;
- EmptyState explícito;
- modal próprio;
- drawer de detalhes;
- bulk actions.

### `users_new.html`

**Existe:**
- campos username, password, nome, matrícula, função, horário, endereço, tipo de passagem;
- CSRF;
- salvar;
- voltar à lista.

**Problemas de normalização:**
- campos usam predominantemente placeholder, sem labels persistentes;
- UI não expõe escolha de `access_role`, embora backend aceite e aplique default;
- não há ajuda contextual, validação inline ou resumo de erros.

### `users_biometric.html`

**Existe:**
- câmera ao vivo;
- challenge/progresso;
- várias leituras faciais;
- feedback via `aria-live`;
- orientações de processo e segurança;
- timeout/falhas tratados no JS.

**Preservar:**
- câmera ao vivo obrigatória;
- proibição de galeria/upload no fluxo real;
- uma pessoa por captura;
- multiframe;
- challenge;
- checagem de duplicidade.

### `punch.html`

**Existe:**
- câmera ao vivo;
- challenge;
- botões abrir câmera / identificar e registrar;
- seletor Entrada/Saída;
- meta e tempo atual;
- status `aria-live`;
- timeout e erros em JS.

**Preservar:**
- experiência isolada do admin;
- ação primária clara;
- confirmação nominal do registro;
- mensagens de câmera/reconhecimento;
- proteção contra duplicidade.

## 5. JavaScript existente

| Arquivo | Responsabilidade | Decisão |
|---|---|---|
| `static/punch.js` | câmera, challenge, burst, envio, timeout, status, tempo | PRESERVAR comportamento; NORMALIZAR UI |
| `static/biometric_capture.js` | câmera, challenge, burst de cadastro, envio, timeout | PRESERVAR comportamento; NORMALIZAR UI |

Não foi localizado framework frontend SPA; a evolução prevista é progressiva sobre Flask/Jinja/JS.

## 6. Estados visuais atuais

| Estado | Ponto | Biometria | Admin lista/form | Avaliação |
|---|---|---|---|---|
| loading/busy | texto + disable | texto + disable | não formal | NORMALIZAR |
| success | texto verde | flash verde/redirecionamento | flash verde | NORMALIZAR |
| error | texto vermelho | texto/flash vermelho | flash vermelho | NORMALIZAR |
| empty | não aplicável | não aplicável | tabela vazia sem EmptyState | CRIAR |
| skeleton | inexistente | inexistente | inexistente | CRIAR quando espera justificar |
| offline | erro genérico de comunicação | erro genérico | inexistente | ESPECIFICAR, não implementar nesta NF |
| degraded | inexistente | inexistente | inexistente | ESPECIFICAR |
| no permission | HTTP 403 genérico | HTTP 403 genérico | HTTP 403 | NORMALIZAR |
| telemetry unavailable | inexistente em UI | inexistente | inexistente | ESPECIFICAR |

## 7. Formulários

| Formulário | Campos/ação | Estado |
|---|---|---|
| Login | usuário + senha | REAL |
| Novo funcionário | dados cadastrais e senha | REAL |
| Cadastro biométrico | câmera/challenge; sem upload manual | REAL |
| Remoção biométrica | POST + confirm nativo | REAL |
| Registrar ponto | tipo Entrada/Saída + câmera | REAL |

## 8. Tabelas, modais e navegação

- **Tabela real:** somente lista de usuários/funcionários.
- **Modal real:** nenhum componente; remoção usa confirmação nativa do navegador.
- **Navegação global real:** inexistente.
- **Breadcrumb real:** inexistente.
- **Sidebar real:** inexistente.
- **Header global real:** inexistente.
- **Tabs reais:** inexistentes.
- **Paginação real:** inexistente.

## 9. Inventário por domínio solicitado

| Domínio | Evidência de UI | Classificação NF-01 |
|---|---|---|
| Dashboard | nenhuma | FUTURO / NF-02 shell |
| Funcionários | lista + novo usuário/Employee | REDESENHAR |
| Biometria | cadastro/remover | PRESERVAR + REDESENHAR |
| Empresas | domínio existente, sem tela localizada | FUTURO de UI |
| Obras/Unidades | domínio existente, sem tela localizada | FUTURO de UI |
| Registros | dados existem em `Ponto`, sem tela localizada | FUTURO de UI |
| Health | `/health` técnico, sem tela | FUTURO de UI |
| Logs | logs estruturados, sem tela | FUTURO de UI |
| Telemetria | `/metrics` em memória, sem tela | FUTURO de UI |
| Relatórios | sem tela viva | FUTURO |
| IA | não implementada | FUTURO |

## 10. Matriz de decisão final

### PRESERVAR

- fluxos e invariantes de câmera/liveness/identificação;
- RBAC;
- isolamento por empresa/obra;
- CSRF;
- mensagens de resultado úteis;
- `aria-live` já presente nas capturas;
- confirmação antes de remoção biométrica.

### REDESENHAR

- login;
- lista de funcionários;
- novo funcionário;
- cadastro biométrico;
- Registrar Ponto, sem anexá-lo ao shell admin.

### NORMALIZAR

- estados;
- campos/labels;
- botões;
- mensagens;
- tabela;
- tipografia/espaçamento;
- navegação administrativa;
- confirmação destrutiva.

### DEPRECAR

- `form.html` e `result.html` como UI de upload legado; a remoção física não ocorre na NF-01.

### FUTURO

- dashboard;
- empresas/obras na UI;
- registros recentes;
- saúde/logs/eventos;
- relatórios;
- IA;
- offline/geofence.

### NÃO APLICÁVEL NESTA NF

- implementação de backend para telas futuras;
- migration `Ponto -> AttendanceEvent`;
- telemetria nova;
- deploy/homologação.

## 11. Conclusão

```text
CURRENT_UI_INVENTORY=COMPLETE
CURRENT_GLOBAL_SHELL=ABSENT
CURRENT_COMPONENT_SYSTEM=ABSENT
ACTIVE_UPLOAD_UI=NO
PUNCH_UI=REAL_AND_SEPARATE
ADMIN_USERS_UI=REAL
COMPANY_WORKSITE_UI=NOT_FOUND
HEALTH_LOG_UI=NOT_FOUND
```