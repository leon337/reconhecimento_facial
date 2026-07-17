# 09 — Deploy

## 1. Objetivo

Definir o processo controlado de implantação do Controle de Ponto Potiguar em homologação e produção.

## 2. Escopo

Este documento cobre Docker, Gunicorn, variáveis de ambiente, proxy reverso, HTTPS, banco de dados, validações e rollback. A implantação real em produção depende de aprovação explícita, revisão jurídica/LGPD e infraestrutura definida.

## 3. Ambientes

### Desenvolvimento

- dados sintéticos;
- SQLite local;
- `APP_ENV=development`;
- acesso restrito ao desenvolvedor;
- sem dados biométricos reais.

### Homologação

- dados fictícios;
- imagem Docker equivalente à produção;
- HTTPS;
- banco isolado;
- execução de testes funcionais e de restauração.

### Produção

- `APP_ENV=production`;
- `SECRET_KEY` forte e externa ao Git;
- banco persistente e protegido;
- HTTPS obrigatório;
- backup e monitoramento ativos;
- acesso administrativo restrito.

## 4. Pipeline de publicação

```text
branch da fase
→ testes locais
→ Pull Request
→ GitHub Actions
→ revisão
→ merge por squash
→ imagem de release
→ homologação
→ gate de produção
→ deploy
→ smoke tests
→ monitoramento
```

O pipeline funciona como uma linha de montagem: cada estação valida uma parte antes de liberar a próxima.

## 5. Build Docker

```bash
docker build -t controle-ponto-potiguar:local .
```

Execução local:

```bash
docker run --rm \
  -p 8000:8000 \
  -e APP_ENV=development \
  -e SECRET_KEY=trocar-em-producao \
  controle-ponto-potiguar:local
```

## 6. Variáveis obrigatórias

```text
APP_ENV=production
SECRET_KEY=<segredo forte>
DATABASE_URL=<conexão do banco>
PORT=8000
WEB_CONCURRENCY=1
```

O valor de `WEB_CONCURRENCY` deve ser validado conforme CPU, memória e comportamento das bibliotecas de reconhecimento facial.

## 7. Proxy reverso e HTTPS

A aplicação deve ficar atrás de Nginx, Caddy ou serviço equivalente.

Requisitos:

- certificado TLS válido;
- redirecionamento HTTP para HTTPS;
- limite de tamanho compatível com o upload de imagem;
- timeouts compatíveis com o processamento facial;
- cabeçalhos de segurança;
- acesso direto à porta do Gunicorn bloqueado externamente.

## 8. Banco de dados

O projeto ainda usa SQLite como padrão local. Produção com múltiplos acessos deve ser validada com banco adequado e migrações controladas antes da liberação.

Antes do deploy:

1. confirmar banco e volume persistente;
2. gerar backup;
3. testar restauração em ambiente isolado;
4. validar permissões;
5. impedir banco e credenciais no Git.

## 9. Smoke tests pós-deploy

Executar após cada implantação:

```text
[ ] aplicação responde por HTTPS
[ ] login administrativo abre
[ ] credencial inválida é rejeitada
[ ] listagem de usuários exige autenticação
[ ] upload inválido é rejeitado
[ ] página de ponto abre
[ ] registro sintético controlado responde corretamente
[ ] logs não exibem segredos
[ ] volume de dados permanece após reinício
```

## 10. Rollback

Em falha crítica:

1. interromper novas gravações;
2. preservar logs e evidências;
3. restaurar imagem anterior;
4. restaurar banco somente quando necessário e após validação;
5. executar smoke tests;
6. registrar incidente e causa.

## 11. Gate de produção

```text
CI=PASS
DOCUMENTACAO=PASS
SECURITY_REVIEW=PASS
LGPD_REVIEW=PASS
BACKUP_RESTORE_TEST=PASS
SECRETS_EXTERNALIZED=PASS
HTTPS=PASS
SMOKE_TESTS=PASS
OWNER_APPROVAL=PASS
```

Enquanto qualquer item estiver pendente, o deploy de produção permanece bloqueado.

## 12. Testes

- testes unitários e de integração com `pytest`;
- verificação de sintaxe com `compileall`;
- build Docker no GitHub Actions;
- smoke tests em homologação;
- teste de rollback;
- teste de backup e restauração.

## 13. Problemas conhecidos

- não há pipeline automático de deploy definido;
- não há migração formal para PostgreSQL;
- não há observabilidade centralizada;
- não há teste de carga documentado;
- produção ainda não está autorizada.
