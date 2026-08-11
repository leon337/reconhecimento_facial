# Controle de Ponto Potiguar — Decisões Congeladas

Versão: 1.0  
Vigência: 2026-08-10  
Autoridade humana: Leandro  
Repositório: `leon337/reconhecimento_facial`  
Baseline usada para este congelamento: `e9f2075eecbd4e2385f1d1674fb52bbaa689f198`

```text
DECISION_FREEZE=ACTIVE
APPROVED_BY=LEANDRO
FASE_12=COMPLETE
NF_01=NEXT_NOT_STARTED
NF_02_TO_NF_08=NOT_STARTED
PRODUCTION_HOMOLOGATION=BLOCKED
LEGAL_CONFORMITY_DECLARED=NO
```

## 1. Finalidade

Este documento consolida as decisões estratégicas, arquiteturais, operacionais e de governança que não podem ser reinterpretadas por um novo chat, agente, documento secundário ou implementação futura sem um novo gate humano explícito.

Ele não declara que funcionalidades futuras já existem. Ele congela **o que foi decidido**, **a ordem de execução**, **os limites de cada etapa** e **as condições para alterar essas decisões**.

## 2. Hierarquia de fontes de verdade

1. **GitHub `main`** é a fonte técnica para o estado real do código e dos artefatos publicados.
2. **Este documento** é a fonte oficial para decisões estratégicas congeladas e para a ordem NF-01 → NF-08.
3. `ROADMAP_CURRENT.md`, `PROJECT_STATE.md`, `CHECKPOINT.md` e os artefatos da FASE 12 são documentos de suporte e evidência.
4. Linear representa acompanhamento de fases, gates, dependências e decisões, mas não substitui evidência técnica no GitHub.
5. Em matéria jurídica, trabalhista, regulatória ou de proteção de dados, nenhuma conclusão de engenharia substitui validação especializada.

### Regra de conflito

```text
CONFLITO_SOBRE_CODIGO_ATUAL -> GITHUB_MAIN_PREVALECE
CONFLITO_SOBRE_DECISAO_ESTRATEGICA -> DECISOES_CONGELADAS_PREVALECEM
CONFLITO_COM_GATE_HUMANO_POSTERIOR -> GATE_HUMANO_EXPLICITO_PREVALECE_E_EXIGE_ATUALIZACAO_DESTE_ARQUIVO
CONFLITO_JURIDICO -> VALIDACAO_ESPECIALIZADA_NECESSARIA
```

Nenhum chat futuro pode alterar silenciosamente o significado destas decisões.

## 3. Regra para modificar o congelamento

Uma decisão congelada só pode ser alterada quando houver:

```text
1. NOVO_GATE_HUMANO_EXPLICITO_DE_LEANDRO
2. MOTIVO_E_IMPACTO_DOCUMENTADOS
3. ATUALIZACAO_VERSIONADA_DESTE_ARQUIVO
4. PUBLICACAO_NO_GITHUB
5. RASTREABILIDADE_DA_MUDANCA
```

Uma recomendação de agente, resultado de IA, comentário em chat ou conveniência de implementação não é autorização para modificar o congelamento.

## 4. Definição do produto congelada

O Controle de Ponto Potiguar deixa de ser tratado como apenas um projeto de reconhecimento facial.

> **Produto:** plataforma de controle de jornada para equipes presenciais e de campo, com identificação facial, gestão multiempresa/multiunidade, rastreabilidade operacional e capacidade de diagnóstico do próprio sistema.

Linha lógica do produto:

```text
IDENTIDADE
  -> RECONHECIMENTO FACIAL
  -> REGISTRO DE PONTO
  -> JORNADA
  -> GESTAO
  -> AUDITORIA
  -> OBSERVABILIDADE
  -> IA ASSISTIVA
```

Público inicial pretendido: pequenas e médias empresas com equipes presenciais, de campo, obras ou unidades distribuídas, com necessidade de simplicidade operacional, baixo custo de infraestrutura e rastreabilidade.

## 5. Experiências separadas

O produto deve preservar três experiências distintas:

```text
FUNCIONARIO -> registrar ponto, receber confirmação, entender erro e saber o que fazer
GESTOR/ADMIN -> pessoas, unidades, registros, pendencias, jornada e estado operacional
SUPORTE -> health, logs, request IDs, falhas, latencia, estacoes, backup e diagnostico
```

