# LEA-96 / LEA-133 — Métricas recuperáveis e classificação conservadora

## 1. Regra de evidência

O objetivo original da LEA-96 era calcular média, mediana, P95 e maior tempo das 20 marcações controladas.

A execução das 20 marcações está confirmada pelo operador, porém os **20 tempos individuais não foram preservados nas fontes recuperáveis**. Portanto, este documento separa métricas calculáveis, limites demonstráveis e métricas não recuperáveis.

## 2. Evidência disponível

```text
TOTAL_ATTEMPTS=20
NOTEBOOK_ATTEMPTS=10
PHONE_ATTEMPTS=10
ALL_ATTEMPTS_CONFIRMED=YES
SUCCESSFUL_ATTEMPTS=20_BY_OPERATOR_CONFIRMATION
FALSE_POSITIVES_REPORTED=0
LIVE_CAMERA_ONLY=YES
ALL_TOTAL_TIMES_LT_10_SECONDS=REPORTED_PASS
```

Amostra visual preservada do telefone:

```text
TOTAL_TIMES=2.9,2.9,2.8
PROCESSING_TIMES=0.9,0.9,0.9
```

Métricas da amostra de três registros, **não da série de 20**:

```text
SAMPLE_N=3
SAMPLE_MEAN=2.866666...s
SAMPLE_MEDIAN=2.9s
SAMPLE_MIN=2.8s
SAMPLE_MAX=2.9s
SAMPLE_PROCESSING_MEAN=0.9s
```

## 3. Métricas da série de 20

| Métrica | Resultado | Grau de evidência |
|---|---:|---|
| total | 20 | confirmado pelo operador |
| notebook | 10 | confirmado pelo operador |
| telefone | 10 | confirmado pelo operador |
| sucessos | 20 | confirmado pelo operador |
| falhas reportadas | 0 | derivado da confirmação de todas as tentativas |
| taxa de sucesso | 100% | derivado da confirmação operacional |
| falsos positivos | 0 | reportado explicitamente |
| alvo `<10s` | PASS | reportado explicitamente para as 20 |
| média exata | indisponível | 20 tempos ausentes |
| mediana exata | indisponível | 20 tempos ausentes |
| P95 exato | indisponível | 20 tempos ausentes |
| máximo exato | indisponível | 20 tempos ausentes |
| limite do máximo | `<10s` | decorrente do PASS reportado do alvo para todas as tentativas |
| limite do P95 | `<10s` | decorrente de todos os tempos reportados `<10s` |

## 4. Critério oficial recuperado

O protocolo preservado define:

```text
PASS:
- 20 testes concluídos
- falso positivo = 0
- taxa de sucesso >= 95%
- P95 <= 8s
- máximo <= 10s

PASS_WITH_WARNINGS:
- falso positivo = 0
- taxa de sucesso >= 90%
- P95 > 8s e <= 10s
- ou máximo > 10s e <= 15s
- desvios explicados e controlados

FAIL:
- qualquer falso positivo
- taxa de sucesso < 90%
- falha estrutural recorrente
- P95 > 10s
- máximo > 15s
- evidência insuficiente
```

## 5. Classificação

A evidência recuperada prova os requisitos de volume, taxa de sucesso reportada, ausência reportada de falso positivo e limite `<10s`. Ela não prova `P95 <= 8s`.

Como `P95 < 10s` é suportado pelo relato de que todas as 20 tentativas ficaram abaixo de 10 s, a classificação operacional conservadora é:

```text
RESULT=PASS_WITH_WARNINGS
REASON=EXACT_DISTRIBUTION_NOT_RECOVERABLE
SUCCESS_RATE=100_PERCENT_BY_OPERATOR_CONFIRMATION
FALSE_POSITIVE=0_REPORTED
P95_BOUND=<10s
MAX_BOUND=<10s
P95_TARGET_8S=NOT_PROVABLE
EXACT_MEAN=UNAVAILABLE
EXACT_MEDIAN=UNAVAILABLE
EXACT_P95=UNAVAILABLE
EXACT_MAX=UNAVAILABLE
```

Essa classificação não afirma que P95 foi maior que 8 s. Ela apenas recusa promover o resultado a `PASS` sem a prova necessária.

## 6. Consequência de governança

```text
LEA_95=PASS
LEA_96=PASS_WITH_WARNINGS_EVIDENCE_GAP
STATISTICAL_RESULT=RECORDED_WITH_LIMITATIONS
PRODUCTION_HOMOLOGATION=BLOCKED
```

A homologação de produção continua bloqueada porque a rastreabilidade estatística completa foi perdida. Para remover essa limitação em uma futura homologação, deve-se repetir a bateria com captura estruturada dos 20 tempos individuais.

## 7. Prevenção de recorrência

A próxima bateria física deve registrar automaticamente, por tentativa:

```text
TEST_ID
DATE_TIME
DEVICE
TYPE
RESULT
TOTAL_TIME_SECONDS
PROCESSING_TIME_SECONDS
FALSE_POSITIVE
FALSE_NEGATIVE
CONDITIONS
EVIDENCE_REFERENCE
```

### Teste unitário futuro

O calculador de métricas deve receber uma lista de tentativas e produzir média, mediana, P95, máximo, taxa de sucesso e classificação reproduzível.

### Teste de integração futuro

A resposta do `/punch` já contém `processing_ms`; a instrumentação futura deve persistir/associar a duração total de teste sem armazenar imagem biométrica ou segredo.

## 8. Regra permanente

```text
NO_RAW_DATA -> NO_EXACT_STATISTIC
NO_EXACT_P95_PROOF -> NO_STRICT_PASS
```

A lacuna é registrada como warning de evidência, não ocultada.