# LEA-133 — Observabilidade, diagnóstico e guardrails de IA

## 1. Princípio

Nenhuma tela, API ou agente pode exibir um componente como saudável se não houver sinal real que sustente esse estado.

```text
SEM_TELEMETRIA != SAUDAVEL
SEM_TELEMETRIA = TELEMETRIA_INDISPONIVEL
```

A observabilidade deve separar estado técnico da aplicação, estado operacional da marcação de ponto e estado de integrações futuras.

## 2. Telemetria existente e verificada

| Sinal | Estado | Fonte atual | Limitação |
|---|---|---|---|
| request ID | real | `app/observability.py` | gerado por processo/request |
| logs HTTP estruturados | real | `after_request` | dependem do destino de logs do runtime |
| status HTTP/duração | real | log por request | ainda não agregado de forma durável |
| `/health` aplicação | real | endpoint Flask | confirma app responsiva no processo |
| `/health` banco | real | `SELECT 1` | não prova saúde de todos os componentes |
| `/metrics` | real | `defaultdict(int)` | contadores em memória, resetam com processo |
| erro 404/500 | real | contadores + request ID | não há série histórica persistente |
| tempo de punch | real | `processing_ms` da resposta | por requisição, sem P95 durável |
| falhas de reconhecimento/liveness | real parcial | contadores em memória | sem persistência/retention |
| auditoria de ações | real | `AuditEvent` | não substitui métrica técnica |
| CI/regressão | real | GitHub Actions | estado da branch, não runtime do piloto |
| backup PostgreSQL em CI | real | workflow Production Validation | sintético; não é estado do último backup do piloto |

## 3. Telemetria ausente

```text
CAMERA_HEARTBEAT=UNAVAILABLE
STATION_HEARTBEAT=UNAVAILABLE
BACKUP_LAST_SUCCESS_PILOT=UNAVAILABLE
RESTORE_LAST_SUCCESS_PILOT=UNAVAILABLE
DURABLE_METRICS=UNAVAILABLE
DURABLE_LATENCY_HISTOGRAM=UNAVAILABLE
QUEUE_TELEMETRY=NOT_APPLICABLE_YET_QUEUE_DOES_NOT_EXIST
AI_HEALTH=NOT_APPLICABLE_YET_AI_NOT_IMPLEMENTED
OFFLINE_SYNC_TELEMETRY=NOT_APPLICABLE_YET_SYNC_DOES_NOT_EXIST
```

A distinção `UNAVAILABLE` versus `NOT_APPLICABLE_YET` evita transformar uma funcionalidade inexistente em incidente falso.

## 4. Modelo de estado proposto para o futuro dashboard

Para serviços existentes:

```text
HEALTHY
DEGRADED
UNAVAILABLE
UNKNOWN
TELEMETRY_UNAVAILABLE
```

Para IA, somente quando houver implementação:

```text
IA_CONFIGURADA
IA_ACESSIVEL
IA_OPERACIONAL
IA_DEGRADADA
IA_INDISPONIVEL
```

`IA_CONFIGURADA` nunca deve ser sinônimo de `IA_OPERACIONAL`.

## 5. Health Aggregator futuro

```text
Dashboard / API de Operação
          |
          v
   Health Aggregator
     /    |     \
   API    DB   Estações
    |      |      |
 logs   queries  heartbeat/camera
    \      |      /
       Event Store / Métricas
               |
               v
        Diagnóstico assistido
```

O agregador deve ser determinístico. IA pode explicar sinais já coletados; não decide se um componente está saudável sem dados objetivos.

## 6. Primeiro módulo de IA recomendado

### `IA_DIAGNOSTICO`

Entrada permitida:

- códigos de erro;
- request IDs;
- métricas técnicas agregadas;
- estado dos componentes;
- eventos operacionais sanitizados;
- runbooks e documentação técnica aprovada.

Saída permitida:

- resumo do incidente;
- hipóteses ordenadas;
- componentes possivelmente relacionados;
- próximos passos de investigação;
- explicação em linguagem simples para administrador/suporte.

### `IA_EXPLICACAO_EVENTOS`

Pode traduzir um código/estado técnico em mensagem acionável e contextual. Para mensagens determinísticas conhecidas, preferir tabela de mensagens a LLM.

## 7. Dados proibidos ou minimizados no provedor de IA

Por padrão, não enviar:

- imagem facial;
- template/embedding biométrico;
- chave de criptografia;
- senha/token/cookie;
- documento pessoal completo;
- salário ou folha individual quando não necessário;
- payload bruto de banco;
- logs com segredos.

Antes de qualquer chamada externa deve existir camada de sanitização e política explícita de campos permitidos.

## 8. Autoridade da IA

A IA pode:

```text
ANALISAR=YES
EXPLICAR=YES
RESUMIR=YES
RECOMENDAR=YES
PRIORIZAR_INVESTIGACAO=YES
```

A IA não pode autonomamente:

```text
APROVAR_CORRECAO_DE_PONTO=NO
ALTERAR_JORNADA=NO
ALTERAR_PAGAMENTO=NO
PUNIR_COLABORADOR=NO
DECLARAR_FRAUDE=NO
SOBRESCREVER_RECONHECIMENTO_BIOMETRICO=NO
CONCEDER_ACESSO=NO
EXCLUIR_BIOMETRIA=NO
DECLARAR_CONFORMIDADE_JURIDICA=NO
```

Qualquer ação futura que produza efeito trabalhista deve passar por regra determinística + autorização humana apropriada + auditoria.

## 9. Contrato de diagnóstico futuro

Exemplo conceitual:

```json
{
  "request_id": "...",
  "component_states": [],
  "sanitized_events": [],
  "metrics_window": {},
  "allowed_actions": ["explain", "recommend_investigation"]
}
```

A resposta deve carregar:

```text
confidence
supporting_signals
missing_signals
hypotheses
recommended_checks
cannot_conclude
```

`cannot_conclude` é obrigatório quando faltarem sinais.

## 10. Testes para implementação futura

### Unitários

- sanitização remove campos proibidos;
- estado `TELEMETRY_UNAVAILABLE` não vira `HEALTHY`;
- mapeamento de códigos determinísticos;
- policy bloqueia ações trabalhistas/autoritativas;
- resposta sem evidência marca `cannot_conclude`.

### Integração

- agregador combina API + DB sem mascarar falha parcial;
- falha do provedor de IA não derruba registro de ponto;
- timeout/circuit breaker da IA retorna diagnóstico indisponível;
- logs da integração não contêm biometria/segredos;
- auditoria registra solicitação e resposta sanitizada quando aplicável.

### Avaliação de IA

- conjunto de incidentes conhecidos com hipótese esperada;
- taxa de afirmações sem suporte;
- recusa correta em decisões proibidas;
- robustez quando telemetria está incompleta;
- consistência de recomendação com runbook.

## 11. Resultado desta ressalva

```text
OBSERVABILITY_CURRENT_LIMITS=DOCUMENTED
FALSE_GREEN_POLICY=DEFINED
MISSING_TELEMETRY=EXPLICIT
AI_FIRST_MODULE=ARCHITECTED
AI_GUARDRAILS=DEFINED
AI_IMPLEMENTED=NO
AI_AUTONOMOUS_LABOR_DECISION=PROHIBITED
```

Este documento resolve a ambiguidade arquitetural; a implementação de observabilidade durável e IA permanece para fase própria após novo gate.