A tela de marcação de ponto continua sendo uma experiência simples e separada do shell administrativo.

## 6. Invariantes técnicas congeladas

Devem ser preservados, salvo novo gate humano com justificativa técnica:

- Flask/Gunicorn;
- PostgreSQL;
- Alembic;
- `Company` / `Worksite` e isolamento multiempresa/multiobra;
- RBAC;
- auditoria;
- templates biométricos cifrados;
- armazenamento biométrico privado;
- captura facial multiquadro;
- câmera ao vivo no fluxo moderno;
- desafio de uso único;
- liveness passivo;
- identificação automática;
- backup/restore existente;
- Caddy/HTTPS local;
- suíte de testes automatizados.

### Decisão arquitetural

```text
FRAMEWORK_REWRITE_FOR_REDESIGN=NO
```

O redesign deve evoluir sobre a base existente antes de qualquer proposta de reescrita estrutural.

## 7. Legado `Ponto` e `AttendanceEvent`

Estado congelado:

```text
PONTO_LIVE_WRITE=YES
PONTO_DUPLICATE_READ=YES
ATTENDANCE_EVENT_EXISTS=YES
ATTENDANCE_EVENT_IMMUTABLE=YES
ATTENDANCE_EVENT_LIVE_WRITE=NO
PONTO_TO_ATTENDANCE_EVENT_MIGRATION=NOT_IMPLEMENTED
```

A migração futura não pode ser tratada como simples troca de tabela. Ela exige, antes de produção:

- idempotência;
- reconciliação;
- rollback;
- preservação histórica;
- preservação de empresa, obra e timestamp;
- mapeamento `User.employee_id`;
- testes unitários;
- testes de integração;
- regressão da batida facial e de RBAC/multitenancy.

Nenhuma NF anterior a um gate específico para essa mudança pode declarar a migração concluída.

## 8. Observabilidade congelada

Regra permanente:

```text
SEM_TELEMETRIA != SAUDAVEL
BOTAO != ESTADO
ACAO -> BACKEND -> OBSERVACAO -> ESTADO_REAL -> INTERFACE
```

Sinais reais já existentes não podem ser confundidos com sinais ainda inexistentes.

```text
REQUEST_ID=REAL
STRUCTURED_HTTP_LOGS=REAL
API_HEALTH=REAL
DATABASE_HEALTH=REAL
IN_MEMORY_METRICS=REAL_NON_DURABLE
PUNCH_PROCESSING_MS=REAL_PER_REQUEST
AUDIT_EVENT=REAL
CAMERA_HEARTBEAT=TELEMETRY_UNAVAILABLE
STATION_HEARTBEAT=TELEMETRY_UNAVAILABLE
DURABLE_METRICS=TELEMETRY_UNAVAILABLE
PILOT_BACKUP_LAST_SUCCESS=TELEMETRY_UNAVAILABLE
QUEUE=NOT_IMPLEMENTED
AI=NOT_IMPLEMENTED
OFFLINE_SYNC=NOT_IMPLEMENTED
```

Telemetria técnica deve permanecer separada dos dados trabalhistas:

```text
DADOS_TRABALHISTAS != TELEMETRIA_TECNICA
```

## 9. IA — objetivo e limites congelados

Primeiro candidato de IA:

```text
IA_DIAGNOSTICO
+
IA_EXPLICACAO_DE_EVENTOS
```

A primeira IA deve ser assistiva, de leitura e diagnóstico. Não será iniciado um chatbot genérico apenas para “ter IA”.

### IA pode

```text
ANALISAR
EXPLICAR
RESUMIR
RECOMENDAR
PRIORIZAR_INVESTIGACAO
```

### IA não pode decidir autonomamente

```text
APROVAR_OU_RECUSAR_CORRECAO_DE_JORNADA
ALTERAR_PAGAMENTO
APLICAR_PUNICAO
SOBREPOR_RECONHECIMENTO_BIOMETRICO
CONCEDER_ACESSO
EXCLUIR_BIOMETRIA
DECLARAR_FRAUDE
DECLARAR_CONFORMIDADE_JURIDICA
ALTERAR_FOLHA
```

Dados biométricos brutos, templates, chaves, senhas e tokens ficam fora do contrato padrão da IA.

## 10. Fronteira jurídica e regulatória

Estado congelado:

