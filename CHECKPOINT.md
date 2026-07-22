# Checkpoint Atual — Controle de Ponto Potiguar

Atualizado em: 22/07/2026

## Estado oficial

```text
REPOSITORY=leon337/reconhecimento_facial
DEFAULT_BRANCH=main
PROJECT_STATUS=PILOTO_LOCAL_AVANCADO
CURRENT_PHASE=FASE_10.1.1
MAIN_SHA=3908e639be2cd025e4a1eee044db21d1ef52d7ee
PROJECT_STATE=PROJECT_STATE.md
LINEAR_PARENT=LEA-85
```

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
IMPLEMENTATION_CONTINUATION=ALLOWED
PRODUCTION_HOMOLOGATION=BLOCKED
```

A migração para Vercel foi descartada neste momento. Qualquer futura migração para nuvem exige decisão arquitetural própria.

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
```

## Pendências preservadas

- executar as 20 marcações controladas antes de homologar ou ampliar o piloto;
- calcular média, mediana, P95, máximo e taxa de sucesso;
- registrar evidências finais;
- encerrar formalmente a FASE 10.1.1;
- revisar o PR #13;
- atualizar o manual antigo;
- documentar LGPD, retenção e exclusão de dados biométricos;
- validar backup, restauração e contingência operacional.

## Próxima ação

```text
NEXT_ACTION=CONTINUE_OFFICIAL_IMPLEMENTATION_ROADMAP
TEST_DEBT=LEA_95
NEXT_GATE_BEFORE_HOMOLOGATION=TWENTY_CONTROLLED_PUNCHES
```

## Regra de continuidade

Este arquivo representa o checkpoint mais recente do projeto. Em novo chat, consultar primeiro `CHECKPOINT.md`, depois `PROJECT_STATE.md` e, por fim, as issues relacionadas no Linear.