# LEA-133 — Pacote consolidado de evidências

**Data:** 10/08/2026  
**Missão:** `CPP-COMMERCIAL-REDESIGN-AI-OBS-001`  
**Gate de entrada:** `APPROVED_WITH_RESERVATIONS`  
**PR de trabalho:** #30  

## 1. Regra de prova

Este pacote distingue quatro estados:

```text
PROVADO
PROVADO_COM_LIMITACAO
PLANEJADO_NAO_IMPLEMENTADO
DEPENDENCIA_EXTERNA
```

Nenhum item `PLANEJADO_NAO_IMPLEMENTADO` ou `DEPENDENCIA_EXTERNA` é apresentado como funcionalidade pronta.

## 2. Baseline e governança

| Evidência | Resultado |
|---|---|
| `main` antes da missão | `783ca912c38876e68c12439a0db3616bf2b29a1d` |
| PR #29 | merged |
| LEA-125 a LEA-132 | Done |
| PR #29 alterou app? | não; documentação apenas |
| LEA-133 | iniciada com autorização humana |
| PRF MCF | criado, Classe C |
| nova fase funcional | bloqueada até novo gate |
| declaração jurídica | não autorizada |

Classificação: `PROVADO`.

## 3. LEA-95 — 20 marcações

A leitura integral do histórico da Linear recuperou confirmação operacional explícita das 20 tentativas, registrada após a execução física de 22/07/2026.

```text
TOTAL_ATTEMPTS=20
NOTEBOOK_ATTEMPTS=10
PHONE_ATTEMPTS=10
SUCCESSFUL_ATTEMPTS=20_BY_OPERATOR_CONFIRMATION
SUCCESS_RATE=100_PERCENT_BY_OPERATOR_CONFIRMATION
FALSE_POSITIVES_REPORTED=0
ALL_TOTAL_TIMES_LT_10_SECONDS=REPORTED_PASS
LIVE_CAMERA_ONLY=YES
```

Três registros visuais preservados para telefone:

```text
TOTAL=2.9s,2.9s,2.8s
PROCESSING=0.9s,0.9s,0.9s
```

Classificação: `PROVADO_COM_LIMITACAO`, porque a execução está confirmada, mas a série completa de tempos não foi preservada.

## 4. LEA-96 — métricas

Valores suportados:

```text
TOTAL=20
SUCCESS_RATE=100_PERCENT_BY_OPERATOR_CONFIRMATION
FALSE_POSITIVE=0_REPORTED
MAX_BOUND=<10s
P95_BOUND=<10s
```

Valores não recuperáveis:

```text
EXACT_MEAN=UNAVAILABLE
EXACT_MEDIAN=UNAVAILABLE
EXACT_P95=UNAVAILABLE
EXACT_MAX=UNAVAILABLE
STRICT_P95_8S=NOT_PROVABLE
```

Resultado formal:

```text
LEA_96=Done
RESULT=PASS_WITH_WARNINGS
WARNING=EXACT_DISTRIBUTION_NOT_RECOVERABLE
PRODUCTION_HOMOLOGATION=BLOCKED
```

Classificação: `PROVADO_COM_LIMITACAO`.

## 5. Dependência do legado `Ponto`

Inspeção do código confirmou:

```text
POST_/punch -> Ponto.from_user -> db.session.add -> commit
check_duplicate_punch -> Ponto.query
AttendanceEvent=EXISTS_AND_IMMUTABLE
AttendanceEvent_live_write=NO
```

O mapa de convergência documenta ponte `User.employee_id`, mapeamento de tipos, preservação de escopo/timestamp, idempotência, reconciliação, rollback e retirada gradual.

Classificação do mapa/plano: `PROVADO`.  
Classificação da migração: `PLANEJADO_NAO_IMPLEMENTADO`.

## 6. Observabilidade

Sinais existentes confirmados no código:

```text
REQUEST_ID
STRUCTURED_HTTP_LOGS
API_HEALTH
DATABASE_HEALTH_SELECT_1
IN_MEMORY_METRICS
PER_REQUEST_DURATION
PUNCH_PROCESSING_MS
AUDIT_EVENT
```

Sinais ausentes ou ainda não aplicáveis:

```text
CAMERA_HEARTBEAT=TELEMETRY_UNAVAILABLE
STATION_HEARTBEAT=TELEMETRY_UNAVAILABLE
DURABLE_METRICS=TELEMETRY_UNAVAILABLE
PILOT_BACKUP_LAST_SUCCESS=TELEMETRY_UNAVAILABLE
QUEUE=NOT_IMPLEMENTED
AI=NOT_IMPLEMENTED
OFFLINE_SYNC=NOT_IMPLEMENTED
```

Política formalizada:

```text
SEM_TELEMETRIA != SAUDAVEL
```

Classificação da verdade operacional: `PROVADO`.  
Health aggregator/métricas duráveis/heartbeats: `PLANEJADO_NAO_IMPLEMENTADO`.

## 7. IA

Arquitetura do primeiro candidato:

```text
IA_DIAGNOSTICO + IA_EXPLICACAO_EVENTOS
MODE=READ_ONLY
```

Guardrails proíbem decisão autônoma sobre jornada, pagamento, punição, biometria, acesso, exclusão de biometria, fraude e conformidade jurídica. Dados biométricos brutos, templates, chaves e segredos ficam fora do contrato padrão.