```text
TARGET_PRODUCT=COMMERCIAL_MULTI_COMPANY_TIME_ATTENDANCE_PLATFORM
CURRENT_REGULATORY_CLAIM=NONE
REP_P=VALIDACAO_ESPECIALIZADA_NECESSARIA
PTRP=VALIDACAO_ESPECIALIZADA_NECESSARIA
COLLECTOR_ROLE=VALIDACAO_ESPECIALIZADA_NECESSARIA
LGPD_BIOMETRICS=VALIDACAO_ESPECIALIZADA_NECESSARIA
ENGINEERING_CAN_DECLARE_COMPLIANCE=NO
LEGAL_CONFORMITY_DECLARED=NO
```

Nenhuma NF pode transformar uma hipótese jurídica em alegação comercial de conformidade sem validação especializada e novo gate apropriado.

## 11. Oito ressalvas da FASE 12

As oito ressalvas foram encerradas no nível de baseline, governança e arquitetura:

```text
R1_STALE_BASELINE=RESOLVED
R2_LEA95_AMBIGUITY=RESOLVED
R3_LEA133_NOT_STARTED=RESOLVED
R4_PONTO_DEPENDENCY=RESOLVED_AS_AUDITED_MAP_AND_CONTROLLED_PLAN
R5_OBSERVABILITY_AMBIGUITY=RESOLVED_AS_TRUTH_MATRIX
R6_MISSING_TELEMETRY=RESOLVED_AS_TRUTHFUL_STATE_MODEL
R7_LEGAL_AUTHORITY=RESOLVED_BY_SPECIALIST_BOUNDARY
R8_AI_AUTONOMY=RESOLVED_BY_GUARDRAILS
```

`RESOLVED` não significa implementação de funcionalidades futuras.

## 12. Homologação de produção continua separada

A produção não está homologada.

Permanecem os gates:

```text
GATE_HOM_01=REPEAT_20_WITH_FULL_TIMING_DATASET
GATE_HOM_02=REAL_PILOT_DISASTER_RECOVERY
GATE_HOM_03=PHYSICAL_CAMERA_NETWORK_SERVER_DB_CONTINGENCY_DRILLS
RPO_PILOT=UNDECIDED
RTO_PILOT=UNMEASURED
LEGAL_SPECIALIST_VALIDATION=PENDING
PRODUCTION_HOMOLOGATION=BLOCKED
```

Esses gates não devem ser reclassificados como “já resolvidos” apenas porque a FASE 12 foi encerrada.

## 13. Roadmap NF oficial congelado

A ordem aprovada de trabalho é:

```text
NF-01 PRODUTO + DESIGN SYSTEM
  -> NF-02 REDESIGN COMERCIAL
  -> NF-03 EXPERIENCIA OPERACIONAL
  -> NF-04 OBSERVABILIDADE
  -> NF-05 ARQUITETURA + PRIMEIRO MODULO DE IA
  -> NF-06 IDENTIDADE + DISPOSITIVOS
  -> NF-07 REAVALIACAO DO ROADMAP
  -> NF-08 VALIDACOES TECNICAS REMANESCENTES
```

Uma NF não autoriza automaticamente a seguinte.

### NF-01 — Produto + Design System

Objetivo: congelar a arquitetura da informação, linguagem de produto, estados, permissões, tokens e componentes antes de alterar código de produção.

Dentro do escopo:

- definição operacional do produto;
- inventário das telas existentes;
- arquitetura da informação;
- mapa de navegação;
- papéis e permissões por tela;
- wireframes conceituais;
- design tokens;
- componentes reutilizáveis;
- estados `loading`, `empty`, `ready`, `success`, `warning`, `degraded`, `error`, `offline`, `no_permission`, `telemetry_unavailable`;
- diretrizes de responsividade;
- diretrizes de acessibilidade;
- critérios de aceite e testes conceituais.

Fora do escopo:

```text
PRODUCTION_CODE=NO
PONTO_MIGRATION=NO
AI_OPERATIONAL_IMPLEMENTATION=NO
OBSERVABILITY_BACKEND_IMPLEMENTATION=NO
DEPLOY=NO
PRODUCTION_HOMOLOGATION=NO
```

### NF-02 — Redesign Comercial

Aplicar shell visual e componentes aprovados na NF-01 sem alterar regras centrais de jornada, IA ou migração `Ponto -> AttendanceEvent`.

### NF-03 — Experiência Operacional

