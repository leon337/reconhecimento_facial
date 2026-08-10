# LEA-133 — Mapa auditável do legado `Ponto` e plano para `AttendanceEvent`

**Escopo:** análise e plano; nenhuma migração executada.

## 1. Resultado executivo

```text
PONTO_LIVE_WRITE=YES
PONTO_DUPLICATE_READ=YES
ATTENDANCE_EVENT_MODEL_EXISTS=YES
ATTENDANCE_EVENT_IMMUTABLE=YES
ATTENDANCE_EVENT_LIVE_WRITE=NO
DESTRUCTIVE_MIGRATION=NO
```

O risco principal não está na inexistência do domínio novo; está na coexistência entre um domínio moderno já criado e o fluxo operacional que continua dependente do legado.

## 2. Dependências do modelo `Ponto`

### 2.1 Persistência viva — CRÍTICA

Arquivo: `app/punch/routes.py`

Fluxo atual:

```text
câmera ao vivo
  -> challenge de uso único
  -> liveness passivo multiquadro
  -> reconhecimento do usuário
  -> regra de duplicidade
  -> Ponto.from_user(...)
  -> db.session.add(record)
  -> db.session.commit()
  -> JSON com id/tipo/timestamp
```

A função `_finish_punch` cria `Ponto.from_user(result.user, tipo=punch_type, timestamp=now)`. Portanto, mudar apenas o modelo ou adicionar uma migration não altera o comportamento real do produto.

### 2.2 Regra anti-duplicidade — CRÍTICA

Arquivo: `app/punch/rules.py`

`check_duplicate_punch()` consulta o último registro por `Ponto.query.filter_by(user_id=...)` e `Ponto.timestamp`. Uma migração da escrita sem migrar essa leitura faria a proteção de duplo clique consultar a fonte errada.

### 2.3 Modelo e relacionamentos — ESTRUTURAL

Arquivo: `app/models.py`

`Ponto` contém:

```text
id
user_id
company_id
worksite_id
timestamp
tipo
```

Relacionamentos legados existem em `Company.pontos`, `Worksite.pontos` e `User.pontos`. O modelo também possui validação de escopo empresa/obra e `scoped_query()`.

### 2.4 Testes acoplados ao legado — RELEVANTE

`tests/test_punch.py` verifica diretamente a criação e consulta de `Ponto`, inclusive a regra de duplicidade. `tests/test_organizational_isolation.py` também cobre criação/escopo do legado. Esses testes são proteção de regressão, mas precisarão ser evoluídos durante a convergência para não transformar o legado em contrato permanente por acidente.

### 2.5 Adaptadores existentes — NÃO COBREM PONTO

`app/infrastructure/legacy.py` possui `LegacyUserRepository` e `LegacySqlAlchemyUnitOfWork`, mas não existe adaptador equivalente para `Ponto`. Logo, a fronteira de compatibilidade para o registro de jornada ainda não está encapsulada.

### 2.6 Rotas antigas de upload

`app/routes.py` ainda contém `/form`, `/upload` e `/api/face`, porém `main.create_app()` registra apenas os blueprints `admin` e `punch`. Portanto essas rotas não são tratadas como dependência viva na baseline atual. O arquivo permanece dívida de limpeza/remoção controlada, não evidência de fluxo operacional ativo.

## 3. Domínio de destino

Arquivo: `app/attendance_models.py`

`AttendanceEvent` contém:

```text
id
employee_id
company_id
worksite_id
schedule_id
event_type
occurred_at
source
created_at
```

O modelo possui restrição única:

```text
(employee_id, occurred_at, event_type)
```

e listeners que rejeitam `UPDATE` e `DELETE`, sustentando a intenção append-only.

`AttendanceAdjustment` e `AttendanceClosure` já existem separadamente. O domínio `app/attendance.py` também define eventos `clock_in`, `break_start`, `break_end`, `clock_out` e regras de sequência.

## 4. Mapeamento proposto

| Legado `Ponto` | Destino | Regra |
|---|---|---|
| `Ponto.id` | referência de reconciliação externa | não reutilizar como PK do destino |
| `Ponto.user_id` | `AttendanceEvent.employee_id` | resolver por `User.employee_id`; ausência é erro de reconciliação |
| `Ponto.company_id` | `AttendanceEvent.company_id` | preservar e validar contra o Employee/User |
| `Ponto.worksite_id` | `AttendanceEvent.worksite_id` | preservar nullable conforme domínio atual |
| `Ponto.timestamp` | `AttendanceEvent.occurred_at` | preservar valor original, sem `now()` durante backfill |
| `Ponto.tipo=ENTRADA` | `event_type=clock_in` | mapeamento explícito e testado |
| `Ponto.tipo=SAIDA` | `event_type=clock_out` | mapeamento explícito e testado |
| captura facial | `source=biometric` | apenas quando origem for comprovadamente biométrica |
| inexistente | `schedule_id` | `NULL` até associação determinística |

