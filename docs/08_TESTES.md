# 08 — Testes

## 1. Objetivo

Documentar a estratégia de testes do Controle de Ponto Potiguar e os comandos usados para validar regras de negócio, integrações HTTP, autenticação administrativa, reconhecimento facial, jornada e banco de horas.

## 2. Escopo

A suíte cobre:

- criação da aplicação Flask em modo de teste;
- autenticação e proteção de rotas administrativas;
- cadastro de usuários e biometria;
- validação de imagens;
- reconhecimento facial com resultados controlados;
- registro de entrada e saída;
- bloqueio de batidas duplicadas;
- interpretação de jornadas;
- cálculo diário e tolerâncias;
- consolidação do banco de horas;
- fechamento mensal;
- build do contêiner Docker.

Dados biométricos reais não devem ser usados na suíte automatizada. Use mocks, arquivos sintéticos e usuários fictícios.

## 3. Tipos de teste

### 3.1 Testes unitários

Validam funções e regras isoladas, sem depender da interface completa:

- parser de jornada;
- duração prevista;
- cálculo de atraso, saída antecipada e saldo;
- tolerâncias configuráveis;
- detecção de duplicidade;
- consolidação de créditos e débitos;
- bloqueio do fechamento com registros incompletos.

### 3.2 Testes de integração

Validam a linha de montagem completa da aplicação:

```text
requisição HTTP
→ validação
→ serviço de reconhecimento simulado
→ regra de duplicidade
→ persistência no banco de teste
→ resposta HTTP
```

Exemplos cobertos:

- `POST /punch` sem imagem retorna `400`;
- tipo de ponto inválido retorna `400`;
- rosto desconhecido retorna `422`;
- usuário reconhecido gera registro e retorna `201`;
- batida dentro da janela configurada retorna `409` e não cria novo registro.

### 3.3 Testes de segurança

Devem confirmar:

- rotas administrativas exigem login;
- somente usuário com papel `admin` autentica no painel;
- senhas são verificadas por hash;
- redirecionamentos externos inseguros são rejeitados;
- CSRF permanece ativo fora do ambiente de teste;
- uploads aceitam somente conteúdo JPEG ou PNG válido;
- arquivos recebem nomes aleatórios e não reutilizam o nome original.

### 3.4 Teste de build Docker

O pipeline deve construir a imagem baseada em Python 3.10 e validar a instalação das dependências nativas e Python.

## 4. Organização esperada

```text
tests/
├── conftest.py
├── test_admin_auth.py
├── test_admin_users.py
├── test_banco_horas.py
├── test_calculo_jornada.py
├── test_jornada.py
└── test_punch.py
```

A lista real pode crescer. Cada arquivo deve manter responsabilidade clara.

## 5. Execução local

Com o ambiente virtual ativo:

```bash
python -m pytest -q
```

Executar um arquivo específico:

```bash
python -m pytest -q tests/test_punch.py
```

Executar um teste específico:

```bash
python -m pytest -q tests/test_punch.py::test_punch_post_rejects_duplicate_record
```

Verificar sintaxe:

```bash
python -m compileall -q app main.py tests
```

## 6. Execução com Docker

Construir a imagem:

```bash
docker build -t controle-ponto-potiguar:test .
```

A execução do contêiner não substitui os testes unitários e de integração. Ela valida empacotamento, dependências e inicialização pelo Gunicorn.

## 7. Integração contínua

O GitHub Actions funciona como gate do Pull Request:

```text
commit
→ syntax check
→ pytest
→ docker build
→ revisão
→ aprovação
→ merge por squash
```

Nenhum resultado deve ser considerado aprovado enquanto o workflow não estiver `completed` com `conclusion=success`.

## 8. Princípios obrigatórios

- testes independentes e determinísticos;
- banco isolado para cada execução;
- nenhuma foto ou biometria real;
- datas e horários controlados nos testes;
- mocks limitados às fronteiras externas;
- regras de negócio testadas diretamente;
- falhas devem deixar mensagem compreensível;
- correções devem incluir teste de regressão.

## 9. Matriz mínima de cobertura funcional

| Área | Teste unitário | Teste de integração |
|---|---:|---:|
| Autenticação administrativa | Sim | Sim |
| Cadastro de usuário | Parcial | Sim |
| Upload biométrico | Sim | Sim |
| Reconhecimento facial | Sim | Simulado no endpoint |
| Registro de ponto | Sim | Sim |
| Duplicidade | Sim | Sim |
| Jornada | Sim | Não aplicável inicialmente |
| Tolerâncias | Sim | Não aplicável inicialmente |
| Banco de horas | Sim | Não aplicável inicialmente |
| Fechamento mensal | Sim | Não aplicável inicialmente |
| Docker | Não | Build no CI |

## 10. Critérios para aprovação

```text
SYNTAX_CHECK=PASS
UNIT_TESTS=PASS
INTEGRATION_TESTS=PASS
DOCKER_BUILD=PASS
REAL_BIOMETRIC_TEST_DATA=NO
REGRESSION_TESTS_REQUIRED_FOR_FIXES=YES
```

## 11. Problemas conhecidos

- a suíte não mede ainda cobertura percentual;
- reconhecimento facial real depende de câmera, iluminação e qualidade da captura;
- não existe teste end-to-end completo em navegador;
- PostgreSQL de homologação ainda não faz parte do pipeline;
- backup e restauração ainda precisam de testes próprios.

## 12. Evoluções futuras

- adicionar relatório de cobertura;
- adicionar testes end-to-end com navegador;
- testar PostgreSQL em serviço isolado no CI;
- validar backup e restauração;
- criar conjunto de imagens sintéticas versionadas e autorizadas;
- adicionar testes de carga e concorrência para registro de ponto.