Tornar marcação, cadastro, biometria, unidades, registros e erros operacionalmente claros. Nenhuma operação crítica pode ficar sem feedback verificável.

### NF-04 — Observabilidade

Criar health aggregation, métricas duráveis, estados verificáveis, eventos, telemetria de estação/backup e alertas sem transformar ausência de sinal em verde.

### NF-05 — Arquitetura + Primeiro Módulo de IA

Integrar IA apenas com problema comprovado, começando por diagnóstico/explicação, leitura apenas, dados minimizados, fallback determinístico e avaliação específica.

### NF-06 — Identidade + Dispositivos

Consolidar identidade própria do produto e estratégia para desktop/mobile web/estação compartilhada. Decisão PWA versus nativo continua dependente de análise da própria NF.

### NF-07 — Reavaliação do Roadmap

Reconciliar roadmap histórico, produto redesenhado, dívida técnica, observabilidade, IA e resultados de uso antes de escolher a próxima sequência funcional.

### NF-08 — Validações Técnicas Remanescentes

Retomar explicitamente os bloqueios de homologação: série completa das 20 marcações, métricas estritas, DR real do piloto, contingência física e demais validações necessárias.

## 14. Roadmap histórico FASE 13–21

O roadmap anterior não é apagado. Ele permanece como histórico/proposta de produto, porém:

```text
FASE_13_TO_21=AUTO_AUTHORIZATION_NO
RECONCILIATION_POINT=NF_07
```

Nenhuma fase histórica futura deve ser iniciada apenas porque aparece em documentos antigos.

## 15. Uma NF por chat — regra congelada

Decisão humana de Leandro:

```text
ONE_NF_PER_CHAT=MANDATORY
CROSS_NF_IMPLEMENTATION=PROHIBITED_WITHOUT_NEW_CHAT_AND_GATE
```

Fluxo obrigatório:

```text
NOVO_CHAT_DA_NF
  -> recuperar GitHub main + DECISOES_CONGELADAS.md
  -> recuperar fechamento da NF anterior, quando existir
  -> executar somente a NF nomeada
  -> produzir evidencias e artefatos
  -> revisar/testar
  -> publicar fechamento da NF
  -> gerar prompt da NF seguinte
  -> encerrar o chat
```

O encerramento de uma NF não inicia automaticamente a próxima. O início ocorre apenas em novo chat e com ação humana explícita de Leandro.

## 16. Linha de montagem de qualidade

```text
REQUISITO
  -> DESIGN
  -> ARQUITETURA
  -> IMPLEMENTACAO
  -> TESTE_UNITARIO
  -> TESTE_DE_INTEGRACAO
  -> TESTE_DE_CONTRATO
  -> REGRESSAO
  -> UX_RESPONSIVIDADE_ACESSIBILIDADE
  -> SEGURANCA
  -> OBSERVABILIDADE
  -> VALIDACAO_OPERACIONAL
  -> EVIDENCIA
  -> GATE
```

Testes unitários e de integração são obrigatórios quando houver código correspondente. Mudança de banco exige teste de upgrade/downgrade e rollback. Alteração de fluxo de ponto exige regressão facial, RBAC e multitenancy.

## 17. Direção visual congelada em nível de princípio

A identidade pode se inspirar na família visual institucional já estudada, sem copiar outra marca:

```text
BASE=VERDE_INSTITUCIONAL
SUPERFICIES=NEUTROS_CLAROS
ACENTO_PREMIUM=DOURADO_MODERADO
DADOS=GRAFITE
STATUS=CORES_SEMANTICAS_INDEPENDENTES_DA_MARCA
```

O verde da marca nunca significa automaticamente “sistema saudável”. Estado operacional precisa ser derivado de telemetria real.

## 18. Estado imediatamente após este congelamento

```text
DECISION_FREEZE=ACTIVE
FASE_12=COMPLETE
NF_01=READY_FOR_NEW_CHAT_NOT_STARTED
NF_02_TO_NF_08=NOT_STARTED
REDESIGN_PRODUCTION_CODE_STARTED=NO
AI_IMPLEMENTATION_STARTED=NO
PONTO_MIGRATION_STARTED=NO
PRODUCTION_HOMOLOGATION=BLOCKED
NEXT_WORK_CHAT=NF_01_ONLY
```

A publicação deste documento **não executa a NF-01**. Ela apenas prepara a fonte de verdade para que a NF-01 seja iniciada em um novo chat, conforme a decisão humana registrada.