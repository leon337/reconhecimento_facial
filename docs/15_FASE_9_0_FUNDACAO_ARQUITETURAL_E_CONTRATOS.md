# FASE 9.0 — Fundação Arquitetural e Contratos

## 1. Objetivo

Introduzir limites arquiteturais e contratos testáveis antes da migração para PostgreSQL, multiempresa e biometria criptografada.

## 2. Escopo deste primeiro bloco

- criar as camadas `domain`, `application` e `infrastructure`;
- declarar contratos para tempo, repositórios, transações, armazenamento privado, criptografia e auditoria;
- adicionar testes unitários dos contratos;
- preservar integralmente o comportamento legado;
- não alterar modelos SQLAlchemy nem schema nesta etapa.

## 3. Regra de dependências

```text
web/API
  ↓
application
  ↓
domain

infrastructure
  ↑ implementa contratos da application
```

### Permitido

- `application` importar `domain`;
- `infrastructure` importar contratos de `application`;
- web/API importar casos de uso de `application`.

### Proibido

- `domain` importar Flask, SQLAlchemy ou filesystem;
- `application` importar implementações concretas de infraestrutura;
- regras de negócio dependerem diretamente de `datetime.now()`;
- casos de uso gravarem arquivos em `static/uploads`;
- auditoria registrar encoding, imagem facial ou segredo em texto aberto.

## 4. Contratos iniciais

### Clock

Fornece tempo timezone-aware e injetável, permitindo testes determinísticos.

### Repository

Abstrai acesso a entidades e exige filtros de escopo organizacional nas futuras implementações multiempresa.

### UnitOfWork

Delimita transações e padroniza `commit` e `rollback`.

### ObjectStorage

Define armazenamento privado por chave opaca, sem exposição pública direta.

### SecretBox

Define criptografia autenticada de dados sensíveis em repouso.

### AuditSink

Registra eventos imutáveis sem incluir payload biométrico.

## 5. Estratégia de migração incremental

```text
contratos
→ adaptadores para o legado
→ casos de uso
→ PostgreSQL e Alembic
→ multiempresa
→ biometria segregada
```

As rotas existentes continuarão funcionando durante a transição. Cada nova implementação deverá entrar por contrato, com testes unitários e de integração.

## 6. Testes

O arquivo `tests/test_architecture_contracts.py` valida:

- relógio com timezone;
- ciclo de vida de armazenamento privado;
- round trip de criptografia sintética;
- auditoria sem payload biométrico.

As implementações de teste são intencionalmente simples e não representam algoritmos de produção.

## 7. Gates

```text
LAYER_BOUNDARIES_DOCUMENTED=PASS
APPLICATION_CONTRACTS_CREATED=PASS
CONTRACT_UNIT_TESTS_CREATED=PASS
LEGACY_BEHAVIOR_CHANGED=NO
DATABASE_SCHEMA_CHANGED=NO
REAL_BIOMETRIC_DATA_USED=NO
```

## 8. Próxima entrega da FASE 9.0

- criar casos de uso mínimos para cadastro biométrico e registro de ponto;
- criar adaptadores do legado sem substituir as rotas de uma vez;
- adicionar teste arquitetural de dependências;
- definir contratos de contexto organizacional e idempotência.
