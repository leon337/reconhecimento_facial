# Controle de Ponto Potiguar — Estado Oficial do Projeto

Atualizado em: 2026-07-22

## Identificação

```text
REPOSITORY=leon337/reconhecimento_facial
DEFAULT_BRANCH=main
PROJECT_STATUS=PILOTO_LOCAL_AVANCADO
CURRENT_PHASE=FASE_10.1.1_EM_FECHAMENTO
BASELINE_FUNCTIONAL_SHA=3908e639be2cd025e4a1eee044db21d1ef52d7ee
ROADMAP_FILE=ROADMAP_CURRENT.md
NEXT_CONFIRMED_PHASE=FASE_12_LEA_133
```

## Estado executivo

O projeto já ultrapassou a prova de conceito. A base atual inclui aplicação Flask/Gunicorn, PostgreSQL 16, migrations Alembic, isolamento por empresa e obra, RBAC, templates biométricos criptografados, eventos de ponto imutáveis, auditoria, backup e restauração, implantação local via Docker Compose e acesso HTTPS na rede local.

A FASE 10.1.1 está funcionalmente aprovada no notebook e no telefone. O PR #28 foi integrado por squash e o fluxo de ponto facial multiquadro sem piscada foi validado com câmera ao vivo, identificação automática, entrada, saída e rejeição de rosto não cadastrado.

A homologação estatística permanece pendente porque as 20 marcações controladas foram adiadas. A continuidade é permitida somente sob o roadmap e os gates oficiais.

A pesquisa de mercado e a extração de escopo da LEA-125 foram produzidas e publicadas no PR #29 como documentação. O PR permanece Draft, sem merge e sem autorização automática do roadmap proposto.

## Objetivo final preservado

Transformar o piloto local em uma plataforma segura, auditável e comercialmente viável de controle de jornada, com foco em empresas com múltiplas obras, equipes externas, baixa conectividade e operação simples.

O produto não deve ser anunciado como juridicamente conforme enquanto os requisitos regulatórios não forem validados por especialista.

## Entregas integradas na `main`

- FASE 9.0: fundação arquitetural em camadas e contratos testáveis;
- FASE 9.1: PostgreSQL e Alembic;
- FASE 9.2: empresas, obras e isolamento organizacional;
- FASE 9.3: colaboradores, contas e controle de acesso por papéis;
- FASE 9.4: segregação e criptografia dos templates biométricos;
- FASE 9.5: domínio imutável de ponto, jornadas e correções auditáveis;
- FASE 9.6: auditoria, observabilidade e endurecimento HTTP;
- FASE 9.7: backup, restauração e infraestrutura persistente;
- FASE 9.8: validação de produção;
- FASE 10: piloto local no Linux Mint e captura biométrica por câmera;
- FASE 10.1: HTTPS local, câmera exclusiva, prova de vida e desempenho;
- FASE 10.1.1: cadastro e ponto facial multiquadro sem piscada.

## PR #28 — estado final

```text
PULL_REQUEST=28
TITLE=HOTFIX FASE 10.1.1 — ponto facial multiquadro sem piscada
AUTHORIZED_HEAD=53483aa139ab6b810f54427ef544c7f9550f7103
MERGE_METHOD=SQUASH
MERGED=YES
MERGE_COMMIT=3908e639be2cd025e4a1eee044db21d1ef52d7ee
CI_175=SUCCESS
PRODUCTION_VALIDATION_44=SUCCESS
```

