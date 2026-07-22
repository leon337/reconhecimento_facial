# Controle de Ponto Potiguar — Estado Oficial do Projeto

Atualizado em: 2026-07-22

## Identificação

```text
REPOSITORY=leon337/reconhecimento_facial
DEFAULT_BRANCH=main
PROJECT_STATUS=PILOTO_LOCAL_AVANCADO
CURRENT_PHASE=FASE_10.1.1
MAIN_SHA=3908e639be2cd025e4a1eee044db21d1ef52d7ee
```

## Estado executivo

O projeto já ultrapassou a prova de conceito. A base atual inclui aplicação Flask/Gunicorn, PostgreSQL 16, migrations Alembic, isolamento por empresa e obra, RBAC, templates biométricos criptografados, eventos de ponto imutáveis, auditoria, backup e restauração, implantação local via Docker Compose e acesso HTTPS na rede local.

A FASE 10.1.1 está funcionalmente aprovada no notebook e no telefone. O PR #28 foi integrado por squash e o fluxo de ponto facial multiquadro sem piscada foi validado com câmera ao vivo, identificação automática, entrada, saída e rejeição de rosto não cadastrado.

A homologação estatística permanece pendente porque as 20 marcações controladas foram adiadas de forma consciente para permitir continuidade da implementação.

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

A migração para nuvem exigiria uma decisão arquitetural separada, pois o sistema depende de processamento facial nativo, PostgreSQL, volumes biométricos persistentes, Docker Compose, LGPD, armazenamento privado e backend persistente.

A Vercel não deve ser usada apenas para resolver certificados locais.

## Linear sincronizado

```text
PARENT_ISSUE=LEA-85
LEA_93=Done
LEA_94=Done
LEA_95=Backlog_DEFERRED
LEA_96=Todo_BLOCKED_BY_LEA_95
LEA_97=Todo
LEA_98=Todo
LEA_118=Done_HOSTING_LOCAL_DECISION
LEA_119=Documentation_Sync
```

## Pendências atuais

- retomar a LEA-95 antes da homologação estatística ou ampliação do piloto;
- executar 20 marcações controladas;
- calcular média, mediana, P95, máximo e taxa de sucesso;
- atualizar as evidências finais e encerrar formalmente a FASE 10.1.1;
- revisar e encerrar o PR #13 caso esteja obsoleto;
- atualizar o manual de instalação de 2025;
- documentar política LGPD, retenção e exclusão de dados biométricos;
- validar backup e restauração em ambiente separado;
- definir contingência manual para indisponibilidade de câmera, rede ou servidor.

## Gate atual

```text
FUNCTIONAL_VALIDATION=PASS
STATISTICAL_VALIDATION=DEFERRED
PRODUCTION_HOMOLOGATION=BLOCKED
IMPLEMENTATION_CONTINUATION=ALLOWED
NEXT_IMPLEMENTATION=FOLLOW_OFFICIAL_ROADMAP_AND_LINEAR
```

GitHub permanece como fonte técnica oficial. Linear deve refletir as missões, gates, decisões e pendências descritas neste documento.