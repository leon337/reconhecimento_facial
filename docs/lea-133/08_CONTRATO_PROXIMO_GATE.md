# LEA-133 — Contrato de entrada para o próximo gate

## 1. Finalidade

Este documento define o que o próximo gate pode autorizar e o que continua bloqueado. Ele **não** autoriza automaticamente uma nova fase.

## 2. Baseline que o próximo trabalho deve preservar

```text
FLASK_GUNICORN=PRESERVE
POSTGRESQL_ALEMBIC=PRESERVE
MULTITENANCY_COMPANY_WORKSITE=PRESERVE
RBAC=PRESERVE
AUDIT=PRESERVE
BIOMETRIC_TEMPLATE_ENCRYPTION=PRESERVE
PRIVATE_BIOMETRIC_STORAGE=PRESERVE
ONE_USE_CHALLENGE=PRESERVE
PASSIVE_MULTIFRAME_LIVENESS=PRESERVE
LIVE_CAMERA_PUNCH=PRESERVE
```

Qualquer regressão nesses invariantes bloqueia merge.

## 3. Direção estratégica candidata

A direção já aprovada conceitualmente é:

```text
NF_01=PRODUTO_E_DESIGN_SYSTEM
NF_02=REDESIGN_COMERCIAL
NF_03=EXPERIENCIA_OPERACIONAL
NF_04=OBSERVABILIDADE
NF_05=ARQUITETURA_E_PRIMEIRO_MODULO_IA
NF_06=IDENTIDADE_E_DISPOSITIVOS
NF_07=REAVALIACAO_DO_ROADMAP
NF_08=VALIDACOES_TECNICAS_REMANESCENTES
```

O próximo gate deve escolher explicitamente qual bloco iniciar. Aprovar NF-01 não significa aprovar automaticamente NF-02 a NF-08.

## 4. Condições obrigatórias para qualquer implementação seguinte

- branch e PR próprios;
- escopo explícito;
- critérios de aceitação antes do código;
- testes unitários e de integração definidos;
- regressão automática;
- nenhuma alteração destrutiva de dados sem plano de rollback;
- nenhum dado biométrico real em GitHub/IA;
- nenhuma declaração jurídica;
- nenhuma decisão trabalhista autônoma por IA;
- estados operacionais sustentados por fonte de verdade.

## 5. Dívidas que permanecem bloqueando homologação de produção

Mesmo que o próximo gate libere trabalho de produto/design/arquitetura, permanece proibido declarar produção homologada enquanto estiverem abertos:

```text
EXACT_20_TIMINGS=NOT_RECOVERED
STRICT_P95_8S=NOT_PROVABLE
PILOT_REAL_DR_EXERCISE=PENDING
PHYSICAL_OUTAGE_DRILLS=PENDING
RPO_PILOT=UNDECIDED
RTO_PILOT=UNMEASURED
LEGAL_SPECIALIST_VALIDATION=PENDING
```

## 6. Regra para o legado `Ponto`

O mapa e o plano existem, mas a migração não foi executada.

Qualquer fase que tocar persistência de jornada deve cumprir:

```text
NO_DESTRUCTIVE_CUTOVER_WITHOUT_RECONCILIATION
USER_TO_EMPLOYEE_MAPPING_REQUIRED
IDEMPOTENCY_REQUIRED
ROLLBACK_REQUIRED
HISTORICAL_TIMESTAMP_PRESERVATION_REQUIRED
COMPANY_WORKSITE_INVARIANTS_REQUIRED
DUPLICATE_PUNCH_RULE_MUST_MOVE_WITH_SOURCE_OF_TRUTH
```

## 7. Regra para observabilidade

```text
NO_TELEMETRY != HEALTHY
```

Dashboard futuro deve diferenciar saúde real, degradação, indisponibilidade, desconhecido e telemetria indisponível. Fila/IA/sync que ainda não existem devem aparecer como não implementados/não aplicáveis, não como serviço indisponível falso.

## 8. Regra para IA

O primeiro módulo candidato é diagnóstico assistido + explicação de eventos, somente leitura. Antes de implementação:

- contrato de dados sanitizados;
- lista de campos proibidos;
- timeout/fallback/circuit breaker;
- testes de policy;
- avaliação contra incidentes conhecidos;
- `cannot_conclude` quando faltarem sinais;
- auditoria apropriada.

## 9. Gate humano esperado

O resultado da FASE 12 deve chegar a Leandro em uma destas formas:

```text
APPROVE_NEXT_BLOCK
APPROVE_NEXT_BLOCK_WITH_RESERVATIONS
HOLD
REJECT
```

Até essa decisão:

```text
NEXT_FUNCTIONAL_PHASE=BLOCKED
PR_30_MERGE_MAY_CLOSE_BASELINE_ONLY
PRODUCTION_HOMOLOGATION=BLOCKED
```

## 10. Contrato de saída

```text
FASE_12_OUTPUT=DECISION_BASELINE
AUTOMATIC_NEXT_PHASE=NO
AUTOMATIC_PRODUCTION_HOMOLOGATION=NO
AUTOMATIC_LEGAL_CLAIM=NO
NEXT_ACTION_AFTER_AUDIT=HUMAN_GATE
```