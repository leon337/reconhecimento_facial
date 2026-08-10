# Checkpoint Atual — Controle de Ponto Potiguar

Atualizado em: 10/08/2026

## Estado oficial reconciliado

```text
REPOSITORY=leon337/reconhecimento_facial
DEFAULT_BRANCH=main
MAIN_SHA=783ca912c38876e68c12439a0db3616bf2b29a1d
BASELINE_FUNCTIONAL_SHA=3908e639be2cd025e4a1eee044db21d1ef52d7ee
PROJECT_STATUS=PILOTO_LOCAL_AVANCADO
CURRENT_PHASE=FASE_12_LEA_133_EM_EXECUCAO
WORK_MODE=RESOLUCAO_DE_RESSALVAS
MCF_PROTOCOL=1.1
MCF_RISK_CLASS=C
PRF=docs/mcf/PRF_CPP_COMMERCIAL_REDESIGN_AI_OBS_001.md
```

## Gate humano de 10/08/2026

Leandro confirmou alinhamento com o Mestre e aprovou a direção estratégica proposta pelo Léo **com ressalvas**.

A ordem é vinculante:

```text
GATE_LEANDRO=APPROVED_WITH_RESERVATIONS
STRATEGIC_DIRECTION=APPROVED
RESOLVE_RESERVATIONS_FIRST=YES
LEA_133_START=AUTHORIZED
FUNCTIONAL_IMPLEMENTATION=BLOCKED
NEW_STRATEGIC_PHASE=BLOCKED_UNTIL_RESERVATIONS_RESOLVED
PRODUCTION_HOMOLOGATION=BLOCKED
LEGAL_CONFORMITY_DECLARED=NO
```

## FASE 11 — estado final

```text
LEA_125=Done
LEA_126_TO_132=Done
PR_29=MERGED
PR_29_MERGE_COMMIT=783ca912c38876e68c12439a0db3616bf2b29a1d
PR_29_SCOPE=DOCUMENTATION_ONLY
APPLICATION_CODE_CHANGED_BY_PR_29=NO
ROADMAP_AUTO_APPROVED_BY_PR_29=NO
```

O checkpoint anterior estava desatualizado ao registrar LEA-125 como `In Progress` e PR #29 como Draft aberto. Esta versão corrige essa divergência.

## FASE 10.1.1 — validação

### Validação funcional preservada

```text
NOTEBOOK=PASS
PHONE=PASS
LIVE_CAMERA_ONLY=PASS
MULTIFRAME_CAPTURE=PASS
AUTOMATIC_IDENTIFICATION=PASS
ENTRY=PASS
EXIT=PASS
UNKNOWN_FACE_REJECTION=PASS
TARGET_LT_10_SECONDS=PASS
FALSE_IDENTIFICATION_OBSERVED_IN_FUNCTIONAL_TESTS=NO
```

Tempos históricos observados:

```text
NOTEBOOK_ENTRY=2.6s
NOTEBOOK_EXIT=2.5s
PHONE_ENTRY=3.0s
PHONE_EXIT=2.8s
```

### Dívida estatística reconciliada

```text
LEA_95=Backlog
LEA_95_TECHNICAL_COMPLETION=NO
TWENTY_CONTROLLED_PUNCHES=NOT_EVIDENCED
LEA_96=Todo
LEA_97=Todo
LEA_98=Todo
STATISTICAL_VALIDATION=PENDING
PRODUCTION_HOMOLOGATION=BLOCKED
```

A LEA-95 havia sido marcada como `Done` no tracker sem evidência das 20 marcações. Em 10/08/2026 ela foi devolvida para `Backlog`, preservando a descrição `STATUS=DEFERRED` e o bloqueio de homologação.

## FASE 12 — LEA-133

```text
LEA_133=In_Progress
MISSION=CPP-COMMERCIAL-REDESIGN-AI-OBS-001
PRIMARY_OBJECTIVE=RESOLVE_RESERVATIONS_AND_ESTABLISH_DECISION_BASELINE
APPLICATION_CODE_CHANGE=NOT_AUTHORIZED_IN_THIS_BLOCK
DATABASE_MIGRATION=NOT_AUTHORIZED
DEPLOY=NOT_AUTHORIZED
```

### Ressalvas que precisam ser resolvidas

