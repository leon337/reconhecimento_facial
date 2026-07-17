# Auditoria Arquitetural Completa — Pré-FASE 9

## 1. Identificação

- Projeto: Controle de Ponto Potiguar
- Repositório: `leon337/reconhecimento_facial`
- Branch auditada: `main`
- Commit-base: `079a767682c1b045635e3057d6f4c7092113f42b`
- Tipo: auditoria somente leitura
- Alteração de código da aplicação: não
- Dados biométricos reais utilizados: não

## 2. Objetivo

Avaliar a arquitetura atual antes da FASE 9, identificando pontos fortes, acoplamentos, riscos, limitações de crescimento, lacunas de segurança, débitos técnicos e a sequência correta de refatoração.

## 3. Escopo observado

A auditoria considerou a fábrica Flask, configuração, modelos, autenticação administrativa, cadastro biométrico, reconhecimento facial, registro de ponto, cálculo de jornada, banco de horas, testes, Docker, CI e documentação integrada nas FASES anteriores.

## 4. Visão atual

```text
Navegador
   |
   v
Flask / main.py
   |
   +-- Blueprint administrativo
   |      +-- autenticação por sessão
   |      +-- cadastro de usuário
   |      +-- upload e encoding facial
   |
   +-- Blueprint de ponto
          +-- reconhecimento
          +-- bloqueio de duplicidade
          +-- persistência de Ponto

SQLAlchemy
   |
   +-- User
   +-- Ponto

Domínio em módulos independentes
   +-- jornada
   +-- cálculo diário
   +-- banco de horas
```

## 5. Resultado executivo

```text
ARQUITETURA_ATUAL=ADEQUADA_PARA_POC_E_HOMOLOGACAO_CONTROLADA
ARQUITETURA_ATUAL=INADEQUADA_PARA_PRODUCAO_MULTIEMPRESA
REFATORACAO_TOTAL=NAO_NECESSARIA
REFATORACAO_ESTRUTURAL_INCREMENTAL=OBRIGATORIA
FASE_9_PODE_INICIAR_DIRETAMENTE=NAO
FASE_9_DEVE_SER_REORDENADA=SIM
```

A base não deve ser descartada. O núcleo Flask, os módulos puros de jornada e a suíte de testes são reutilizáveis. Entretanto, segurança, persistência, tenancy e separação de responsabilidades precisam ser corrigidas antes de criptografar biometria ou implantar PostgreSQL.

## 6. Pontos fortes

### 6.1 Fábrica de aplicação testável

`create_app(test_config)` permite substituir banco, diretório de upload e configurações nos testes. Isso reduz dependência de recursos reais e facilita testes unitários e de integração.

### 6.2 Blueprints separados

Administração e registro de ponto possuem blueprints próprios, evitando concentrar todas as rotas no entrypoint.

### 6.3 Domínio de jornada parcialmente desacoplado

`Jornada`, `calcular_dia`, `consolidar_banco_horas` e `fechar_mes` são funções e objetos imutáveis, com regras testáveis fora das rotas HTTP.

### 6.4 Segurança básica já existente

- senha armazenada por hash;
- CSRF habilitado;
- sessão HTTPOnly;
- cookie seguro em produção;
- redirecionamento interno validado;
- upload conferido por conteúdo JPEG/PNG;
- nome de arquivo aleatório;
- limite de 5 MB;
- autenticação administrativa obrigatória.

### 6.5 CI funcional

O pipeline executa compilação, testes e build Docker. A linha de montagem está correta:

```text
checkout -> dependências -> sintaxe -> testes -> Docker
```

### 6.6 Testes isolados

Os testes usam SQLite em memória, diretório temporário e reconhecimento simulado. Não dependem de fotos reais nem de biometria real.

## 7. Achados críticos

### ARQ-01 — Modelo de dados não suporta multiempresa ou múltiplas obras

`User` e `Ponto` não possuem `company_id`, `worksite_id`, vínculo temporal ou escopo organizacional. Todos os usuários pertencem implicitamente a uma única empresa e uma única base global.

Impactos:

- administrador enxerga todos os usuários;
- uma matrícula não possui escopo por empresa;
- ponto não informa em qual obra/unidade foi registrado;
- banco de horas não pode ser consolidado por contrato, obra ou lotação;
- risco de vazamento entre clientes quando o sistema crescer.

Classificação: crítico antes de multiempresa.

### ARQ-02 — Modelo `User` mistura identidade, credencial, empregado e biometria

A tabela atual reúne:

- login;
- senha;
- papel de acesso;
- dados pessoais;
- matrícula;
- cargo;
- jornada textual;
- endereço;
- passagem;
- encoding facial;
- URL da foto.

