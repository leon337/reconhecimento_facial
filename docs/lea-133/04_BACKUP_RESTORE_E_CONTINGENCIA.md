# LEA-133 — Backup, restore isolado e contingência

## 1. Escopo

Este documento separa três níveis que não podem ser confundidos:

1. **capacidade do código** de gerar/verificar/restaurar backup;
2. **validação automatizada isolada** com dados sintéticos;
3. **exercício operacional do piloto real** no Linux Mint.

Um PASS em (2) não é automaticamente um PASS em (3).

## 2. Capacidade existente

`app/infrastructure/backup.py` oferece:

- validação de URL PostgreSQL;
- `pg_dump` em formato custom;
- manifesto JSON;
- SHA-256 do dump;
- validação do arquivo contra manifesto;
- `pg_restore` com confirmação explícita `RESTORE`;
- retenção de backups.

A implementação existente cobre o banco. O armazenamento biométrico é filesystem separado (`BIOMETRIC_STORAGE_FOLDER`) e a chave (`BIOMETRIC_ENCRYPTION_KEY`) é configuração/segredo externo. Esses dois componentes não fazem parte do dump PostgreSQL.

## 3. Validação automatizada ampliada na LEA-133

O workflow `.github/workflows/production-validation.yml` foi ampliado na branch da LEA-133 para executar um exercício sintético de disaster recovery sem usar dados reais.

Linha de montagem:

```text
PostgreSQL limpo
  -> migrations upgrade/downgrade/upgrade
  -> fixture sintética de empresa/obra/employee/user
  -> template biométrico sintético cifrado
  -> objeto sintético no storage biométrico
  -> backup PostgreSQL + manifesto + SHA-256
  -> checksum do storage biométrico
  -> banco vazio de restore
  -> pg_restore
  -> storage biométrico em diretório isolado
  -> validação de checksums
  -> aplicação apontando para DB/storage restaurados
  -> health
  -> empresa/obra
  -> senha/RBAC
  -> descriptografia com chave recuperada
  -> falha esperada sem chave
  -> marcação sintética após restore
```

A chave de teste nunca é persistida como artefato. O teste prova que a restauração depende da recuperação segura da chave externa e que a ausência da chave impede descriptografia.

## 4. Evidências que o workflow deve produzir

- JUnit da regressão;
- diagnóstico do backup;
- lista do `pg_restore`;
- diagnóstico do restore;
- duração do restore do banco no CI;
- manifesto/checksum do dump;
- checksum relativo do storage biométrico sintético;
- diagnóstico da restauração do storage.

Nenhum artefato pode conter chave de criptografia, imagem facial real ou template biométrico real.

## 5. Interpretação correta

Se o workflow ampliado passar:

```text
SYNTHETIC_DB_RESTORE=PASS
SYNTHETIC_BIOMETRIC_STORAGE_RESTORE=PASS
SYNTHETIC_KEY_DEPENDENCY=PASS
SYNTHETIC_RBAC_AFTER_RESTORE=PASS
SYNTHETIC_ORG_SCOPE_AFTER_RESTORE=PASS
SYNTHETIC_PUNCH_AFTER_RESTORE=PASS
PILOT_REAL_DR_EXERCISE=NOT_PROVED_BY_CI
```

A última linha é deliberada. O CI não possui acesso ao volume real, à chave operacional real nem aos dispositivos físicos do piloto.

## 6. Runbook de restore do piloto real

### Preparação

```text
1. congelar escrita do piloto
2. registrar timestamp do início
3. identificar DATABASE_URL sem expor credenciais
4. identificar BIOMETRIC_STORAGE_FOLDER
5. confirmar disponibilidade da chave no cofre/meio seguro
6. gerar backup do PostgreSQL
7. gerar manifesto/checksum
8. gerar manifesto/checksum do storage biométrico
9. criar ambiente isolado, nunca sobrescrever o piloto
```

### Restore

```text
10. restaurar PostgreSQL em banco vazio
11. restaurar storage biométrico em diretório isolado
12. injetar a chave pelo canal seguro
13. apontar instância isolada para DB/storage restaurados
14. subir aplicação
15. GET /health
16. autenticar administrador de teste
17. validar RBAC
18. validar empresa/obra
19. validar leitura/descriptografia de perfil biométrico autorizado
20. executar uma marcação controlada
21. verificar auditoria e ausência de duplicidade
```

### Evidência

Registrar somente dados sanitizados:

