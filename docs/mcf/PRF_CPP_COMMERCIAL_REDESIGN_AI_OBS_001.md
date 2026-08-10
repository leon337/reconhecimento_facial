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

Leandro aprovou a direção estratégica proposta pelo Léo **com ressalvas** e determinou que as ressalvas sejam resolvidas antes de qualquer avanço para a nova fase funcional.

Interpretação operacional:

```text
STRATEGIC_DIRECTION=APPROVED
RESERVATION_RESOLUTION=AUTHORIZED
FUNCTIONAL_IMPLEMENTATION=BLOCKED
NEW_STRATEGIC_PHASE=BLOCKED_UNTIL_RESERVATIONS_RESOLVED
LEGAL_CONFORMITY_DECLARATION=PROHIBITED
AUTONOMOUS_LABOR_DECISIONS_BY_AI=PROHIBITED
```

## Objetivo imediato

Reconciliar o estado oficial do projeto e eliminar inconsistências documentais, de rastreabilidade e de governança antes do novo roadmap de redesign comercial, IA e observabilidade.

## Ressalvas obrigatórias

1. Reconciliar `CHECKPOINT.md`, `PROJECT_STATE.md`, `ROADMAP_CURRENT.md`, GitHub e Linear com o estado real do PR #29 e da LEA-125.
2. Corrigir a divergência da LEA-95: o tracker estava `Done`, mas as 20 marcações controladas não possuem evidência de conclusão.
3. Registrar a LEA-133 como fase ativa apenas após autorização humana explícita.
4. Preservar como dívida técnica a dependência do fluxo vivo no modelo legado `Ponto` e planejar `AttendanceEvent` sem migração destrutiva nesta etapa.
5. Classificar a observabilidade atual como parcial; não representar câmera, backup, fila, estações ou IA como monitorados sem telemetria real.
6. Manter decisões regulatórias e de conformidade sob `VALIDAÇÃO_ESPECIALIZADA_NECESSÁRIA`.
7. Fixar limites de IA: analisar, explicar, resumir e recomendar; não aprovar jornada, alterar pagamento, punir colaborador, sobrescrever biometria, conceder acesso, excluir biometria ou declarar fraude/conformidade autonomamente.
8. Preservar a dívida de validação estatística e a homologação de produção bloqueada até evidência suficiente.

## Escopo autorizado nesta etapa

- reconciliação documental;
- sincronização de estado GitHub–Linear;
- produção de evidências e contratos de entrada/saída;
- inventário de dependências do legado `Ponto`;
- plano de migração futuro para `AttendanceEvent`;
- arquitetura de observabilidade e telemetria em nível de planejamento;
- arquitetura e limites do primeiro módulo de IA em nível de planejamento;
- definição de estratégia de testes;
- preparação do protocolo das 20 marcações e demais validações operacionais.

## Fora de escopo sem novo gate

- redesign em código;
- implementação de IA;
- migração `Ponto` → `AttendanceEvent`;
- alteração de banco ou migrations;
- deploy;
- expansão do piloto;
- homologação de produção;
- declaração de conformidade jurídica;
- decisão automatizada de RH;
- execução autônoma de testes físicos que dependam de câmera/dispositivo/pessoa real sem operador disponível.

## Equipe MCF convocada

### Núcleo ativo

- Mestre — coordenação e ESEV.
- Léo — gate delegado e decisão operacional.
- Miriam — memória, baseline e reconciliação multi-fonte.
- Leonardo — produto e requisitos.
- Carlos — riscos futuros e inovação.
- Evelyn — estratégia de experiência.
- Laura — UX.
- Isabela — UI.
- Marina — acessibilidade.
- Sofia — arquitetura.
- Rafael — engenharia e impacto de implementação.
- Manoel — dados e persistência.
- Renato — QA, unitários, integração e regressão.
- Bruno — plataforma, SRE e observabilidade.
- Ricardo — segurança.
- Carmem — documentação técnica.
- Emily — auditoria independente.
- Tiago — IA/ML.
- Augusto — observabilidade multiagente.
- Beatriz — avaliação de agentes/IA.
- Júlia — governança e compliance de IA.

### Agentes sob demanda

Gabriel, Eduardo, Helena, André, Daniela, Vinícius, Patrícia e Lucas entram quando houver tarefa específica de Git/release, backend, frontend, mobile, dados, refatoração, debugging ou performance.

## Ordem de execução

```text
Miriam: reconciliar fontes
  -> Carmem: corrigir baseline documental
  -> Renato: fechar estratégia de evidência e testes
  -> Sofia/Rafael/Manoel: mapear Ponto e plano AttendanceEvent
  -> Bruno/Ricardo: observabilidade, backup, contingência e segurança
  -> Tiago/Júlia/Beatriz: limites e arquitetura de IA
  -> Emily: auditoria independente
  -> Mestre: consolidar
  -> Léo/Leandro: gate seguinte
```

## Estratégia de testes

A execução segue uma linha de montagem:

```text
Requisito
  -> Contrato
  -> Teste unitário
  -> Teste de integração
  -> Teste de regressão
  -> Teste de segurança
  -> Teste de observabilidade
  -> Validação operacional
  -> Evidência
  -> Gate
```

### Obrigatórios antes de nova implementação funcional

- unitários para cálculos/classificações e contratos de domínio;
- integração de backup/restore, RBAC, multitenancy e biometria;
- regressão facial e de liveness;
- testes negativos de autorização e isolamento;
- validação de telemetria e estados degradados;
- 20 marcações controladas quando o operador e os dispositivos estiverem disponíveis;
- média, mediana, P95, máximo, taxa de sucesso e falso positivo observado;
- evidências sanitizadas e reproduzíveis.

## Gate de saída desta etapa

```text
DOCUMENTS_RECONCILED=REQUIRED
LEA_95_TRACKER_RECONCILED=REQUIRED
LEA_133_STATE_RECONCILED=REQUIRED
PONTO_DEPENDENCY_MAP=REQUIRED
ATTENDANCE_EVENT_PLAN=REQUIRED
OBSERVABILITY_LIMITS_DOCUMENTED=REQUIRED
AI_GUARDRAILS_DOCUMENTED=REQUIRED
LEGAL_ITEMS_SEPARATED=REQUIRED
STATISTICAL_DEBT_EXPLICIT=REQUIRED
INDEPENDENT_AUDIT=REQUIRED
NEXT_GATE=REQUIRED
```

Enquanto qualquer item obrigatório permanecer aberto:

```text
NEW_FUNCTIONAL_PHASE=BLOCKED
PRODUCTION_HOMOLOGATION=BLOCKED
```
