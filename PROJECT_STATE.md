# Controle de Ponto Potiguar — Estado Oficial do Projeto

Atualizado em: 2026-08-10

## Identificação

```text
REPOSITORY=leon337/reconhecimento_facial
DEFAULT_BRANCH=main
MAIN_SHA_BEFORE_PR30=783ca912c38876e68c12439a0db3616bf2b29a1d
BASELINE_FUNCTIONAL_SHA=3908e639be2cd025e4a1eee044db21d1ef52d7ee
PROJECT_STATUS=PILOTO_LOCAL_AVANCADO
CURRENT_PHASE=FASE_12_LEA_133_BASELINE_COMPLETE
MISSION=CPP-COMMERCIAL-REDESIGN-AI-OBS-001
MCF_PROTOCOL=1.1
MCF_RISK_CLASS=C
PR_30=READY_FOR_FINAL_GREEN_CI_AND_BASELINE_MERGE
```

## Estado executivo

A FASE 11 está encerrada: PR #29 integrado, LEA-125 e LEA-126 a LEA-132 concluídas. O PR #29 foi documental e não autorizou automaticamente o roadmap nem declarou conformidade jurídica.

A FASE 12 foi autorizada em 10/08/2026 para resolver as oito ressalvas do gate `APPROVED_WITH_RESERVATIONS`. O trabalho foi consolidado no PR #30 com reconciliação de fontes, recuperação de evidências, mapa do legado `Ponto`, plano `AttendanceEvent`, observabilidade, IA, fronteira regulatória, backup/restore sintético, contingência e auditoria independente.

```text
STRATEGIC_DIRECTION=APPROVED
RESERVATIONS_1_TO_8=RESOLVED_AT_BASELINE_GOVERNANCE_ARCHITECTURE_LEVEL
NEXT_FUNCTIONAL_PHASE=BLOCKED_UNTIL_NEW_HUMAN_GATE
PRODUCTION_HOMOLOGATION=BLOCKED
LEGAL_CONFORMITY_DECLARED=NO
```

`RESOLVED` não significa que módulos futuros já foram implementados. Significa que as inconsistências abertas receberam fonte de verdade, decisão, evidência, plano, teste e/ou fronteira de autoridade.

## Validação facial

### Funcional

```text
NOTEBOOK=PASS
PHONE=PASS
LIVE_CAMERA_ONLY=PASS
MULTIFRAME_CAPTURE=PASS
AUTOMATIC_IDENTIFICATION=PASS
ENTRY=PASS
EXIT=PASS
UNKNOWN_FACE_REJECTION=PASS
FALSE_IDENTIFICATION_OBSERVED_IN_FUNCTIONAL_TESTS=NO
```

### LEA-95 — vinte marcações

A evidência histórica da própria issue confirma:

```text
LEA_95=Done
TOTAL_ATTEMPTS=20
NOTEBOOK_ATTEMPTS=10
PHONE_ATTEMPTS=10
SUCCESSFUL_ATTEMPTS=20_BY_OPERATOR_CONFIRMATION
SUCCESS_RATE=100_PERCENT_BY_OPERATOR_CONFIRMATION
FALSE_POSITIVES_REPORTED=0
ALL_TOTAL_TIMES_LT_10_SECONDS=REPORTED_PASS
```

A primeira reconciliação de 10/08 havia devolvido a tarefa a Backlog por leitura incompleta; a evidência histórica foi recuperada e a correção ficou registrada na trilha.

### LEA-96 — estatística conservadora

Os 20 tempos individuais não foram preservados nas fontes recuperáveis.

```text
LEA_96=Done
RESULT=PASS_WITH_WARNINGS
MAX_BOUND=<10s
P95_BOUND=<10s
EXACT_MEAN=UNAVAILABLE
EXACT_MEDIAN=UNAVAILABLE
EXACT_P95=UNAVAILABLE
EXACT_MAX=UNAVAILABLE
STRICT_P95_8S=NOT_PROVABLE
PRODUCTION_HOMOLOGATION=BLOCKED
```

Uma futura homologação estrita deve repetir a bateria persistindo cada tentativa.

## Domínio de jornada

O fluxo operacional continua escrevendo `Ponto`; `AttendanceEvent` existe e é imutável, mas ainda não recebe a escrita viva.

```text
PONTO_LIVE_WRITE=YES
PONTO_DUPLICATE_READ=YES
ATTENDANCE_EVENT_MODEL_EXISTS=YES
ATTENDANCE_EVENT_IMMUTABLE=YES
ATTENDANCE_EVENT_LIVE_WRITE=NO
PONTO_DEPENDENCY_MAP=COMPLETE
ATTENDANCE_EVENT_CONVERGENCE_PLAN=COMPLETE
MIGRATION_IMPLEMENTED=NO
```

O plano exige `User.employee_id`, preservação de empresa/obra/timestamp, idempotência, reconciliação, rollback e retirada gradual. A migração permanece para fase funcional autorizada separadamente.

## Observabilidade

Estado real:

```text
REQUEST_ID=REAL
STRUCTURED_HTTP_LOGS=REAL
API_HEALTH=REAL
DATABASE_HEALTH=REAL
IN_MEMORY_METRICS=REAL_NON_DURABLE
PUNCH_PROCESSING_MS=REAL_PER_REQUEST
AUDIT_EVENT=REAL
CAMERA_HEARTBEAT=TELEMETRY_UNAVAILABLE
STATION_HEARTBEAT=TELEMETRY_UNAVAILABLE
DURABLE_METRICS=TELEMETRY_UNAVAILABLE
PILOT_BACKUP_LAST_SUCCESS=TELEMETRY_UNAVAILABLE
QUEUE=NOT_IMPLEMENTED
AI=NOT_IMPLEMENTED
OFFLINE_SYNC=NOT_IMPLEMENTED
```

