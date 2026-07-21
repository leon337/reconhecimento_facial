# Controle de Ponto Potiguar — Estado Oficial do Projeto

Atualizado em: 2026-07-21

## Identificação

```text
REPOSITORY=leon337/reconhecimento_facial
DEFAULT_BRANCH=main
PROJECT_STATUS=PILOTO_LOCAL_AVANCADO
CURRENT_PHASE=FASE_10.1.1
MAIN_SHA=b04a42bf65f5b8d35fc14dd9433d347dba1cf9c6
```

## Estado executivo

O projeto já ultrapassou a prova de conceito. A base atual inclui aplicação Flask/Gunicorn, PostgreSQL 16, migrations Alembic, isolamento por empresa e obra, RBAC, templates biométricos criptografados, eventos de ponto imutáveis, auditoria, backup e restauração, implantação local via Docker Compose e acesso HTTPS na rede local.

A operação homologada até o momento é um piloto local em Linux Mint, acessível pelo notebook e por celulares conectados à mesma rede. Não existe deploy público oficial em Vercel e os projetos Supabase antigos não fazem parte da arquitetura ativa.

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
- FASE 10.1.1: cadastro facial multiquadro sem piscada.

## Pull request ativo

```text
PULL_REQUEST=28
TITLE=HOTFIX FASE 10.1.1 — ponto facial multiquadro sem piscada
STATE=OPEN
DRAFT=YES
MERGEABLE=YES
BASE_SHA=b04a42bf65f5b8d35fc14dd9433d347dba1cf9c6
HEAD_SHA=53483aa139ab6b810f54427ef544c7f9550f7103
CI=PASS
PRODUCTION_VALIDATION=PASS
MERGE=NOT_DONE
```

O PR #28 substitui a piscada obrigatória na batida de ponto por verificação facial passiva multiquadro. A implementação mantém câmera ao vivo, desafio de uso único, identificação automática e bloqueio de envio pela galeria.

## Gate atual

O próximo gate é a validação operacional do PR #28 em dispositivo real.

Critérios mínimos:

1. testar no celular usado no piloto;
2. confirmar identificação em menos de 10 segundos no fluxo principal;
3. testar iluminação adequada, baixa e excessiva;
4. testar rosto fora do centro e mais de uma pessoa no quadro;
5. testar repetição do desafio de captura;
6. verificar comportamento diante de foto ou tela apresentada à câmera;
7. registrar falsos bloqueios e falsos aceites observados;
8. somente depois realizar revisão final e merge.

## Infraestrutura oficial

```text
APPLICATION=Flask/Gunicorn
DATABASE=PostgreSQL 16 local em Docker
MIGRATIONS=Alembic
REVERSE_PROXY_TLS=Caddy
BIOMETRIC_STORAGE=volume persistente separado e criptografado
SUPABASE=NOT_IN_USE
VERCEL=NOT_CONFIGURED
```

### Supabase

Os projetos antigos `potiguarbd`, `ponto-mvp` e `ponto-mvp-demo` estão inativos e não devem ser tratados como banco oficial da versão atual.

### Vercel

Não existe projeto Vercel associado ao Controle de Ponto Potiguar. A aplicação atual depende de backend Python, processamento facial e persistência local, portanto o piloto permanece hospedado no servidor Linux Mint.

## Pendências de governança

- concluir a validação operacional do PR #28;
- executar revisão final independente do HEAD exato;
- decidir o merge somente após evidências do piloto;
- revisar e encerrar o PR #13 caso esteja obsoleto;
- atualizar o manual de instalação de 2025, que descreve somente a antiga prova de conceito;
- documentar política LGPD, retenção e exclusão de dados biométricos;
- validar backup e restauração em ambiente separado;
- definir contingência manual para indisponibilidade de câmera, rede ou servidor.

## Próxima ação oficial

```text
NEXT_ACTION=VALIDAR_PR_28_EM_CELULAR_REAL
NEXT_GATE=OPERATIONAL_VALIDATION
IMPLEMENTATION_CHANGES=NOT_AUTHORIZED_BY_THIS_DOCUMENT
```

Este arquivo é a referência resumida para reconstrução do estado entre chats. GitHub permanece como fonte técnica oficial; Linear deve refletir as missões, gates e pendências descritas aqui.