### Bloqueador estrutural

`AttendanceEvent.employee_id` é obrigatório, enquanto `Ponto` referencia `User`. A convergência exige que todo usuário com ponto histórico tenha `employee_id` resolvível. Registros sem essa associação devem ir para uma fila/matriz de reconciliação, nunca ser descartados ou associados por aproximação.

## 5. Plano de convergência seguro

### Etapa A — contrato e inventário

1. criar contrato `LegacyPunchRecord -> AttendanceEventCandidate`;
2. definir enum único de mapeamento `ENTRADA/SAIDA`;
3. validar empresa/obra/employee;
4. definir chave determinística de idempotência/reconciliação;
5. produzir relatório de registros não mapeáveis.

### Etapa B — leitura comparativa, sem alterar a escrita

1. construir adaptador somente leitura do legado;
2. projetar o candidato `AttendanceEvent` em memória;
3. comparar contagens, identidades e timestamps;
4. rodar em testes e ambiente controlado;
5. nenhuma escrita no novo domínio ainda.

### Etapa C — backfill idempotente em ambiente não produtivo

1. copiar dados para ambiente isolado;
2. executar backfill por lotes;
3. repetir o mesmo lote e provar idempotência;
4. comparar origem/destino por checksum lógico;
5. testar rollback removendo apenas eventos marcados como provenientes do backfill controlado.

### Etapa D — escrita nova com compatibilidade temporária

Preferência arquitetural: **uma fonte primária por vez**, evitando dual-write permanente.

Estratégia recomendada:

```text
POST /punch
  -> serviço de domínio único
  -> AttendanceEvent como fonte primária
  -> adaptador de compatibilidade/consulta para legado durante transição
```

Se dual-write temporário for inevitável, ele deve possuir transação única, idempotência e alarme de divergência. Um commit em `AttendanceEvent` e outro independente em `Ponto` é proibido.

### Etapa E — migrar consumidores

A regra de duplicidade deve ser uma das primeiras leituras migradas, pois hoje consulta `Ponto`. Depois migram relatórios/consultas e testes. Só então os relacionamentos `*.pontos` podem ser depreciados.

### Etapa F — retirada gradual

1. período de leitura comparativa sem divergência;
2. backup comprovadamente restaurável;
3. evidência de reconciliação completa;
4. consumidores zerados;
5. gate humano;
6. somente depois considerar remoção física do legado em fase própria.

## 6. Rollback

Antes do corte:

```text
ROLLBACK_POINT=commit/tag + backup verificável + contagem lógica
```

Durante o corte:

- feature flag/configuração deve permitir retornar a leitura à fonte anterior;
- nenhum registro de `Ponto` histórico é apagado;
- backfill precisa carregar origem rastreável;
- falha de reconciliação interrompe o lote (`fail closed`).

Depois do corte, rollback não deve exigir reconstrução por inferência de eventos ausentes.

## 7. Testes obrigatórios para a futura implementação

### Unitários

- `ENTRADA -> clock_in` e `SAIDA -> clock_out`;
- usuário sem `employee_id` -> erro explícito;
- invariantes empresa/obra;
- chave de idempotência;
- mapeamento de timestamp sem alteração;
- repetição do backfill não duplica eventos.

### Integração

- `Ponto` + `User` + `Employee` -> candidato correto;
- reconciliação por empresa/obra;
- backfill idempotente em PostgreSQL;
- regra anti-duplicidade lendo a nova fonte;
- transação e rollback;
- regressão de RBAC, liveness, criptografia e auditoria.

### Contrato/regressão

- resposta pública do `/punch` preservada durante a transição;
- nenhum falso sucesso quando a persistência falhar;
- contagem origem/destino reproduzível;
- eventos imutáveis continuam rejeitando update/delete.

## 8. Decisão desta fase

```text
PONTO_DEPENDENCY_MAP=COMPLETE
ATTENDANCE_EVENT_CONVERGENCE_PLAN=COMPLETE
MIGRATION_IMPLEMENTED=NO
LEGACY_REMOVED=NO
NEXT_IMPLEMENTATION_REQUIRES_NEW_GATE=YES
```