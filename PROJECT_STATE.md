# Controle de Ponto Potiguar — Estado Oficial do Projeto

Atualizado em: 2026-08-10

## Identificação

```text
REPOSITORY=leon337/reconhecimento_facial
DEFAULT_BRANCH=main
MAIN_SHA=783ca912c38876e68c12439a0db3616bf2b29a1d
BASELINE_FUNCTIONAL_SHA=3908e639be2cd025e4a1eee044db21d1ef52d7ee
PROJECT_STATUS=PILOTO_LOCAL_AVANCADO
CURRENT_PHASE=FASE_12_LEA_133_FECHAMENTO
MISSION=CPP-COMMERCIAL-REDESIGN-AI-OBS-001
MCF_PROTOCOL=1.1
MCF_RISK_CLASS=C
PR_30=DRAFT_OPEN
```

## Estado executivo

A FASE 11 está documentalmente encerrada: PR #29 integrado, LEA-125 e LEA-126 a LEA-132 concluídas. O merge não alterou código funcional, não aprovou automaticamente o roadmap e não declarou conformidade jurídica.

A FASE 12 foi autorizada em 10/08/2026 para resolver as ressalvas do gate `APPROVED_WITH_RESERVATIONS`. O trabalho de reconciliação, arquitetura, evidência, testes automatizados e governança está no PR #30.

```text
STRATEGIC_DIRECTION=APPROVED
RESERVATION_RESOLUTION=AUTHORIZED
NEXT_FUNCTIONAL_PHASE=BLOCKED_UNTIL_NEW_HUMAN_GATE
PRODUCTION_HOMOLOGATION=BLOCKED
LEGAL_CONFORMITY_DECLARED=NO
```

## Estado da validação facial

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

### 20 marcações — LEA-95

A evidência histórica da própria issue confirma a execução das 20 tentativas.

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

A primeira reconciliação de 10/08 havia movido a LEA-95 indevidamente para Backlog; a leitura integral dos comentários recuperou a evidência e o tracker voltou para `Done`. A trilha foi mantida, não apagada.

### Métricas — LEA-96

Os 20 tempos individuais não foram recuperados. Portanto:

```text
LEA_96=Done
RESULT=PASS_WITH_WARNINGS
MAX_BOUND=<10s
P95_BOUND=<10s
EXACT_MEAN=UNAVAILABLE
EXACT_MEDIAN=UNAVAILABLE
EXACT_P95=UNAVAILABLE
EXACT_MAX=UNAVAILABLE
P95_TARGET_8S=NOT_PROVABLE
```

A limitação impede homologação estatística estrita. Uma futura homologação deve repetir a bateria preservando cada tentativa.

## Domínio de jornada

Existem `AttendanceEvent`, `AttendanceAdjustment` e `AttendanceClosure`, mas o fluxo operacional atual continua escrevendo `Ponto`.

A dependência foi mapeada no PR #30:

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

O plano futuro prevê mapeamento determinístico `User -> Employee`, preservação de empresa/obra/timestamp, idempotência, reconciliação, rollback e retirada gradual. Nenhuma migração destrutiva foi executada.

## Observabilidade

O estado real atual é uma fundação parcial:

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

A política `SEM_TELEMETRIA != SAUDAVEL` foi formalizada. A arquitetura futura usa health aggregator determinístico; IA apenas explica sinais existentes.

## IA e governança

O primeiro candidato futuro é diagnóstico assistido + explicação de eventos, somente leitura.

Pode futuramente analisar, resumir, explicar e recomendar investigação. Não pode autonomamente aprovar/alterar ponto, alterar pagamento, punir colaborador, sobrescrever biometria, conceder acesso, excluir biometria, declarar fraude ou conformidade jurídica.

Dados biométricos brutos, templates, chaves, senhas, tokens e payloads sensíveis ficam fora do contrato padrão de IA.

## Backup, restore e contingência

A Production Validation da branch da LEA-133 foi ampliada com fixture totalmente sintética para validar restauração isolada do banco e do armazenamento biométrico, dependência da chave, autenticação, RBAC, escopo empresa/obra e uma marcação sintética após restore.

O run #63 concluiu com sucesso:

