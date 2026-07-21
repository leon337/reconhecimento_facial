# Checkpoint Atual — Controle de Ponto Potiguar

Atualizado em: 21/07/2026

## Estado oficial

```text
REPOSITORY=leon337/reconhecimento_facial
DEFAULT_BRANCH=main
PROJECT_STATUS=PILOTO_LOCAL_AVANCADO
CURRENT_PHASE=FASE_10.1.1
MAIN_SHA=c1a6b550e6c6f137db67f4683e8609df2b0b6fcb
PROJECT_STATE=PROJECT_STATE.md
LINEAR_ISSUE=LEA-85
```

## Pull request ativo

```text
PULL_REQUEST=28
TITLE=HOTFIX FASE 10.1.1 — ponto facial multiquadro sem piscada
HEAD_SHA=53483aa139ab6b810f54427ef544c7f9550f7103
STATE=OPEN
DRAFT=YES
MERGEABLE=YES
CI=PASS
PRODUCTION_VALIDATION=PASS
MERGE=NOT_DONE
```

## Infraestrutura atual

```text
APPLICATION=Flask/Gunicorn
DATABASE=PostgreSQL 16 local em Docker
MIGRATIONS=Alembic
TLS=Caddy
SUPABASE=NOT_IN_USE
VERCEL=NOT_CONFIGURED
```

## Próximo gate

```text
NEXT_ACTION=VALIDAR_PR_28_EM_CELULAR_REAL
NEXT_GATE=OPERATIONAL_VALIDATION
```

## Pendências do gate operacional

- testar o PR #28 no celular real do piloto;
- confirmar fluxo principal abaixo de 10 segundos;
- testar iluminação adequada, baixa e excessiva;
- testar enquadramento inadequado e múltiplas pessoas;
- testar reutilização do desafio de captura;
- avaliar tentativa com fotografia ou tela diante da câmera;
- registrar falsos bloqueios e falsos aceites;
- executar revisão final independente do HEAD exato;
- decidir merge somente com evidências suficientes;
- revisar o PR #13 e encerrar se estiver obsoleto.

## Regra de continuidade

Este arquivo representa o checkpoint mais recente do projeto e deve ser atualizado ao final de cada ciclo relevante de trabalho. O histórico técnico detalhado permanece em `PROJECT_STATE.md`, nos PRs e nas issues do Linear.