```text
BACKUP_CREATED_AT=
RESTORE_STARTED_AT=
RESTORE_FINISHED_AT=
RPO_OBSERVED=
RTO_OBSERVED=
DB_CHECKSUM=PASS|FAIL
BIOMETRIC_STORAGE_CHECKSUM=PASS|FAIL
HEALTH=PASS|FAIL
LOGIN=PASS|FAIL
RBAC=PASS|FAIL
COMPANY_WORKSITE_SCOPE=PASS|FAIL
BIOMETRIC_DECRYPTION=PASS|FAIL
CONTROLLED_PUNCH=PASS|FAIL
AUDIT=PASS|FAIL
```

## 7. Contingência operacional

### 7.1 Câmera indisponível

Estado esperado:

```text
PUNCH_BY_FACE=UNAVAILABLE
DO_NOT_PRETEND_SUCCESS=YES
MANUAL_CONTINGENCY=REQUIRED
```

Procedimento:

1. estação mostra erro de câmera, não tela verde;
2. operador registra ocorrência manual em canal controlado definido pela empresa;
3. registro manual contém pessoa, empresa/obra, horário declarado, motivo e responsável;
4. quando o serviço retornar, reconciliação é humana e auditável;
5. não criar ponto facial retroativo fingindo que houve biometria.

### 7.2 Rede indisponível

O produto atual não possui fila offline. Portanto:

```text
OFFLINE_QUEUE=NO
AUTOMATIC_SYNC=NO
```

Procedimento atual é contingência manual auditável. Não guardar biometria improvisadamente no navegador/dispositivo.

### 7.3 Servidor indisponível

1. cliente deve apresentar indisponibilidade;
2. operador usa contingência manual;
3. reinício deve ser seguido de `/health`;
4. retornar operação somente após aplicação + DB responderem;
5. reconciliar registros manuais sem duplicar.

### 7.4 Banco indisponível

`/health` depende de `SELECT 1`; banco indisponível deve resultar em falha, nunca `database=ok`.

Regra:

```text
DATABASE_UNAVAILABLE -> PUNCH_PERSISTENCE_UNAVAILABLE
NO_DB_WRITE -> NO_SUCCESS_RECEIPT
```

Nenhum sucesso deve ser exibido antes do commit do registro.

## 8. Reconciliação de contingência

Para cada ocorrência manual futura:

```text
contingency_id
employee
company
worksite
declared_at
recorded_at
reason
recorded_by
source=manual_contingency
review_status
linked_attendance_event
```

A futura importação deve ser idempotente e não pode sobrescrever evento original. Correção deve ser append-only/auditável.

## 9. RPO e RTO

A FASE 12 não inventa metas empresariais. Devem ser distinguidos:

- `RTO_CI_OBSERVED`: medido pelo workflow sintético;
- `RTO_PILOT_OBSERVED`: somente após exercício no Linux Mint;
- `RPO_PILOT`: depende da frequência real de backup, ainda precisa de decisão operacional.

Até existir decisão humana e exercício real:

```text
RPO_PILOT=UNDECIDED
RTO_PILOT=UNMEASURED
```

## 10. Testes

### Unitários

- checksum adulterado falha;
- manifesto errado falha;
- confirmação diferente de `RESTORE` falha;
- chave ausente impede descriptografia;
- regra de reconciliação é idempotente.

### Integração

- migrations up/down/up;
- PostgreSQL -> dump -> banco vazio -> restore;
- DB + storage biométrico + chave sintética;
- autenticação/RBAC após restore;
- empresa/obra após restore;
- marcação sintética após restore;
- falha de DB produz estado indisponível.

### Operacional físico

- câmera ausente;
- rede interrompida;
- servidor parado;
- banco parado;
- execução do runbook por operador diferente;
- restore real isolado sem tocar o piloto.

## 11. Estado

```text
BACKUP_CODE_AUDITED=YES
SYNTHETIC_FULL_RESTORE_WORKFLOW=IMPLEMENTED_IN_PR30
CI_RESULT_FOR_NEW_WORKFLOW=PENDING
PILOT_REAL_RESTORE=REQUIRES_ACCESS_TO_PILOT
PHYSICAL_CAMERA_NETWORK_SERVER_EXERCISE=REQUIRES_OPERATOR_AND_PILOT
CONTINGENCY_RUNBOOK=DEFINED
LEGAL_CONFORMITY_DECLARED=NO
```