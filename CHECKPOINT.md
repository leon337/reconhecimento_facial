# Checkpoint Atual — Controle de Ponto Potiguar

Atualizado em: 22/07/2026

## Estado oficial

```text
REPOSITORY=leon337/reconhecimento_facial
DEFAULT_BRANCH=main
PROJECT_STATUS=PILOTO_LOCAL_AVANCADO
CURRENT_PHASE=FASE_10.1.1_EM_FECHAMENTO
BASELINE_FUNCTIONAL_SHA=3908e639be2cd025e4a1eee044db21d1ef52d7ee
PROJECT_STATE=PROJECT_STATE.md
ROADMAP=ROADMAP_CURRENT.md
LINEAR_PARENT=LEA-85
NEXT_PHASE=LEA-133_FASE_12
```

## Objetivo preservado

Evoluir o piloto facial para uma plataforma simples, segura, auditável e multiobra de controle de jornada, adequada a equipes externas e locais com conectividade limitada.

Nenhuma alegação de conformidade jurídica está autorizada sem validação especializada.

## PR #28

```text
PULL_REQUEST=28
AUTHORIZED_HEAD=53483aa139ab6b810f54427ef544c7f9550f7103
MERGE_METHOD=SQUASH
MERGED=YES
MERGE_COMMIT=3908e639be2cd025e4a1eee044db21d1ef52d7ee
CI_175=SUCCESS
PRODUCTION_VALIDATION_44=SUCCESS
```

## Validação funcional

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
FALSE_IDENTIFICATION_OBSERVED=NO
```

Tempos observados:

```text
NOTEBOOK_ENTRY=2.6s
NOTEBOOK_EXIT=2.5s
PHONE_ENTRY=3.0s
PHONE_EXIT=2.8s
PHONE_PROCESSING_ENTRY=0.9s
PHONE_PROCESSING_EXIT=0.8s
```

## Infraestrutura atual

```text
APPLICATION=Flask/Gunicorn
DATABASE=PostgreSQL 16 local em Docker
MIGRATIONS=Alembic
TLS=Caddy
LAN_IP=192.168.10.101
BIOMETRIC_STORAGE=volume persistente separado e criptografado
SUPABASE=NOT_IN_USE
VERCEL=NOT_CONFIGURED
HOSTING=LINUX_MINT_LOCAL_PILOT
```

## Decisões vigentes

```text
VERCEL_MIGRATION=NOT_AUTHORIZED
LOCAL_PILOT=KEEP
LEA_95=DEFERRED_TO_BACKLOG
IMPLEMENTATION_CONTINUATION=ALLOWED_UNDER_GOVERNANCE
PRODUCTION_HOMOLOGATION=BLOCKED
ROADMAP_13_TO_21_APPROVED=NO
LEGAL_CONFORMITY_DECLARED=NO
```

## FASE 11 — pesquisa e escopo

```text
LEA_125=In_Progress
PR_29=OPEN_DRAFT
PR_29_MERGED=NO
DOCUMENTS=14_MARKDOWN_FILES
CATALOGUE=84_FUNCTIONS
ANALYSIS_COMPLETED=YES
LINEAR_RECONCILIATION=PENDING
```

O conteúdo analítico existe no PR #29, mas ainda exige revisão formal, merge autorizado e reconciliação de LEA-125 e LEA-126 a LEA-132.

## Linear

```text
LEA_85=In_Progress
LEA_93=Done
LEA_94=Done
LEA_95=Backlog_DEFERRED
LEA_96=Todo
LEA_97=Todo
LEA_98=Todo
LEA_118=Done
LEA_119=Documentation_Sync
LEA_125=In_Progress
LEA_126_TO_132=STATUS_RECONCILIATION_PENDING
LEA_133=NEXT_CONFIRMED_PHASE_NOT_STARTED
```

## Próxima fase — LEA-133

A FASE 12 deve ser executada como linha de montagem de validação:

```text
20_MARCACOES
    -> METRICAS
    -> RESTORE_ISOLADO
    -> CONTINGENCIA
    -> MAPA_DO_LEGADO_PONTO
    -> PLANO_ATTENDANCE_EVENT
    -> DECISAO_REP_PTRP
    -> BASELINE_APROVADA
```

Checklist essencial:

- [ ] revisar e reconciliar o PR #29;
- [ ] autorizar formalmente o início da LEA-133;
- [ ] executar 20 marcações controladas;
- [ ] calcular média, mediana, P95, máximo e taxa de sucesso;
- [ ] validar backup e restore isolado;
- [ ] testar contingência de câmera, rede, servidor e banco;
- [ ] mapear o modelo legado `Ponto`;
- [ ] definir migração futura para `AttendanceEvent` sem implementá-la;
- [ ] preservar multitenancy, RBAC, auditoria, criptografia e liveness;
- [ ] registrar decisão REP/PTRP com separação jurídica;
- [ ] encerrar formalmente a FASE 10.1.1;
- [ ] escolher explicitamente a próxima fase.

## Roadmap futuro — não autorizado

```text
FASE_13=NUCLEO_IMUTAVEL_E_COMPROVANTE
FASE_14=DIVERGENCIAS_E_APROVACOES
FASE_15=JORNADAS_E_CALCULOS
FASE_16=RELATORIOS_E_FECHAMENTO
FASE_17=SEGURANCA_E_PRIVACIDADE_COMERCIAL
FASE_18=OFFLINE_MOBILIDADE_GEOLOCALIZACAO
FASE_19=V1_COMERCIAL_MULTIOBRA
FASE_20=API_E_INTEGRACOES
FASE_21=ANTIFRAUDE_E_DIFERENCIAIS
```

Essas fases são propostas do mapa. Nenhuma implementação está autorizada antes do gate da FASE 12.

## Pendências preservadas

- concluir a validação estatística;
- registrar evidências finais;
- encerrar formalmente a FASE 10.1.1;
- validar restore e contingência;
- revisar o PR #29 e reconciliar o Linear;
- mapear e planejar retirada do legado `Ponto`;
- decidir o papel arquitetural REP/PTRP;
- revisar o PR #13;
- atualizar o manual antigo;
- documentar LGPD, retenção e exclusão de dados biométricos.

## Próxima ação

```text
NEXT_ACTION=REVIEW_PR_29_AND_RECONCILE_LEA_125_TO_132
NEXT_OPERATIONAL_PHASE=LEA_133_FASE_12
TEST_DEBT=LEA_95
NEXT_GATE_BEFORE_HOMOLOGATION=TWENTY_CONTROLLED_PUNCHES
NEXT_FUNCTIONAL_IMPLEMENTATION=NOT_AUTHORIZED
NEXT_HUMAN_GATE=AUTHORIZE_LEA_133_AFTER_DOCUMENTAL_SYNC
```

## Regra de continuidade

Em novo chat, consultar nesta ordem:

1. `ROADMAP_CURRENT.md`;
2. `CHECKPOINT.md`;
3. `PROJECT_STATE.md`;
4. LEA-85, LEA-125 e LEA-133 no Linear;
5. PRs e código relacionados.

Esse fluxo funciona como uma linha de montagem: o roadmap define a sequência, o checkpoint indica a estação atual, o estado oficial preserva a baseline e o Linear controla cada gate.