Política vigente: `SEM_TELEMETRIA != SAUDAVEL`.

## IA e governança

Primeiro candidato futuro: diagnóstico assistido + explicação de eventos, somente leitura.

A IA poderá analisar, resumir, explicar e recomendar investigação. Não poderá autonomamente aprovar/alterar ponto, alterar pagamento, punir colaborador, sobrescrever reconhecimento biométrico, conceder acesso, excluir biometria, declarar fraude ou conformidade jurídica.

Dados biométricos brutos, templates, chaves, senhas e tokens ficam fora do contrato padrão.

## Backup, restore e contingência

Production Validation run #71 (`31438214366`) passou após o hardening final:

```text
RUN_71=PASS
REGRESSION=143_PASSED
MIGRATIONS_UP_DOWN_UP=PASS
POSTGRES_BACKUP_CHECKSUM=PASS
POSTGRES_RESTORE_EMPTY_DB=PASS
BIOMETRIC_STORAGE_CHECKSUM_RESTORE=PASS
BIOMETRIC_DECRYPTION_WITH_KEY=PASS
BIOMETRIC_DECRYPTION_WITHOUT_KEY=EXPECTED_FAIL_PASS
LOGIN_AFTER_RESTORE=PASS
RBAC_AFTER_RESTORE=PASS
COMPANY_WORKSITE_SCOPE_AFTER_RESTORE=PASS
SYNTHETIC_PUNCH_AFTER_RESTORE=PASS
DATABASE_UNAVAILABLE_FAIL_CLOSED=PASS_STATUS_500
SYNTHETIC_KEY_LOG_MASKING=PASS
CI_DATABASE_RESTORE_DURATION=258ms
ARTIFACT_ID=9081842144
ARTIFACT_SHA256=d16350a5c77c2ac36c5d509764bf68f9fb8a5c142334d7a0caad3c27b3f53793
```

O exercício usa dados sintéticos e não substitui disaster recovery do piloto real. O runbook de contingência para câmera, rede, servidor e banco está documentado e proíbe falso sucesso ou biometria retroativa simulada.

## Auditoria independente

`docs/lea-133/09_AUDITORIA_INDEPENDENTE.md` registra:

```text
INDEPENDENT_AUDIT=COMPLETE
EMILY_VERDICT=APPROVE_WITH_WARNINGS_FOR_BASELINE_MERGE
FALSE_CLAIMS_FOUND=NO_AFTER_CORRECTIONS
```

Achados baixos não bloqueantes: warning de `.gitmodules` no post-job e `Query.get()` legado do SQLAlchemy. Eles não alteraram o resultado dos testes.

## Fronteira regulatória e comercial

A direção é preparar plataforma comercial multiempresa/multiobra, sem inferir enquadramento legal.

```text
CURRENT_REGULATORY_CLAIM=NONE
REP_P_CLASSIFICATION=VALIDACAO_ESPECIALIZADA_NECESSARIA
PTRP_CLASSIFICATION=VALIDACAO_ESPECIALIZADA_NECESSARIA
COLLECTOR_ROLE=VALIDACAO_ESPECIALIZADA_NECESSARIA
LGPD_BIOMETRICS=VALIDACAO_ESPECIALIZADA_NECESSARIA
ENGINEERING_CAN_DECLARE_COMPLIANCE=NO
```

## Oito ressalvas — estado final da baseline

```text
R1_STALE_BASELINE=RESOLVED
R2_LEA95_AMBIGUITY=RESOLVED
R3_LEA133_NOT_STARTED=RESOLVED
R4_PONTO_DEPENDENCY=RESOLVED_AS_AUDITED_MAP_AND_CONTROLLED_PLAN
R5_OBSERVABILITY_AMBIGUITY=RESOLVED_AS_TRUTH_MATRIX
R6_MISSING_TELEMETRY=RESOLVED_AS_TRUTHFUL_UNAVAILABLE_NOT_IMPLEMENTED_STATES
R7_LEGAL_AUTHORITY=RESOLVED_BY_SPECIALIST_BOUNDARY
R8_AI_AUTONOMY=RESOLVED_BY_GUARDRAILS
```

## Gates que continuam bloqueando homologação de produção

Eles foram separados das oito ressalvas e registrados na LEA-98:

```text
GATE_HOM_01=REPEAT_20_WITH_FULL_TIMING_DATASET
GATE_HOM_02=REAL_PILOT_DISASTER_RECOVERY
GATE_HOM_03=PHYSICAL_CAMERA_NETWORK_SERVER_DB_CONTINGENCY_DRILLS
RPO_PILOT=UNDECIDED
RTO_PILOT=UNMEASURED
LEGAL_SPECIALIST_VALIDATION=PENDING
PRODUCTION_HOMOLOGATION=BLOCKED
```

## Linear antes do merge da baseline

```text
LEA_95=Done
LEA_96=Done_PASS_WITH_WARNINGS
LEA_97=Done
LEA_98=Todo_PRODUCTION_GATES_OPEN
LEA_85=In_Progress_PRODUCTION_HOMOLOGATION_BLOCKED
LEA_133=In_Progress_READY_TO_CLOSE_ON_PR30_MERGE
```

## Próximo passo

Executar CI no último head documental, aplicar o gate delegado do Léo, fazer o merge do PR #30 como baseline da FASE 12 e fechar a LEA-133. O merge não autoriza automaticamente NF-01 nem qualquer outra fase funcional; a próxima autorização é um novo gate humano de Leandro.