Classificação da arquitetura/policy: `PROVADO` como decisão de projeto.  
Módulo de IA: `PLANEJADO_NAO_IMPLEMENTADO`.

## 8. Backup/restore isolado — run #63

Production Validation:

```text
RUN_ID=31437529880
JOB_ID=93614885716
RESULT=PASS
REGRESSION=143_PASSED
WARNINGS=26_NON_BLOCKING
MIGRATIONS_UP_DOWN_UP=PASS
POSTGRES_BACKUP=PASS
BACKUP_CHECKSUM=PASS
POSTGRES_RESTORE_EMPTY_DB=PASS
CI_DATABASE_RESTORE_DURATION=415ms
BIOMETRIC_STORAGE_RESTORE_CHECKSUM=PASS
BIOMETRIC_DECRYPT_WITH_KEY=PASS
BIOMETRIC_DECRYPT_WITHOUT_KEY=EXPECTED_FAIL_PASS
LOGIN_AFTER_RESTORE=PASS
RBAC_AFTER_RESTORE=PASS
ORG_SCOPE_AFTER_RESTORE=PASS
SYNTHETIC_PUNCH_AFTER_RESTORE=PASS
COMPOSE=PASS
```

Artefato:

```text
ARTIFACT_ID=9081579094
NAME=production-validation-report
SIZE_BYTES=6538
ZIP_SHA256=80a3aa236cdc1698c54b23cef52dcf1d6450fd00cafbd84893f4cb7a086c5eca
```

A execução usou dados sintéticos. A chave gerada no run #63 também era sintética; após auditoria de higiene, o workflow foi endurecido para mascará-la explicitamente nos logs dos runs seguintes.

Classificação do restore sintético: `PROVADO`.

## 9. Contingência

Runbook definido para:

- câmera indisponível;
- rede indisponível;
- servidor indisponível;
- banco indisponível;
- registro manual auditável;
- reconciliação futura sem biometria retroativa simulada.

O workflow posterior ao run #63 adiciona teste automatizado para provar que banco indisponível produz erro em vez de estado saudável.

Classificação do runbook: `PROVADO` como procedimento.  
Exercícios físicos de câmera/rede/servidor: `DEPENDENCIA_EXTERNA` do ambiente piloto.

## 10. Fronteira regulatória

```text
TARGET_PRODUCT=COMMERCIAL_MULTI_COMPANY_TIME_ATTENDANCE_PLATFORM
CURRENT_REGULATORY_CLAIM=NONE
REP_P=VALIDACAO_ESPECIALIZADA_NECESSARIA
PTRP=VALIDACAO_ESPECIALIZADA_NECESSARIA
COLLECTOR_ROLE=VALIDACAO_ESPECIALIZADA_NECESSARIA
LGPD_BIOMETRICS=VALIDACAO_ESPECIALIZADA_NECESSARIA
```

Classificação: `PROVADO` como fronteira de autoridade; conclusão jurídica continua `DEPENDENCIA_EXTERNA`.

## 11. Dívidas preservadas

```text
EXACT_20_TIMINGS=NOT_RECOVERED
STRICT_P95_8S=NOT_PROVABLE
PILOT_REAL_DR=NOT_EXECUTED_BY_CI
PHYSICAL_OUTAGE_DRILLS=NOT_EXECUTED_BY_CI
RPO_PILOT=UNDECIDED
RTO_PILOT=UNMEASURED
LEGAL_SPECIALIST_REVIEW=PENDING
PRODUCTION_HOMOLOGATION=BLOCKED
```

Esses itens não invalidam a resolução das ambiguidades de arquitetura/governança da FASE 12, mas continuam bloqueando qualquer alegação de homologação de produção.

## 12. Artefatos produzidos

```text
docs/mcf/PRF_CPP_COMMERCIAL_REDESIGN_AI_OBS_001.md
docs/lea-133/01_RECONCILIACAO_EVIDENCIAS.md
docs/lea-133/02_MAPA_LEGADO_PONTO_E_PLANO_ATTENDANCE_EVENT.md
docs/lea-133/03_OBSERVABILIDADE_IA_E_GUARDRAILS.md
docs/lea-133/04_BACKUP_RESTORE_E_CONTINGENCIA.md
docs/lea-133/05_DECISAO_ARQUITETURAL_REGULATORIA.md
docs/lea-133/06_LEA96_METRICAS_E_CLASSIFICACAO.md
docs/lea-133/07_EVIDENCIAS_EXECUCAO.md
```

## 13. Estado para auditoria independente

```text
BASELINE=RECONCILED
LEA_95=Done
LEA_96=Done_PASS_WITH_WARNINGS
PONTO_MAP=COMPLETE
ATTENDANCE_PLAN=COMPLETE
OBSERVABILITY_TRUTH_MATRIX=COMPLETE
AI_GUARDRAILS=COMPLETE
REGULATORY_BOUNDARY=COMPLETE
SYNTHETIC_RESTORE=PASS
CONTINGENCY_RUNBOOK=COMPLETE
FINAL_HEAD_CI=TO_BE_CONFIRMED_AFTER_LAST_DOCUMENTATION_COMMIT
INDEPENDENT_AUDIT=NEXT
```