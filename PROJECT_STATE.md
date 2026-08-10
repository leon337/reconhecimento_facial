# Controle de Ponto Potiguar — Estado Oficial do Projeto

Atualizado em: 2026-08-10

## Identificação

```text
REPOSITORY=leon337/reconhecimento_facial
DEFAULT_BRANCH=main
MAIN_SHA=783ca912c38876e68c12439a0db3616bf2b29a1d
BASELINE_FUNCTIONAL_SHA=3908e639be2cd025e4a1eee044db21d1ef52d7ee
PROJECT_STATUS=PILOTO_LOCAL_AVANCADO
CURRENT_PHASE=FASE_12_LEA_133_EM_EXECUCAO
MISSION=CPP-COMMERCIAL-REDESIGN-AI-OBS-001
MCF_PROTOCOL=1.1
MCF_RISK_CLASS=C
```

## Estado executivo reconciliado

O projeto permanece em piloto local avançado. A base funcional contém Flask/Gunicorn, PostgreSQL 16, Alembic, isolamento por empresa e obra, RBAC, criptografia biométrica, auditoria, backup/restore, Docker Compose, Caddy/HTTPS local, reconhecimento facial multiquadro, desafio de uso único e liveness passivo.

A FASE 10.1.1 possui validação funcional aprovada em notebook e telefone, porém continua sem homologação estatística porque as 20 marcações controladas da LEA-95 não possuem evidência de conclusão.

A FASE 11 foi concluída documentalmente: a LEA-125 e suas subtarefas foram concluídas e o PR #29 foi integrado na `main` pelo merge commit `783ca912c38876e68c12439a0db3616bf2b29a1d`. O PR #29 não alterou código funcional e não aprovou automaticamente um roadmap de implementação.

Em 10/08/2026, Leandro aprovou a nova direção estratégica proposta pelo Léo **com ressalvas** e autorizou o Mestre a convocar a equipe e iniciar os trabalhos de resolução dessas ressalvas. A LEA-133 foi movida para `In Progress`. A implementação funcional da nova direção continua bloqueada até o fechamento das pendências e novo gate.

## Gate vigente

```text
GATE_LEANDRO=APPROVED_WITH_RESERVATIONS
STRATEGIC_DIRECTION=APPROVED
RESERVATION_RESOLUTION=AUTHORIZED
LEA_133=In_Progress
FUNCTIONAL_IMPLEMENTATION=BLOCKED
PRODUCTION_HOMOLOGATION=BLOCKED
LEGAL_CONFORMITY_DECLARED=NO
NEXT_HUMAN_GATE=AFTER_RESERVATIONS_RESOLVED
```

## Estado da FASE 10.1.1

### Validação funcional

```text
NOTEBOOK_LOGIN=PASS
NOTEBOOK_BIOMETRIC_PROFILE=ACTIVE
NOTEBOOK_ENTRY=PASS
NOTEBOOK_EXIT=PASS
NOTEBOOK_ENTRY_TOTAL=2.6s
NOTEBOOK_EXIT_TOTAL=2.5s
PHONE_LOGIN=PASS
PHONE_CAMERA=PASS
PHONE_MULTIFRAME_CAPTURE=PASS_6_FRAMES
PHONE_ENTRY=PASS
PHONE_EXIT=PASS
PHONE_ENTRY_TOTAL=3.0s
PHONE_EXIT_TOTAL=2.8s
UNKNOWN_FACE_REJECTION=PASS
TARGET_LT_10_SECONDS=PASS
FALSE_IDENTIFICATION_OBSERVED_IN_FUNCTIONAL_TESTS=NO
```

### Validação estatística

```text
LEA_95=Backlog
TWENTY_CONTROLLED_PUNCHES=NOT_EVIDENCED
LEA_96=Todo
LEA_97=Todo
LEA_98=Todo
STATISTICAL_VALIDATION=PENDING
PRODUCTION_HOMOLOGATION=BLOCKED
```

A LEA-95 havia sido marcada como `Done`, mas sua própria descrição registrava `STATUS=DEFERRED` e `PRODUCTION_HOMOLOGATION=BLOCKED_UNTIL_COMPLETION`. Em 10/08/2026 o tracker foi reconciliado para `Backlog`.

## Infraestrutura oficial

```text
APPLICATION=Flask/Gunicorn
DATABASE=PostgreSQL 16 local em Docker
MIGRATIONS=Alembic
REVERSE_PROXY_TLS=Caddy
BIOMETRIC_STORAGE=volume persistente separado e criptografado
SUPABASE=NOT_IN_USE
VERCEL=NOT_CONFIGURED
HOSTING_DECISION=KEEP_LOCAL_PILOT
```

A migração para nuvem permanece fora do escopo desta etapa.

## Estado técnico relevante para a FASE 12

### Domínio de ponto

Existem `AttendanceEvent`, `AttendanceAdjustment` e `AttendanceClosure`, porém o fluxo vivo de marcação ainda grava `Ponto`.

```text
LEGACY_PONTO_MODEL=ACTIVE_IN_LIVE_WRITE_PATH
ATTENDANCE_EVENT_DOMAIN=EXISTS
LIVE_WRITE_TO_ATTENDANCE_EVENT=NO
DEPENDENCY_MAP=REQUIRED
MIGRATION_PLAN=REQUIRED
MIGRATION_EXECUTION=NOT_AUTHORIZED
```

