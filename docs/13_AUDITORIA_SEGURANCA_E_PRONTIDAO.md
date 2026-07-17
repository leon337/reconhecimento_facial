# 13 — Auditoria de Segurança e Prontidão

## 1. Objetivo

Registrar o estado de segurança observável do repositório e os bloqueios que impedem classificar o sistema como pronto para produção.

## 2. Escopo auditado

- autenticação administrativa;
- sessão e CSRF;
- upload de imagens;
- armazenamento biométrico;
- registro de ponto;
- banco e segredos;
- Docker e Gunicorn;
- testes automatizados;
- documentação de LGPD, deploy, backup e restauração.

## 3. Controles confirmados no código

| Controle | Estado | Evidência funcional |
|---|---|---|
| Autenticação administrativa | Implementado | acesso administrativo exige usuário com papel `admin` |
| Senha com hash | Implementado | modelo utiliza funções de hash do Werkzeug |
| Proteção CSRF | Implementado | Flask-WTF inicializado na aplicação |
| Cookie HTTPOnly | Implementado | configuração da aplicação |
| Cookie Secure em produção | Implementado | habilitado quando `APP_ENV=production` |
| SameSite | Implementado | `Lax` |
| `SECRET_KEY` obrigatória em produção | Implementado | inicialização bloqueia ausência |
| Validação de extensão | Implementado | PNG/JPG/JPEG |
| Validação do conteúdo da imagem | Implementado | Pillow verifica JPEG/PNG real |
| Nome de upload aleatório | Implementado | UUID |
| Limite de upload | Implementado | 5 MB |
| Bloqueio de batida duplicada | Implementado | janela configurável, padrão 60 s |
| Erros de reconhecimento controlados | Implementado | imagem inválida, nenhuma face, múltiplas faces e desconhecido |
| CI com testes e Docker | Implementado | workflow obrigatório no PR |

## 4. Achados críticos para produção

### SEC-01 — Dados biométricos sem criptografia em repouso comprovada

O encoding facial está armazenado como JSON em coluna de texto e a foto pode permanecer em diretório de uploads. Não há camada de criptografia em repouso demonstrada no código.

```text
SEVERIDADE=CRITICA
PRODUCAO=BLOCKED
```

### SEC-02 — Fotos servidas pelo diretório estático

A URL da foto de referência aponta para `static/uploads`. Isso facilita a operação atual, mas não é adequado como padrão de produção para dado biométrico sensível.

```text
SEVERIDADE=CRITICA
ACAO=armazenamento privado + autorização de acesso
```

### SEC-03 — Política de retenção ainda documental

A matriz LGPD define a necessidade, mas não existe rotina implementada e testada de expiração, anonimização ou exclusão segura.

```text
SEVERIDADE=ALTA
PRODUCAO=BLOCKED
```

### SEC-04 — SQLite como padrão

SQLite atende desenvolvimento e testes, mas o uso em produção concorrente deve ser decidido e validado. Não há migração formal nem estratégia de evolução de schema.

```text
SEVERIDADE=ALTA
ACAO=decisão arquitetural + migrações + teste de concorrência
```

### SEC-05 — Ausência de rate limiting e bloqueio de tentativas

O login valida credenciais, porém não há limitação de tentativas, atraso progressivo ou bloqueio temporário documentado no código.

```text
SEVERIDADE=ALTA
ACAO=implementar e testar antes da exposição pública
```

### SEC-06 — Auditoria de ações administrativas incompleta

Não há trilha persistente confirmada para login, logout, criação de usuário, cadastro biométrico, alteração e exclusão.

```text
SEVERIDADE=ALTA
ACAO=log de auditoria imutável e minimizado
```

### SEC-07 — Cabeçalhos HTTP e proxy ainda dependem do deploy

CSP, HSTS e demais cabeçalhos não estão demonstrados na aplicação ou em configuração versionada de proxy.

```text
SEVERIDADE=MEDIA
ACAO=validar em homologação
```

### SEC-08 — Backup e restauração não executados em ambiente real

O procedimento foi documentado, mas ainda não existe evidência de restauração bem-sucedida de um ambiente de homologação.

```text
SEVERIDADE=ALTA
PRODUCAO=BLOCKED
```

## 5. Resultado da auditoria

```text
AUTHENTICATION=PASS
PASSWORD_HASHING=PASS
CSRF=PASS
COOKIE_BASELINE=PASS
UPLOAD_VALIDATION=PASS
DUPLICATE_PROTECTION=PASS
AUTOMATED_TESTS=PASS
DOCKER_BUILD=PASS
DOCUMENTATION=PASS

BIOMETRIC_ENCRYPTION=FAIL
PRIVATE_BIOMETRIC_STORAGE=FAIL
RETENTION_AUTOMATION=FAIL
PRODUCTION_DATABASE_DECISION=PENDING
RATE_LIMITING=FAIL
ADMIN_AUDIT_TRAIL=FAIL
SECURITY_HEADERS=PENDING
RESTORE_EVIDENCE=PENDING

SECURITY_AUDIT=PASS_WITH_PRODUCTION_BLOCKERS
PRODUCTION_READY=NO
```

## 6. Gate para produção

A implantação com dados reais permanece proibida até:

```text
[ ] criptografia dos encodings biométricos
[ ] armazenamento privado das fotos ou remoção das fotos após geração do encoding
[ ] política de retenção implementada e testada
[ ] exclusão segura implementada e auditável
[ ] decisão e migração do banco de produção
[ ] rate limiting no login e endpoints sensíveis
[ ] trilha de auditoria administrativa
[ ] cabeçalhos de segurança validados
[ ] backup criptografado configurado
[ ] restauração de homologação comprovada
[ ] revisão jurídica/LGPD
[ ] teste de segurança e revisão independente
[ ] aprovação explícita do responsável
```

## 7. Testes recomendados para a próxima fase

### Unitários

- política de retenção;
- criptografia e descriptografia do encoding;
- autorização de acesso a arquivos;
- rate limiting;
- geração de eventos de auditoria.

### Integração

- cadastro biométrico sem exposição pública da foto;
- exclusão completa de usuário e biometria;
- restauração de backup;
- sessão segura atrás do proxy HTTPS;
- tentativas repetidas de login;
- persistência e consulta da trilha de auditoria.

## 8. Conclusão

A FASE 8 conclui a documentação e identifica claramente os controles existentes e as lacunas. Ela não autoriza produção. Os achados críticos devem virar uma fase técnica própria antes do uso de dados biométricos reais.