## Validação operacional concluída

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
FALSE_IDENTIFICATION_OBSERVED=NO
```

## Infraestrutura oficial

```text
APPLICATION=Flask/Gunicorn
DATABASE=PostgreSQL 16 local em Docker
MIGRATIONS=Alembic
REVERSE_PROXY_TLS=Caddy
LAN_IP=192.168.10.101
BIOMETRIC_STORAGE=volume persistente separado e criptografado
SUPABASE=NOT_IN_USE
VERCEL=NOT_CONFIGURED
HOSTING_DECISION=KEEP_LOCAL_PILOT
```

### Decisão de hospedagem

Em 22/07/2026 foi decidido não migrar o projeto para a Vercel neste momento. O piloto permanece no servidor Linux Mint.

A migração para nuvem exige decisão arquitetural separada, pois o sistema depende de processamento facial nativo, PostgreSQL, volumes biométricos persistentes, Docker Compose, LGPD, armazenamento privado e backend persistente.

A Vercel não deve ser usada apenas para resolver certificados locais.

## Pesquisa de mercado e FASE 11

```text
LINEAR_ANALYSIS=LEA-125
PULL_REQUEST=29
PR_STATUS=DRAFT_OPEN
PR_MERGED=NO
DOCUMENTATION_DIRECTORY=docs/lea-125/
FUNCTIONS_CATALOGUED=84
DELIVERED=15
PARTIAL=22
NOT_IMPLEMENTED=34
LEGAL_VALIDATION=8
NOT_RECOMMENDED=5
ROADMAP_APPROVED=NO
```

Pendências documentais:

- revisar formalmente o PR #29;
- retirar do modo Draft somente após revisão;
- fazer merge apenas com autorização;
- reconciliar LEA-125 e LEA-126 a LEA-132 com os entregáveis existentes;
- sincronizar novamente GitHub e Linear.

## Linear e fases

```text
LEA_85=In_Progress
LEA_93=Done
LEA_94=Done
LEA_95=Backlog_DEFERRED
LEA_96=Todo_BLOCKED_BY_LEA_95
LEA_97=Todo
LEA_98=Todo
LEA_118=Done_HOSTING_LOCAL_DECISION
LEA_119=Documentation_Sync
LEA_125=In_Progress_DOCUMENTATION_IN_PR_29
LEA_126_TO_132=DELIVERABLES_EXIST_STATUS_RECONCILIATION_PENDING
LEA_133=NEXT_CONFIRMED_PHASE_NOT_STARTED
```

## Próxima fase confirmada — FASE 12 / LEA-133

A FASE 12 é uma fase de fechamento e baseline, não de expansão funcional. Ela deve:

1. concluir as 20 marcações e métricas;
2. validar backup e restauração em ambiente isolado;
3. testar contingência de câmera, rede, servidor e banco;
4. mapear a dependência do modelo legado `Ponto`;
5. definir plano de migração para `AttendanceEvent` sem executá-lo;
6. preservar multitenancy, RBAC, auditoria, criptografia e liveness;
7. registrar decisão arquitetural sobre REP/PTRP;
8. separar itens técnicos de `EXIGE_VALIDACAO_JURIDICA`;
9. produzir o gate explícito para a próxima implementação.

## Roadmap futuro — proposta não aprovada

- FASE 13: núcleo imutável e comprovante;
- FASE 14: divergências, justificativas e aprovações;
- FASE 15: jornadas, escalas e cálculos explicáveis;
- FASE 16: relatórios, espelho e fechamento;
- FASE 17: segurança e privacidade comercial;
- FASE 18: offline, mobilidade e geolocalização;
- FASE 19: V1 comercial multiobra;
- FASE 20: API e integrações;
- FASE 21: antifraude e diferenciais responsáveis.

Essas fases não estão autorizadas para implementação. O detalhamento oficial está em `ROADMAP_CURRENT.md`.

## Pendências atuais

- revisar e concluir documentalmente o PR #29;
- reconciliar LEA-125 e LEA-126 a LEA-132;
- autorizar formalmente o início operacional da LEA-133;
- retomar a LEA-95 antes da homologação estatística ou ampliação do piloto;
- executar 20 marcações controladas;
- calcular média, mediana, P95, máximo e taxa de sucesso;
- atualizar as evidências finais e encerrar formalmente a FASE 10.1.1;
- validar backup e restauração em ambiente separado;
- definir e testar contingência manual;
- mapear o legado `Ponto` e planejar `AttendanceEvent`;
- registrar decisão REP/PTRP sem declarar conformidade;
- revisar e encerrar o PR #13 caso esteja obsoleto;
- atualizar o manual de instalação de 2025;
- documentar política LGPD, retenção e exclusão de dados biométricos.

## Gate atual

```text
FUNCTIONAL_VALIDATION=PASS
STATISTICAL_VALIDATION=DEFERRED
PRODUCTION_HOMOLOGATION=BLOCKED
PR_29_REVIEW=PENDING
LEA_133_START=REQUIRES_HUMAN_AUTHORIZATION
IMPLEMENTATION_CONTINUATION=ALLOWED_UNDER_GOVERNANCE
NEXT_ACTION=REVIEW_PR_29_AND_RECONCILE_LEA_125_TO_132
NEXT_OPERATIONAL_PHASE=LEA_133_FASE_12
NEXT_FUNCTIONAL_IMPLEMENTATION=NOT_AUTHORIZED
```

## Ordem obrigatória de consulta

Em qualquer novo chat ou missão, consultar:

1. `ROADMAP_CURRENT.md`;
2. `CHECKPOINT.md`;
3. `PROJECT_STATE.md`;
4. issues relacionadas no Linear;
5. PRs e código aplicáveis.

GitHub permanece como fonte técnica oficial. Linear deve refletir as missões, gates, decisões e pendências descritas nestes documentos.
