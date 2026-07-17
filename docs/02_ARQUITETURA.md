# Arquitetura — Controle de Ponto Potiguar

## 1. Objetivo

Registrar a organização técnica do sistema, as responsabilidades dos componentes e o fluxo de dados entre interface, aplicação, reconhecimento facial, regras de jornada e persistência.

## 2. Visão arquitetural

```text
Navegador
   │
   ▼
Flask + Blueprints
   │
   ├── Área administrativa
   ├── Registro de ponto
   └── Proteção CSRF e sessão
   │
   ▼
Serviços e regras de domínio
   │
   ├── Reconhecimento facial
   ├── Jornada e tolerâncias
   ├── Bloqueio de duplicidade
   └── Banco de horas e fechamento
   │
   ▼
SQLAlchemy
   │
   ▼
Banco de dados
```

## 3. Ponto de entrada

`main.py` contém a fábrica `create_app()` e realiza:

- criação da aplicação Flask;
- leitura das variáveis de ambiente;
- configuração do banco;
- configuração de uploads e limite de 5 MB;
- configuração dos cookies de sessão;
- inicialização do SQLAlchemy e CSRF;
- registro dos blueprints administrativo e de ponto;
- criação das tabelas no contexto da aplicação.

A variável `APP_ENV=production` exige uma `SECRET_KEY` explícita e ativa cookie seguro.

## 4. Componentes principais

### 4.1 Administração

O blueprint administrativo concentra autenticação e operações protegidas relacionadas ao gerenciamento do sistema.

### 4.2 Registro de ponto

O pacote `app/punch` recebe a tentativa de batida, aplica validações, verifica duplicidade dentro da janela configurada e persiste somente registros válidos.

### 4.3 Jornada

`app/jornada.py` interpreta jornadas simples ou com intervalos, por exemplo:

```text
08:00-17:00
08:00-12:00,13:00-17:00
```

### 4.4 Cálculo diário

`app/calculo_jornada.py` calcula horas previstas, horas trabalhadas, atrasos, saída antecipada, saldo e registros incompletos. Os valores brutos são preservados para auditoria e os valores tratados respeitam as tolerâncias configuradas.

### 4.5 Banco de horas

`app/banco_horas.py` consolida créditos, débitos, saldo do período, saldo anterior e saldo acumulado. Dias incompletos são registrados como pendentes e não entram silenciosamente no saldo.

### 4.6 Reconhecimento facial

O reconhecimento usa `face-recognition`, `dlib`, NumPy, Pillow e os modelos do pacote `face_recognition_models`. A localização dos modelos é configurada durante a criação da aplicação.

## 5. Fluxo de uma batida

```text
Imagem recebida
      │
      ▼
Validação de formato e tamanho
      │
      ▼
Extração/comparação facial
      │
      ├── falha → rejeitar sem registrar
      │
      ▼
Identificação do colaborador
      │
      ▼
Regra de duplicidade
      │
      ├── duplicada → HTTP 409
      │
      ▼
Persistência da batida
      │
      ▼
Cálculo posterior da jornada
```

## 6. Configuração e dependências

As configurações principais vêm de variáveis de ambiente. O banco padrão local é SQLite em `instance/ponto.db`. Em produção, a URI deve ser fornecida por `DATABASE_URL`.

O Dockerfile usa Python 3.10 slim, instala dependências de compilação do `dlib`, instala `requirements.txt` e inicia Gunicorn na porta definida por `PORT`.

## 7. Testes

- testes unitários validam regras de domínio isoladas;
- testes de integração validam rotas, autenticação, persistência e respostas HTTP;
- GitHub Actions executa sintaxe, testes e build Docker.

## 8. Boas práticas arquiteturais

- manter regras de domínio fora das rotas;
- impedir persistência quando uma validação falhar;
- não misturar dados reais e dados de teste;
- registrar decisões de segurança e retenção;
- introduzir migrações antes de produção;
- testar restauração de backup, não apenas criação.

## 9. Evoluções futuras

- camada de serviços explícita;
- API REST versionada;
- PostgreSQL em homologação e produção;
- migrações com Alembic/Flask-Migrate;
- fila para processamento pesado;
- armazenamento biométrico criptografado e desacoplado;
- observabilidade e métricas.
