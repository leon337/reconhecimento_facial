# PRF — CPP-COMMERCIAL-REDESIGN-AI-OBS-001

## Identificação

```text
PROJECT=Controle de Ponto Potiguar
REPOSITORY=leon337/reconhecimento_facial
MISSION=CPP-COMMERCIAL-REDESIGN-AI-OBS-001
MCF_PROTOCOL=1.1
RISK_CLASS=C
HUMAN_AUTHORITY=Leandro
DELEGATED_GATE=Léo
COORDINATOR=Mestre
BASE_MAIN_SHA=783ca912c38876e68c12439a0db3616bf2b29a1d
GATE_DECISION=APPROVED_WITH_RESERVATIONS
DATE=2026-08-10
```

## Decisão humana vinculante

Leandro aprovou a direção estratégica proposta pelo Léo **com ressalvas** e determinou que elas sejam resolvidas antes de qualquer nova fase funcional.

```text
STRATEGIC_DIRECTION=APPROVED
RESERVATION_RESOLUTION=AUTHORIZED
FUNCTIONAL_EXPANSION=BLOCKED_UNTIL_NEW_GATE
PRODUCTION_HOMOLOGATION=BLOCKED
LEGAL_CONFORMITY_DECLARATION=PROHIBITED
AUTONOMOUS_LABOR_DECISIONS_BY_AI=PROHIBITED
```

## Objetivo

Reconciliar estado, recuperar evidências, transformar ambiguidades em decisões e contratos verificáveis e produzir baseline auditável para o próximo gate, sem executar o redesign, IA operacional ou migração `Ponto -> AttendanceEvent`.

## Ressalvas e interpretação reconciliada

1. **Baseline documental desatualizada.** Reconciliar `CHECKPOINT.md`, `PROJECT_STATE.md`, `ROADMAP_CURRENT.md`, GitHub e Linear com PR #29 merged e LEA-125 concluída.
2. **LEA-95 inconsistente.** A primeira leitura de 10/08 supôs ausência de prova, mas a revisão integral do histórico recuperou confirmação operacional explícita das 20 marcações. Corrigir o tracker para `Done` e preservar a lacuna real: os 20 tempos individuais não foram recuperados.
3. **LEA-133 não iniciada.** Ativar somente após autorização humana; autorização foi dada em 10/08/2026.
4. **Legado `Ponto`.** Mapear escrita/leitura viva e produzir plano seguro de convergência para `AttendanceEvent`, sem migração destrutiva nesta fase.
5. **Observabilidade parcial.** Distinguir sinais reais, não duráveis, indisponíveis e funcionalidades ainda inexistentes; proibir falso verde.
6. **Telemetria/recuperação.** Validar o que for possível de forma isolada e sintética, documentar runbook e não fingir exercício físico do piloto.
7. **Fronteira regulatória.** Manter REP/PTRP/SREP/LGPD biométrica e demais conclusões sob `VALIDAÇÃO_ESPECIALIZADA_NECESSÁRIA`.
8. **IA.** Permitir apenas análise/explicação/recomendação futura; proibir decisões autônomas trabalhistas, disciplinares, biométricas, de acesso, fraude ou conformidade.

## Escopo autorizado

- reconciliação GitHub–Linear;
- documentação e evidências;
- correção de estados rastreados com base em evidência histórica;
- mapa de dependência `Ponto`;
- plano `AttendanceEvent`;
- arquitetura de observabilidade e IA;
- guardrails e fronteira jurídica;
- estratégia/testes unitários e de integração;
- ampliação do workflow de Production Validation com dados sintéticos para backup/restore e falha segura;
- classificação estatística conservadora da LEA-96 com os dados efetivamente recuperáveis.

## Fora de escopo sem novo gate

- redesign funcional em código;
- módulo de IA operacional;
- migração `Ponto -> AttendanceEvent`;
- migration de banco do domínio de jornada;
- deploy;
- expansão do piloto;
- homologação de produção;
- declaração de conformidade jurídica;
- automação de decisão de RH;
- fingir execução de testes físicos que exijam dispositivo, câmera, rede ou ambiente real do piloto.

## Equipe MCF

Núcleo ativo: Mestre, Léo, Miriam, Leonardo, Carlos, Evelyn, Laura, Isabela, Marina, Sofia, Rafael, Manoel, Renato, Bruno, Ricardo, Carmem, Emily, Tiago, Augusto, Beatriz e Júlia.

Agentes sob demanda: Gabriel, Eduardo, Helena, André, Daniela, Vinícius, Patrícia e Lucas.

## Ordem de execução

```text
Miriam -> reconciliação de fontes
Carmem -> baseline documental
Renato -> evidência/testes
Sofia + Rafael + Manoel -> Ponto/AttendanceEvent
Bruno + Ricardo -> observabilidade/restore/contingência
Tiago + Júlia + Beatriz -> IA/governança
Emily -> auditoria independente
Mestre -> consolidação
Léo -> gate delegado
Leandro -> novo gate humano
```

## Linha de montagem de testes

```text
Requisito
  -> Critério
  -> Teste unitário
  -> Integração
  -> Regressão
  -> Segurança
  -> Observabilidade
  -> Evidência
  -> Auditoria
  -> Gate
```

### Evidência estatística

A LEA-95 recuperada suporta:

```text
TOTAL=20
NOTEBOOK=10
PHONE=10
SUCCESS=20_BY_OPERATOR_CONFIRMATION
SUCCESS_RATE=100_PERCENT_BY_OPERATOR_CONFIRMATION
FALSE_POSITIVE=0_REPORTED
ALL_TIMES_LT_10S=REPORTED
```

Não suporta a reconstrução dos 20 tempos individuais. Portanto:

```text
LEA_96=PASS_WITH_WARNINGS
EXACT_MEAN=UNAVAILABLE
EXACT_MEDIAN=UNAVAILABLE
EXACT_P95=UNAVAILABLE
EXACT_MAX=UNAVAILABLE
STRICT_P95_8S=NOT_PROVABLE
PRODUCTION_HOMOLOGATION=BLOCKED
```

## Gate de saída da FASE 12

```text
DOCUMENTS_RECONCILED=REQUIRED
LEA_95_RECONCILED=REQUIRED
LEA_96_LIMITATION_RECORDED=REQUIRED
LEA_133_STATE_RECONCILED=REQUIRED
PONTO_DEPENDENCY_MAP=REQUIRED
ATTENDANCE_EVENT_PLAN=REQUIRED
OBSERVABILITY_TRUTH_MATRIX=REQUIRED
AI_GUARDRAILS=REQUIRED
LEGAL_BOUNDARY=REQUIRED
SYNTHETIC_RESTORE_EVIDENCE=REQUIRED
CONTINGENCY_RUNBOOK=REQUIRED
INDEPENDENT_AUDIT=REQUIRED
NEXT_HUMAN_GATE=REQUIRED
```

## Regra de encerramento

Uma ressalva pode ser considerada resolvida quando deixa de ser ambígua e passa a possuir evidência, decisão, plano e critério verificável. Isso não permite declarar como implementada uma funcionalidade futura.

Dívidas externas ou de homologação devem continuar explícitas:

```text
EXACT_20_TIMINGS=NOT_RECOVERED
PILOT_REAL_DR=NOT_PROVED_BY_CI
PHYSICAL_OUTAGE_DRILLS=REQUIRE_PILOT_ENVIRONMENT
LEGAL_SPECIALIST_VALIDATION=PENDING
PRODUCTION_HOMOLOGATION=BLOCKED
```

Até auditoria independente e novo gate:

```text
NEW_FUNCTIONAL_PHASE=BLOCKED
```