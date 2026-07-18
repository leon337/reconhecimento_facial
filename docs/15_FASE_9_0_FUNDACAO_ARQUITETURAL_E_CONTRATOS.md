# FASE 9.0 — Fundação Arquitetural e Contratos

## 1. Objetivo

Introduzir limites arquiteturais e contratos testáveis antes da migração para PostgreSQL, multiempresa e biometria criptografada, preservando o comportamento legado.

## 2. Camadas

```text
web/API
  ↓
application
  ↓
domain

infrastructure
  ↑ implementa contratos da application
```

### Regras

- `domain` não importa Flask, SQLAlchemy, filesystem ou camadas externas;
- `application` depende de contratos e do domínio, não de infraestrutura;
- `infrastructure` contém adaptadores concretos;
- rotas e modelos legados permanecem operacionais durante a migração.

## 3. Contratos disponíveis

- `Clock`: tempo timezone-aware e injetável;
- `Repository`: persistência abstrata;
- `UnitOfWork`: transações com commit e rollback;
- `ObjectStorage`: armazenamento privado por chave opaca;
- `SecretBox`: criptografia contextual;
- `AuditSink`: auditoria imutável sem biometria aberta;
- `TenantContextProvider`: empresa e obra ativas;
- `IdempotencyStore`: reserva de operações mutáveis.

## 4. Contexto organizacional

`OrganizationalContext` exige empresa explícita e aceita obra opcional.

```text
empresa
empresa:obra
```

A aplicação não deverá depender de empresa global implícita.

## 5. Caso de uso mínimo

`ExecuteScopedCommand` estabelece o pipeline para operações mutáveis:

```text
comando
→ contexto empresa/obra
→ reserva de idempotência
→ unidade de trabalho
→ operação
→ auditoria
→ commit
```

Em falha, ocorre rollback e a chave idempotente é liberada. Esse caso de uso ainda não substitui as rotas atuais.

## 6. Adaptadores do legado

- `LegacyUserRepository` adapta o modelo `User` ao contrato `Repository`;
- `LegacySqlAlchemyUnitOfWork` adapta a sessão atual ao contrato transacional;
- filtros organizacionais inexistentes são rejeitados explicitamente;
- os adaptadores serão substituídos após PostgreSQL e Alembic na FASE 9.1.

## 7. Testes

Foram adicionados:

- testes unitários dos contratos;
- testes do contexto organizacional;
- testes de idempotência;
- testes do caso de uso escopado;
- testes de integração dos adaptadores legados;
- testes AST das regras de dependência;
- suíte legada e build Docker no CI.

O CI `run 73` foi concluído com sucesso antes da implementação dos casos de uso e adaptadores finais deste bloco.

## 8. Limites desta fase

Não fazem parte da FASE 9.0:

- migrations;
- PostgreSQL;
- alteração de schema;
- tabelas de empresa e obra;
- criptografia real da biometria;
- substituição imediata das rotas;
- dados reais.

## 9. Gates

```text
RUN_73=SUCCESS
LAYER_BOUNDARIES_DOCUMENTED=PASS
APPLICATION_CONTRACTS_CREATED=PASS
ORGANIZATIONAL_CONTEXT_CREATED=PASS
IDEMPOTENCY_CONTRACT_CREATED=PASS
MINIMUM_USE_CASE_CREATED=PASS
LEGACY_ADAPTERS_CREATED=PASS
ARCHITECTURE_DEPENDENCY_TESTS_CREATED=PASS
LEGACY_BEHAVIOR_CHANGED=NO
DATABASE_SCHEMA_CHANGED=NO
REAL_BIOMETRIC_DATA_USED=NO
```

O encerramento da fase depende do CI final, revisão integral e aprovação explícita para merge.