Essa concentração dificulta LGPD, exclusão seletiva, histórico trabalhista e múltiplas biometrias.

Separação recomendada:

```text
Account
Employee
Employment
WorkSchedule
BiometricProfile
BiometricSample
```

Classificação: alto.

### ARQ-03 — Camada de rota executa responsabilidades demais

O cadastro biométrico valida upload, grava arquivo, configura variável de modelo, processa imagem, gera encoding, altera modelo e confirma transação dentro da rota.

O registro de ponto reconhece, aplica regra, persiste e monta resposta dentro da rota.

Isso dificulta:

- transações controladas;
- auditoria;
- troca de armazenamento;
- criptografia;
- testes de serviço;
- uso futuro por API móvel.

Recomendação: criar serviços de aplicação:

```text
BiometricEnrollmentService
PunchRegistrationService
EmployeeService
```

Classificação: alto.

### ARQ-04 — A regra de duplicidade consulta o ORM diretamente

`check_duplicate_punch` parece regra de domínio, mas depende de `Ponto.query`. Isso mistura regra e infraestrutura.

Recomendação:

```text
latest_punch = repository.get_latest(employee_id)
result = duplicate_policy.evaluate(latest_punch, now, window)
```

Classificação: médio.

### ARQ-05 — Criação automática das tabelas no startup

`db.create_all()` é executado durante `create_app`. Em produção isso não substitui migrações e pode mascarar divergência de schema.

Riscos:

- ausência de histórico de alteração;
- banco diferente entre ambientes;
- falha em mudanças destrutivas;
- concorrência entre instâncias.

Recomendação: remover em produção após introduzir Alembic/Flask-Migrate.

Classificação: crítico para produção.

### ARQ-06 — SQLite como padrão e ausência de estratégia transacional explícita

SQLite é adequado para testes e POC. Para múltiplos dispositivos e concorrência, PostgreSQL deve ser o ambiente de homologação e produção.

A transação de ponto precisa garantir atomicidade entre:

```text
verificar duplicidade -> inserir ponto
```

Hoje duas requisições concorrentes podem consultar ausência de duplicidade e gravar quase simultaneamente.

Recomendação: constraint/idempotency key ou bloqueio transacional no PostgreSQL.

Classificação: crítico.

### ARQ-07 — Tempo sem timezone

O sistema utiliza `datetime.utcnow()` e colunas `DateTime` sem timezone explícito. O domínio de ponto exige política clara para UTC, fuso da empresa e horário de verão.

Recomendação:

- persistir UTC timezone-aware;
- armazenar timezone IANA por empresa/unidade;
- converter apenas nas bordas;
- definir data operacional local para fechamento.

Classificação: alto.

### ARQ-08 — Jornada armazenada como texto no usuário

`schedule` é texto livre e o parser aceita somente jornadas diurnas simples com no máximo um intervalo.

Não suporta corretamente:

- turno noturno atravessando meia-noite;
- escalas 12x36;
- jornadas por dia da semana;
- feriados;
- alterações históricas;
- múltiplos vínculos;
- tolerância por empresa ou acordo.

Recomendação: entidade versionada de jornada e atribuição com vigência.

Classificação: crítico para evolução funcional.

### ARQ-09 — Tipos de ponto insuficientes

O modelo aceita apenas `ENTRADA` e `SAIDA`. O cálculo combina timestamps por posição e não valida semanticamente a sequência.

Uma sequência incorreta pode ser pareada silenciosamente.

Recomendação:

- eventos tipados ou direção derivada por máquina de estados;
- validação de alternância;
- justificativas e ajustes separados do evento bruto;
- evento original imutável.

Classificação: alto.

### ARQ-10 — Banco de horas e fechamento não persistidos

As regras existem como funções puras, mas não há agregados persistidos, versão de fechamento, aprovação, reabertura ou trilha de ajuste.

Recomendação:

```text
TimeEntry (imutável)
DailyTimesheet
MonthlyClosing
TimeAdjustment
Approval
```

Classificação: alto.

### ARQ-11 — Biometria armazenada junto ao cadastro e sem envelope criptográfico

O encoding é JSON em texto e a foto é gravada em pasta pública estática.

Riscos:

- exposição direta de fotografia;
- cópia em backup sem segregação;
- dificuldade de rotação de chave;
- exclusão incompleta;
- ausência de versão do algoritmo/modelo.

Recomendação:

- armazenamento privado fora de `static`;
- criptografia por envelope;
- `key_id`, versão do modelo e data de coleta;
- opção de descartar foto após gerar encoding;
- acesso somente por serviço autorizado.

Classificação: crítico.

### ARQ-12 — Reconhecimento carrega todas as biometrias a cada batida