A FASE 12 deve produzir inventário auditável das leituras/escritas do legado e plano de convergência com idempotência, reconciliação, rollback e preservação histórica.

### Observabilidade

A observabilidade existente é uma fundação parcial, não um sistema completo de saúde operacional.

```text
REQUEST_ID=REAL
STRUCTURED_HTTP_LOGS=REAL
API_HEALTH=REAL
DATABASE_HEALTH=REAL
IN_MEMORY_METRICS=REAL_NON_DURABLE
PER_REQUEST_PROCESSING_MS=REAL
CAMERA_HEARTBEAT=UNAVAILABLE
STATION_HEARTBEAT=UNAVAILABLE
DURABLE_METRICS=UNAVAILABLE
BACKUP_LAST_SUCCESS_TELEMETRY=UNAVAILABLE
QUEUE_TELEMETRY=UNAVAILABLE
AI_HEALTH=UNAVAILABLE
```

Regra: ausência de telemetria não pode ser convertida em estado verde.

### IA

Nenhum módulo de IA operacional está integrado ao produto atual.

O primeiro candidato estratégico é uma combinação de diagnóstico assistido e explicação de eventos, preferencialmente em modo somente leitura.

```text
AI_CAN_ANALYZE=YES_FUTURE
AI_CAN_EXPLAIN=YES_FUTURE
AI_CAN_SUMMARIZE=YES_FUTURE
AI_CAN_RECOMMEND=YES_FUTURE
AI_CAN_APPROVE_ATTENDANCE=NO
AI_CAN_CHANGE_PAY=NO
AI_CAN_PUNISH_EMPLOYEE=NO
AI_CAN_OVERRIDE_BIOMETRICS=NO
AI_CAN_GRANT_ACCESS=NO
AI_CAN_DELETE_BIOMETRICS=NO
AI_CAN_DECLARE_FRAUD=NO
AI_CAN_DECLARE_LEGAL_CONFORMITY=NO
```

## FASE 11 — estado final

```text
LEA_125=Done
LEA_126_TO_132=Done
PR_29=MERGED
PR_29_MERGE_COMMIT=783ca912c38876e68c12439a0db3616bf2b29a1d
PR_29_SCOPE=DOCUMENTATION_ONLY
CATALOGUED_FUNCTIONS=84
ROADMAP_AUTO_APPROVED=NO
```

## FASE 12 — objetivo atual

A FASE 12 não é expansão funcional. Ela é uma fase de fechamento, evidência e baseline.

Ordem de trabalho:

```text
RECONCILIAR_FONTES
  -> FECHAR_RASTREABILIDADE
  -> MAPEAR_PONTO
  -> PLANEJAR_ATTENDANCE_EVENT
  -> DOCUMENTAR_OBSERVABILIDADE
  -> DOCUMENTAR_GUARDRAILS_IA
  -> VALIDAR_BACKUP_RESTORE
  -> TESTAR_CONTINGENCIA
  -> EXECUTAR_20_MARCACOES
  -> CALCULAR_METRICAS
  -> AUDITORIA_INDEPENDENTE
  -> NOVO_GATE
```

## Ressalvas em acompanhamento

- [x] PR #29 e LEA-125 reconciliados com o estado real;
- [x] LEA-95 devolvida para estado tecnicamente coerente;
- [x] autorização humana registrada;
- [x] LEA-133 iniciada;
- [ ] documentos oficiais integralmente sincronizados;
- [ ] mapa de dependência `Ponto` concluído;
- [ ] plano `AttendanceEvent` concluído;
- [ ] limites e arquitetura de observabilidade documentados;
- [ ] guardrails e arquitetura de IA documentados;
- [ ] backup/restore isolado validado;
- [ ] contingência testada;
- [ ] 20 marcações controladas executadas;
- [ ] métricas calculadas;
- [ ] LEA-96/97/98 e LEA-85 fechadas conforme evidência;
- [ ] auditoria independente concluída.

## Direção estratégica pós-ressalvas

Leandro aprovou como direção estratégica, condicionada ao gate posterior:

1. NF-01 — Produto e Design System;
2. NF-02 — Redesign Comercial;
3. NF-03 — Experiência Operacional;
4. NF-04 — Observabilidade;
5. NF-05 — Arquitetura e Primeiro Módulo de IA;
6. NF-06 — Identidade e Dispositivos;
7. NF-07 — Reavaliação do Roadmap;
8. NF-08 — Retorno às validações técnicas remanescentes.

Essa aprovação define direção; não autoriza implementação imediata.

## Questões regulatórias

PAdES, REP-P, PTRP, AFD, AEJ, retenção, base legal de biometria e demais requisitos trabalhistas/privacidade permanecem sob:

```text
VALIDACAO_ESPECIALIZADA_NECESSARIA=YES
ENGINEERING_ONLY_DECISION=NO
LEGAL_CONFORMITY_DECLARED=NO
```

## Fontes de continuidade

Consultar em ordem:

1. `CHECKPOINT.md`;
2. `PROJECT_STATE.md`;
3. `ROADMAP_CURRENT.md`;
4. `docs/mcf/PRF_CPP_COMMERCIAL_REDESIGN_AI_OBS_001.md`;
5. LEA-85, LEA-95 a LEA-98, LEA-125 e LEA-133 no Linear;
6. PRs, código e evidências aplicáveis.

GitHub permanece como fonte técnica oficial. Linear deve representar fases, gates, relações e estado operacional. Divergências devem ser explicitadas, nunca ocultadas.
