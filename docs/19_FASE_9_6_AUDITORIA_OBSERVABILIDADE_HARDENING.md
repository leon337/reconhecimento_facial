# FASE 9.6 — Auditoria, observabilidade e hardening

## Objetivo

Adicionar controles operacionais e de segurança sem registrar senhas, templates faciais, imagens biométricas ou chaves.

## Entregas

- `AuditEvent` append-only com autor, empresa, obra, alvo, resultado e `request_id`;
- auditoria de login, logout, criação de usuário e cadastro biométrico;
- logs HTTP estruturados com duração e correlação;
- headers CSP, anti-frame, anti-MIME sniffing, referrer e permissions policy;
- HSTS quando cookies seguros estiverem ativos;
- sessão administrativa permanente com expiração configurada;
- limitação de tentativas de login por IP e identidade;
- respostas padronizadas para erros 404 e 500;
- endpoints `/health` e `/metrics`;
- migration Alembic reversível;
- testes unitários e de integração com dados sintéticos.

## Limites conhecidos

O limitador e as métricas permanecem em memória por processo. Na FASE 9.7, a infraestrutura deverá utilizar backend compartilhado para instalações com múltiplas réplicas.

## Testes

- unitários: limitador, imutabilidade e configuração;
- integração: login/logout auditados, health check, métricas, headers e contrato de erros;
- CI: testes, sintaxe e build Docker.
