# Homologação Potiguar no Render — plano gratuito

**Finalidade:** permitir testes remotos do MVP do Controle de Ponto Potiguar sem trabalhadores, biometria ou registros reais.

## Arquitetura

- Serviço Render Web, plano **free**, runtime Docker.
- Branch exclusiva `deploy/potiguar-render-hml-20261111`; não representa a `main`.
- `scripts/render_hml_bootstrap.py` cria ou renova uma conta administrativa **fictícia** no SQLite efêmero.
- `scripts/render_hml_wsgi.py` impõe HTTP Basic Auth em todas as páginas, exceto `GET /health`; o login Flask/RBAC continua obrigatório depois.
- A API do Gemini não é ativada nem provisionada no Render. Nunca copiar a chave principal ou o cofre do notebook para o serviço público.
- Senhas fortes aleatórias configuradas como variáveis privadas do serviço Render, **não** no Git.
- `SESSION_COOKIE_SECURE=True` no gateway, via TLS público do Render.

## Comando de inicialização

```bash
python scripts/render_hml_bootstrap.py &&
exec gunicorn --bind "0.0.0.0:${PORT:-10000}" --workers 1 --timeout 120 scripts.render_hml_wsgi:app
```

## Limitações do plano gratuito

- **SQLite efêmero**: dados podem desaparecer após rebuild/redeploy/restart; não há migrações ou backup/restore homologados.
- A instância pode dormir e demorar para responder depois de inatividade.
- Não há SLA nem garantia de continuidade operacional.
- **Não utilizar para registrar jornada de trabalho oficial, coletar biometria real, cadastrar funcionários reais ou manter dados trabalhistas.**
- Para produção oficial: PostgreSQL durável, storage privado persistente, backups com restore testado, segurança/monitoramento, conformidade jurídica e LGPD, CI de release verde e domínio controlado.

## Critérios de teste

1. `GET /health` retorna HTTP 200.
2. Páginas administrativas sem autenticação HTTP Basic retornam HTTP 401.
3. Após a primeira autenticação, a aplicação Flask ainda exige login do usuário.
4. Conta sintética acessa o módulo Copiloto (modo prévia) e a lista de funcionários vazia.
5. Envio de credenciais inválidas não dá acesso.
6. `POTIGUAR_COPILOT_ENABLED=0`, sem chave Gemini e sem provisionamento externo.

**Autoridade:** LEANDRO autorizou utilizar o workspace Render confirmado em 11/11/2026, com proibição de contratar recursos pagos sem sua aprovação.