A função consulta todos os usuários com encoding e converte todos os JSONs para NumPy em cada requisição.

Escala aproximada:

```text
custo por batida = leitura de N usuários + parsing de N JSONs + comparação de N vetores
```

Para poucas dezenas funciona. Para centenas ou múltiplas empresas, o custo e o isolamento são inadequados.

Recomendação:

- filtrar por empresa/unidade;
- cache versionado por tenant;
- invalidar cache no recadastro;
- avaliar índice vetorial somente quando a escala justificar.

Classificação: alto.

### ARQ-13 — Administração possui autorização binária

Existe apenas papel `admin`. Não há RBAC granular para RH, supervisor de obra, auditor ou operador.

Recomendação:

```text
SUPER_ADMIN
COMPANY_ADMIN
HR
WORKSITE_MANAGER
AUDITOR
EMPLOYEE
```

Cada consulta deve ser limitada pelo tenant e pela unidade autorizada.

Classificação: alto.

### ARQ-14 — Ausência de trilha de auditoria

Login, cadastro, alteração, biometria, ajustes e fechamento não possuem eventos de auditoria persistidos.

Recomendação: `AuditEvent` append-only com ator, tenant, ação, alvo, resultado, IP, user-agent, request-id e timestamp UTC.

Classificação: crítico para produção.

### ARQ-15 — Ausência de camada de configuração tipada

As variáveis são lidas diretamente por `os.environ` e algumas configurações são definidas no `main.py`.

Recomendação: classes `DevelopmentConfig`, `TestingConfig`, `ProductionConfig`, validação de startup e segredos fora do Git.

Classificação: médio.

### ARQ-16 — Observabilidade insuficiente

Não há evidência de logging estruturado, correlation ID, métricas, health/readiness checks ou rastreamento de falhas.

Recomendação mínima:

- logs JSON;
- request-id;
- `/health/live`;
- `/health/ready`;
- métricas de latência e erros;
- alerta de falha de reconhecimento e banco.

Classificação: alto.

### ARQ-17 — CI sem qualidade estática e segurança de dependências

O pipeline valida sintaxe, testes e Docker, mas não executa:

- lint;
- formatação;
- type checking;
- cobertura mínima;
- análise de vulnerabilidades;
- verificação de segredos;
- testes com PostgreSQL.

Recomendação: Ruff, mypy progressivo, coverage gate, pip-audit, secret scan e job PostgreSQL.

Classificação: médio.

### ARQ-18 — Docker executa como root e mistura build/runtime

A imagem atual instala compiladores e bibliotecas de build na mesma camada de runtime e não define usuário não-root.

Recomendação: multi-stage build, usuário dedicado, healthcheck e filesystem com permissões mínimas.

Classificação: alto para produção.

### ARQ-19 — Ausência de API versionada

As rotas retornam HTML e JSON sem contrato de API versionado. Um aplicativo móvel futuro exigirá separação entre interface web e API.

Recomendação:

```text
/api/v1/auth
/api/v1/employees
/api/v1/biometrics
/api/v1/punches
/api/v1/timesheets
```

Classificação: médio antes do aplicativo móvel.

### ARQ-20 — Ausência de entidades para obras, unidades e dispositivos

Para o objetivo informado, faltam no domínio:

```text
Company
Worksite
OrganizationalUnit
Device
EmployeeAssignment
Geofence
```

O ponto deve registrar a lotação válida no momento do evento, não apenas o usuário.

Classificação: crítico para o produto desejado.

## 8. Avaliação por dimensão

| Dimensão | Estado | Nota |
|---|---|---:|
| Organização básica | boa | 7/10 |
| Testabilidade | boa | 8/10 |
| Domínio de jornada | parcial | 6/10 |
| Segurança básica | parcial | 6/10 |
| Segurança biométrica | insuficiente | 2/10 |
| Persistência e migrações | insuficiente | 3/10 |
| Multiempresa | inexistente | 1/10 |
| Múltiplas obras | inexistente | 1/10 |
| Concorrência | insuficiente | 3/10 |
| Observabilidade | insuficiente | 2/10 |
| Escalabilidade do reconhecimento | limitada | 3/10 |
| CI e testes | boa base | 7/10 |
| Prontidão de produção | bloqueada | 2/10 |

## 9. Arquitetura alvo incremental

Não é recomendado migrar agora para microserviços. Um monólito modular continua sendo a melhor relação entre simplicidade e robustez.

```text
app/
  web/                    # páginas e formulários
  api/v1/                 # contratos JSON
  application/            # casos de uso
  domain/
    identity/
    organization/
    biometrics/
    attendance/
    scheduling/
    timebank/
  infrastructure/
    persistence/
    repositories/
    crypto/
    storage/
    observability/
  security/
  models/                 # mapeamentos ORM separados por domínio
```

