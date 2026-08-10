# LEA-133 — Reconciliação de baseline e evidências

**Data:** 10/08/2026  
**Missão MCF:** `CPP-COMMERCIAL-REDESIGN-AI-OBS-001`  
**Base da `main`:** `783ca912c38876e68c12439a0db3616bf2b29a1d`  
**Modo:** resolução de ressalvas / FASE 12  

## 1. Objetivo

Registrar a fonte de verdade reconciliada antes de qualquer nova implementação funcional. Quando uma fonte histórica contradiz o estado atual, a divergência é mantida explicitamente em vez de ser apagada.

## 2. Estado reconciliado

| Item | Estado reconciliado | Evidência / interpretação |
|---|---|---|
| PR #29 | `MERGED` | merge documental na `main`, SHA `783ca912...` |
| LEA-125 a LEA-132 | `Done` | entregáveis publicados pelo PR #29 |
| LEA-133 | `In Progress` | início autorizado por Leandro em 10/08/2026 |
| LEA-95 | `Done` | histórico da issue contém confirmação operacional explícita das 20 marcações |
| LEA-96 | `Todo` | não foram recuperados os 20 tempos individuais necessários para métricas exatas |
| LEA-97 | `Todo` | depende da consolidação das evidências e do fechamento técnico |
| LEA-98 | `Todo` | não pode encerrar enquanto gates remanescentes não forem tratados |
| LEA-85 | `In Progress` | fase funcionalmente aprovada, fechamento estatístico/documental ainda incompleto |
| Homologação de produção | `BLOCKED` | não deve ser inferida a partir da validação funcional |

## 3. Correção da LEA-95

A primeira reconciliação de 10/08/2026 havia devolvido a LEA-95 para `Backlog`, assumindo ausência de evidência. A leitura integral dos comentários da própria issue mostrou que essa conclusão estava errada.

O comentário histórico de 23/07/2026 registra confirmação operacional fornecida pelo usuário em 22/07/2026:

```text
TOTAL_ATTEMPTS=20
NOTEBOOK_ATTEMPTS=10
PHONE_ATTEMPTS=10
ALL_ATTEMPTS_CONFIRMED=YES
FALSE_POSITIVES_REPORTED=0
TARGET_TOTAL_TIME_LT_10_SECONDS=PASS
LIVE_CAMERA_ONLY=YES
CONTROLLED_MARKS_RESULT=PASS
```

Também foram preservadas três amostras visuais de telefone:

```text
TOTAL_TIME_SAMPLES=2.9s,2.9s,2.8s
PROCESSING_TIME_SAMPLES=0.9s,0.9s,0.9s
SAMPLE_MEAN_TOTAL=2.87s
SAMPLE_MEDIAN_TOTAL=2.9s
SAMPLE_MIN_TOTAL=2.8s
SAMPLE_MAX_TOTAL=2.9s
```

Consequência:

```text
LEA_95_TECHNICAL_COMPLETION=YES
LEA_95_TRACKER=Done
TWENTY_CONTROLLED_PUNCHES=CONFIRMED_BY_OPERATOR
FALSE_POSITIVE_REPORTED=0
TARGET_LT_10_SECONDS=REPORTED_PASS
```

Isso **não** torna a LEA-96 automaticamente concluída.

## 4. LEA-96 — lacuna de evidência

Foram pesquisados:

- comentários da LEA-95, LEA-96, LEA-85 e LEA-97;
- documentação do repositório;
- arquivos históricos do projeto disponíveis;
- histórico recuperável da conversa associado à execução de 22/07/2026.

Não foram recuperados os 20 tempos individuais. Portanto não é tecnicamente válido inventar média, mediana, P95 ou máximo exatos da série completa.

O que é suportado pela evidência recuperada:

```text
TOTAL_ATTEMPTS=20
NOTEBOOK_ATTEMPTS=10
PHONE_ATTEMPTS=10
SUCCESSFUL_ATTEMPTS=20_CONFIRMED_BY_OPERATOR
SUCCESS_RATE=100_PERCENT_BY_OPERATOR_CONFIRMATION
FALSE_POSITIVES=0_REPORTED
ALL_TOTAL_TIMES_LT_10_SECONDS=REPORTED
EXACT_MEAN=NOT_RECOVERABLE
EXACT_MEDIAN=NOT_RECOVERABLE
EXACT_P95=NOT_RECOVERABLE
EXACT_MAX=NOT_RECOVERABLE
```

Como todos os 20 tempos foram reportados como menores que 10 segundos, é possível apenas estabelecer o limite `MAX < 10s` e, consequentemente, `P95 < 10s`; não é possível provar o alvo desejado `P95 <= 8s`.

### Classificação metodológica

```text
LEA_96_RESULT=INCOMPLETE_EVIDENCE
PASS_STRICT=NOT_PROVABLE
FAIL=NOT_PROVABLE
BOUNDED_CLASSIFICATION=PASS_OR_PASS_WITH_WARNINGS
PRODUCTION_HOMOLOGATION=BLOCKED
```

O resultado não é convertido artificialmente em `PASS`. A ausência do conjunto individual é uma dívida de evidência explícita.

## 5. Baseline técnica verificada

A rota operacional `POST /punch` continua persistindo `Ponto`. O modelo `AttendanceEvent` existe e é imutável em atualização/exclusão, mas ainda não é a escrita viva do ponto. A migração não é executada nesta fase.

A observabilidade atual contém request IDs, logs HTTP estruturados, `/health` com consulta ao banco e contadores em memória. Esses contadores não são duráveis.

## 6. Evidência automatizada da branch da LEA-133

No head inicial do PR #30 (`afdf26fa8b2f1bb17d531ff2c674880debd25e47`), os workflows executados pelo GitHub Actions concluíram com sucesso:

```text
CI=PASS
PYTEST=143_PASSED
COMPILEALL=PASS
PRODUCTION_VALIDATION=PASS
MIGRATION_UP_DOWN_UP=PASS
POSTGRES_HEALTH=PASS
DATABASE_BACKUP=PASS
BACKUP_CHECKSUM=PASS
DATABASE_RESTORE_TO_EMPTY_DATABASE=PASS
RESTORED_SCHEMA_CHECK=PASS
COMPOSE_VALIDATION=PASS
```

Essa evidência valida o **backup/restore do PostgreSQL sintético no CI**. Ela não deve ser promovida para `FULL_DISASTER_RECOVERY=PASS`, pois o workflow atual não restaura o diretório biométrico e a chave operacional real do piloto.

## 7. Regras de continuidade

```text
NO_EVIDENCE_INVENTION=YES
PHASE_13_IMPLEMENTATION=BLOCKED
REDESIGN_CODE=BLOCKED
AI_IMPLEMENTATION=BLOCKED
DATABASE_MIGRATION=BLOCKED
PRODUCTION_HOMOLOGATION=BLOCKED
LEGAL_CONFORMITY_DECLARED=NO
```

A resolução da LEA-133 pode registrar desvios de evidência, mas não pode mascará-los como testes executados.