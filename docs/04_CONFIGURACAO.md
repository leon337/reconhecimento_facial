# Configuração — Controle de Ponto Potiguar

## 1. Objetivo

Documentar as configurações atualmente reconhecidas pela aplicação e separar parâmetros de desenvolvimento, testes, homologação e produção.

## 2. Princípio geral

Configurações sensíveis ou dependentes do ambiente devem ser fornecidas por variáveis de ambiente. Segredos, bancos, imagens e dados biométricos não devem ser gravados no Git.

## 3. Variáveis de ambiente

| Variável | Padrão | Obrigatória em produção | Finalidade |
|---|---:|---:|---|
| `APP_ENV` | `development` | Sim | Define o comportamento do ambiente |
| `SECRET_KEY` | chave insegura de desenvolvimento | Sim | Protege sessão e recursos criptográficos do Flask |
| `DATABASE_URL` | SQLite em `instance/ponto.db` | Sim, com banco apropriado | URI do SQLAlchemy |
| `PORT` | `5000` em `python main.py`; `8000` no Docker | Não | Porta HTTP interna |
| `FLASK_DEBUG` | `0` | Deve ser `0` | Ativa debug somente em desenvolvimento |
| `WEB_CONCURRENCY` | `1` | Conforme capacidade | Número de workers do Gunicorn |

## 4. Exemplo de desenvolvimento

```env
APP_ENV=development
SECRET_KEY=development-only-change-me
DATABASE_URL=sqlite:///instance/ponto.db
PORT=5000
FLASK_DEBUG=1
WEB_CONCURRENCY=1
```

A chave acima é apenas ilustrativa e não pode ser usada em produção.

## 5. Exemplo de produção

```env
APP_ENV=production
SECRET_KEY=<chave-longa-gerada-fora-do-repositorio>
DATABASE_URL=<uri-do-banco-de-producao>
PORT=8000
FLASK_DEBUG=0
WEB_CONCURRENCY=2
```

A aplicação interrompe a inicialização quando `APP_ENV=production` e `SECRET_KEY` não foi definida.

## 6. Configurações internas atuais

`main.py` define:

| Configuração Flask | Valor atual | Observação |
|---|---:|---|
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` | Evita rastreamento desnecessário |
| `UPLOAD_FOLDER` | `static/uploads` | Deve ser revisto antes de armazenar biometria real |
| `MAX_CONTENT_LENGTH` | 5 MB | Limite máximo da requisição de upload |
| `SESSION_COOKIE_HTTPONLY` | `True` | Impede acesso normal do JavaScript ao cookie |
| `SESSION_COOKIE_SAMESITE` | `Lax` | Reduz risco de envio entre sites |
| `SESSION_COOKIE_SECURE` | ativo em produção | Exige HTTPS no navegador |
| `WTF_CSRF_TIME_LIMIT` | 3600 s | Validade do token CSRF |
| `PUNCH_DUPLICATE_WINDOW_SECONDS` | 60 s | Janela padrão contra batidas duplicadas |

## 7. Banco de dados

### Desenvolvimento

O padrão atual é:

```text
sqlite:///instance/ponto.db
```

### Homologação e produção

Usar um banco separado e uma conta com privilégios mínimos. Antes da produção, o projeto deve adotar migrações versionadas e testar backup e restauração.

Não usar `db.create_all()` como substituto definitivo de migrações em produção.

## 8. Upload e reconhecimento facial

A aplicação cria o diretório configurado em `UPLOAD_FOLDER` e limita uploads a 5 MB.

Requisitos antes de biometria real:

- validar extensão, MIME e conteúdo real do arquivo;
- impedir nomes de arquivo controlados pelo usuário;
- armazenar fora da área pública quando aplicável;
- criptografar dados biométricos em repouso;
- limitar acesso por função;
- registrar operações de cadastro, consulta e exclusão;
- definir retenção e descarte seguro.

O caminho dos modelos de reconhecimento é configurado por `FACE_RECOGNITION_MODEL_LOCATION` durante a criação da aplicação.

## 9. Jornada e tolerâncias

A jornada aceita formatos como:

```text
08:00-17:00
08:00-12:00,13:00-17:00
```

As regras implementadas na FASE 7 incluem:

- atraso padrão tolerado até 5 minutos;
- hora extra inferior a 10 minutos não contabilizada;
- saldo de até 5 minutos neutralizado;
- preservação dos valores brutos para auditoria;
- rejeição de tolerâncias negativas.

Os nomes e a origem definitiva desses parâmetros devem ser centralizados em configuração antes de serem expostos ao administrador.

## 10. Banco de horas e fechamento

A consolidação usa somente o saldo tratado pelas tolerâncias e separa créditos e débitos. O fechamento mensal deve bloquear períodos com registros incompletos e rejeitar registros de outro mês.

Antes da produção, definir:

- persistência do fechamento;
- responsável pela aprovação;
- política para reabertura;
- trilha de auditoria;
- regra para ajustes retroativos;
- integração com folha de pagamento.

## 11. Configuração para testes

A fábrica `create_app(test_config=...)` permite substituir configurações sem acessar banco e diretórios reais.

Exemplo conceitual:

```python
app = create_app(
    {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    }
)
```

Testes unitários devem exercitar regras isoladas. Testes de integração devem usar banco e diretórios temporários e verificar respostas HTTP e persistência.

## 12. Checklist por ambiente

### Desenvolvimento

```text
[ ] Dados exclusivamente sintéticos
[ ] Debug restrito ao computador local
[ ] Banco local ignorado pelo Git
[ ] Segredos fora do repositório
```

### Homologação

```text
[ ] Dados fictícios
[ ] HTTPS
[ ] Banco separado
[ ] Testes de integração executados
[ ] Backup e restauração ensaiados
```

### Produção

```text
[ ] Revisão jurídica e LGPD
[ ] SECRET_KEY forte
[ ] HTTPS obrigatório
[ ] Debug desativado
[ ] Banco com privilégios mínimos
[ ] Biometria criptografada
[ ] Logs e auditoria
[ ] Backup restaurável
[ ] Plano de incidente
[ ] Aprovação formal de deploy
```