Fluxo alvo:

```text
HTTP/API
  -> caso de uso
  -> política de domínio
  -> repositório abstrato
  -> SQLAlchemy/PostgreSQL
  -> evento de auditoria
```

## 10. Modelo mínimo recomendado

```text
Company
Worksite
Account
Role
Permission
Employee
Employment
EmployeeAssignment
WorkSchedule
ScheduleAssignment
BiometricProfile
BiometricSample
Device
TimeEntry
TimeAdjustment
DailyTimesheet
MonthlyClosing
AuditEvent
```

Regras obrigatórias:

- todas as entidades operacionais carregam `company_id`;
- consultas exigem escopo do tenant;
- obra/unidade é registrada no evento de ponto;
- eventos brutos são imutáveis;
- correções são eventos separados;
- fechamento guarda versão e aprovador;
- biometria fica segregada e criptografada.

## 11. Estratégia de migração

### Etapa A — Fundação arquitetural

1. criar configuração tipada;
2. remover responsabilidades das rotas para serviços;
3. introduzir interfaces de repositório;
4. padronizar UTC timezone-aware;
5. adicionar request-id e logs estruturados.

### Etapa B — Banco e tenancy

1. introduzir Alembic;
2. configurar PostgreSQL em CI e homologação;
3. criar Company e Worksite;
4. adicionar escopo organizacional;
5. criar Employee separado de Account.

### Etapa C — Biometria segura

1. separar perfil biométrico;
2. armazenamento privado;
3. criptografia por envelope;
4. descarte configurável de foto;
5. cache por tenant;
6. auditoria de coleta, uso e exclusão.

### Etapa D — Ponto e jornada robustos

1. evento de ponto imutável;
2. validação de sequência;
3. jornada versionada;
4. turno noturno e escalas;
5. ajuste e justificativa;
6. fechamento persistido.

### Etapa E — Hardening

1. RBAC;
2. rate limiting;
3. headers de segurança;
4. health/readiness;
5. backup e restore real;
6. testes de concorrência;
7. pentest e revisão LGPD.

## 12. Reordenação proposta da FASE 9

A subdivisão anterior começava diretamente pela criptografia. A auditoria recomenda:

```text
FASE 9.0 — Fundação arquitetural e contratos
FASE 9.1 — PostgreSQL, Alembic e transações
FASE 9.2 — Multiempresa, obras e escopo de acesso
FASE 9.3 — Identidade, empregado e RBAC
FASE 9.4 — Biometria segregada e criptografada
FASE 9.5 — Ponto imutável, jornada versionada e fechamento
FASE 9.6 — Auditoria, observabilidade e proteção contra abuso
FASE 9.7 — Backup, restauração e segurança de infraestrutura
FASE 9.8 — Validação integral de produção
```

Motivo: criptografar o campo atual antes de separar tenant, empregado e perfil biométrico criaria retrabalho e uma migração adicional.

## 13. Testes obrigatórios por etapa

### Unitários

- políticas de tenant;
- autorização RBAC;
- criptografia e rotação de chave;
- jornada noturna e escalas;
- idempotência;
- fechamento e ajustes.

### Integração

- PostgreSQL real no CI;
- migrations upgrade/downgrade;
- isolamento entre empresas;
- concorrência de duas batidas;
- upload privado;
- auditoria administrativa;
- backup e restauração.

### Contrato e sistema

- API v1;
- fluxo administrativo completo;
- dispositivo autorizado;
- indisponibilidade do banco;
- rollback de deploy;
- exclusão de biometria.

## 14. Gates para iniciar implementação

```text
AUDITORIA_ARQUITETURAL_PUBLICADA=PASS
ARQUITETURA_ALVO_APROVADA=PENDING
ORDEM_DA_FASE_9_APROVADA=PENDING
MULTIEMPRESA_NO_ESCOPO=CONFIRM_REQUIRED
MULTIPLAS_OBRAS_NO_ESCOPO=CONFIRMED_BY_PRODUCT_VISION
PRODUCTION_DATA_ALLOWED=NO
```

## 15. Conclusão

A aplicação possui uma boa base de recuperação: fábrica Flask, blueprints, regras puras de jornada, testes e CI. O problema não é a escolha do Flask nem a existência de um monólito. O problema é que o modelo atual representa apenas uma empresa global, mistura responsabilidades e não possui as fronteiras necessárias para biometria, concorrência e operação multiobra.

A decisão recomendada é preservar o núcleo funcional e executar uma refatoração incremental para monólito modular. Não iniciar a criptografia sobre o campo atual antes de concluir a fundação arquitetural, tenancy e separação de identidade/empregado/biometria.