```text
MIGRATIONS_UP_DOWN_UP=PASS
REGRESSION=143_PASSED
POSTGRES_BACKUP_CHECKSUM=PASS
POSTGRES_RESTORE_EMPTY_DB=PASS
BIOMETRIC_STORAGE_CHECKSUM_RESTORE=PASS
BIOMETRIC_DECRYPTION_WITH_KEY=PASS
BIOMETRIC_DECRYPTION_WITHOUT_KEY=EXPECTED_FAIL_PASS
LOGIN_AFTER_RESTORE=PASS
RBAC_AFTER_RESTORE=PASS
COMPANY_WORKSITE_AFTER_RESTORE=PASS
SYNTHETIC_PUNCH_AFTER_RESTORE=PASS
CI_DATABASE_RESTORE_DURATION=415ms
```

Um run posterior do PR #30 acrescenta máscara explícita da chave sintética e teste fail-closed para banco indisponível. O resultado final desse run deve ser anexado antes do encerramento.

Não há equivalência entre CI sintético e exercício físico do piloto:

```text
PILOT_REAL_DR_EXERCISE=NOT_EXECUTED_BY_CI
PHYSICAL_CAMERA_OUTAGE=REQUIRES_PILOT_OPERATOR
PHYSICAL_NETWORK_OUTAGE=REQUIRES_PILOT_OPERATOR
PHYSICAL_SERVER_OUTAGE=REQUIRES_PILOT_OPERATOR
RPO_PILOT=UNDECIDED
RTO_PILOT=UNMEASURED
```

O runbook de contingência está documentado e proíbe falso sucesso ou biometria retroativa simulada.

## Fronteira regulatória e comercial

A direção de produto é preparar uma plataforma comercial multiempresa/multiobra. Isso não define enquadramento jurídico.

```text
CURRENT_REGULATORY_CLAIM=NONE
REP_P_CLASSIFICATION=VALIDACAO_ESPECIALIZADA_NECESSARIA
PTRP_CLASSIFICATION=VALIDACAO_ESPECIALIZADA_NECESSARIA
COLLECTOR_ROLE=VALIDACAO_ESPECIALIZADA_NECESSARIA
LGPD_BIOMETRICS=VALIDACAO_ESPECIALIZADA_NECESSARIA
ENGINEERING_CAN_DECLARE_COMPLIANCE=NO
```

## Ressalvas do gate — estado

```text
1_STALE_BASELINE=RESOLVED
2_LEA95_AMBIGUITY=RESOLVED
3_LEA133_NOT_STARTED=RESOLVED
4_PONTO_DEPENDENCY=RESOLVED_AS_AUDITED_MAP_AND_MIGRATION_PLAN
5_OBSERVABILITY_AMBIGUITY=RESOLVED_AS_TRUTH_MATRIX_AND_ARCHITECTURE
6_MISSING_TELEMETRY=RESOLVED_AS_EXPLICIT_UNAVAILABLE_OR_NOT_IMPLEMENTED_STATES
7_LEGAL_AUTHORITY=RESOLVED_BY_SPECIALIST_BOUNDARY
8_AI_AUTONOMY=RESOLVED_BY_GUARDRAILS
```

`RESOLVED` aqui significa que a ressalva deixou de ser ambígua e ganhou decisão, evidência, plano e critério. Não significa que funcionalidades futuras, como métricas duráveis ou heartbeat de câmera, tenham sido implementadas nesta fase.

## Dívidas que permanecem como gates de homologação

```text
EXACT_20_TIMINGS=NOT_RECOVERED
STRICT_P95_8S=NOT_PROVABLE
PILOT_REAL_DR=NOT_YET_EXECUTED
PHYSICAL_OUTAGE_DRILLS=NOT_YET_EXECUTED
LEGAL_SPECIALIST_VALIDATION=PENDING
PRODUCTION_HOMOLOGATION=BLOCKED
```

Essas dívidas não são mascaradas para encerrar a FASE 12; são carregadas explicitamente para o gate apropriado.

## Situação de execução

```text
LEA_95=Done
LEA_96=Done_PASS_WITH_WARNINGS
LEA_97=In_Progress
LEA_98=Waiting_Final_Audit
LEA_85=In_Progress_Waiting_Final_Audit
LEA_133=In_Progress_Waiting_Final_Audit
PR_30=DRAFT_OPEN
```

## Próximo passo

Finalizar CI do head, consolidar evidências, realizar auditoria independente MCF, sincronizar LEA-97/98/85/133 e retornar a Leandro para o novo gate. Nenhuma nova implementação funcional é iniciada automaticamente.