- [x] reconciliar PR #29 e LEA-125 com o estado real;
- [x] reabrir tecnicamente a LEA-95 no tracker;
- [x] registrar autorização humana e ativar LEA-133;
- [ ] reconciliar integralmente `PROJECT_STATE.md`, `ROADMAP_CURRENT.md` e Linear;
- [ ] produzir mapa auditável das leituras/escritas do modelo legado `Ponto`;
- [ ] produzir plano de convergência para `AttendanceEvent`, sem executar migração;
- [ ] documentar limites da observabilidade atual e telemetria faltante;
- [ ] documentar guardrails e arquitetura do primeiro módulo de IA;
- [ ] validar backup/restore em ambiente isolado;
- [ ] definir e testar contingência para câmera, rede, servidor e banco;
- [ ] executar 20 marcações controladas com operador e dispositivos disponíveis;
- [ ] calcular média, mediana, P95, máximo, taxa de sucesso e registrar falso positivo observado;
- [ ] executar auditoria independente das evidências;
- [ ] encerrar LEA-96, LEA-97, LEA-98 e LEA-85 somente quando os gates forem satisfeitos.

## Dependência do legado

O estado técnico já verificado mostra que `AttendanceEvent`, `AttendanceAdjustment` e `AttendanceClosure` existem, porém a rota viva de marcação ainda grava o modelo legado `Ponto`.

```text
PONTO_LIVE_WRITE=YES
ATTENDANCE_EVENT_LIVE_WRITE=NO
MIGRATION_PLAN=REQUIRED
MIGRATION_EXECUTION=NOT_AUTHORIZED
```

## Observabilidade — classificação atual

```text
HTTP_LOGS=REAL
REQUEST_ID=REAL
API_HEALTH=REAL
DATABASE_HEALTH=REAL
IN_MEMORY_METRICS=REAL_BUT_NON_DURABLE
PUNCH_PROCESSING_MS=REAL_PER_REQUEST
CAMERA_HEARTBEAT=UNAVAILABLE
STATION_HEARTBEAT=UNAVAILABLE
BACKUP_LAST_SUCCESS_TELEMETRY=UNAVAILABLE
QUEUE_TELEMETRY=UNAVAILABLE
AI_HEALTH=UNAVAILABLE
DURABLE_METRICS=UNAVAILABLE
```

Nenhum componente sem telemetria deve aparecer como saudável por inferência.

## IA — limites aprovados

O primeiro candidato estratégico continua sendo diagnóstico assistido + explicação de eventos, em modo somente leitura.

A IA pode analisar, explicar, resumir, recomendar e priorizar investigação. Ela não pode autonomamente:

- aprovar ou alterar jornada;
- alterar pagamento;
- punir colaborador;
- sobrescrever resultado biométrico;
- conceder acesso;
- excluir biometria;
- declarar fraude;
- declarar conformidade jurídica.

## Questões regulatórias

```text
REP_PTRP_ROLE=UNDECIDED
LEGAL_VALIDATION=REQUIRED
LGPD_BIOMETRICS=REQUIRES_SPECIALIZED_VALIDATION
PAdES_AFD_AEJ_RETENTION=REQUIRES_SPECIALIZED_VALIDATION
```

Nenhuma conclusão jurídica é derivada apenas de engenharia.

## Direção estratégica aprovada, ainda bloqueada para implementação

Após o fechamento das ressalvas e novo gate:

```text
NF_01=PRODUTO_E_DESIGN_SYSTEM
NF_02=REDESIGN_COMERCIAL
NF_03=EXPERIENCIA_OPERACIONAL
NF_04=OBSERVABILIDADE
NF_05=ARQUITETURA_E_PRIMEIRO_MODULO_IA
NF_06=IDENTIDADE_E_DISPOSITIVOS
NF_07=REAVALIACAO_DO_ROADMAP
NF_08=RETORNO_AS_VALIDACOES_TECNICAS_REMANESCENTES
```

Essa sequência está aprovada como direção estratégica, não como autorização para implementação imediata.

## Próxima ação

```text
NEXT_ACTION=COMPLETE_BASELINE_RECONCILIATION_AND_TECHNICAL_EVIDENCE_PLAN
NEXT_OPERATIONAL_ISSUE=LEA_133
NEXT_PHYSICAL_GATE=LEA_95_TWENTY_CONTROLLED_PUNCHES
NEXT_FUNCTIONAL_IMPLEMENTATION=BLOCKED
NEXT_HUMAN_GATE=AFTER_RESERVATIONS_RESOLVED
```

## Regra de continuidade

Consultar nesta ordem:

1. `CHECKPOINT.md`;
2. `PROJECT_STATE.md`;
3. `ROADMAP_CURRENT.md`;
4. `docs/mcf/PRF_CPP_COMMERCIAL_REDESIGN_AI_OBS_001.md`;
5. LEA-85, LEA-95 a LEA-98, LEA-125 e LEA-133 no Linear;
6. PRs e código aplicáveis.

O pipeline funciona como uma linha de montagem: cada estação só libera a seguinte quando a evidência exigida está presente.
