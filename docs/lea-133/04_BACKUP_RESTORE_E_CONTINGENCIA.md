# LEA-133 — Backup, restore isolado e contingência

## 1. Escopo e regra de evidência

Este documento separa:

1. capacidade do código de gerar/verificar/restaurar backup;
2. validação automatizada isolada com dados sintéticos;
3. exercício operacional do piloto real no Linux Mint.

```text
CI_SYNTHETIC_PASS != PILOT_REAL_DR_PASS
```

Nenhum resultado automatizado é promovido artificialmente para evidência física do piloto.

## 2. Capacidade existente

`app/infrastructure/backup.py` cobre PostgreSQL com `pg_dump`, manifesto JSON, SHA-256, validação do backup, `pg_restore` com confirmação explícita e retenção.

O armazenamento biométrico (`BIOMETRIC_STORAGE_FOLDER`) e a chave (`BIOMETRIC_ENCRYPTION_KEY`) ficam fora do dump PostgreSQL. A LEA-133 passou a tratá-los explicitamente no exercício sintético.

## 3. Workflow ampliado

`.github/workflows/production-validation.yml` executa a seguinte linha de montagem:

```text
migrations up/down/up
  -> regressão
  -> empresa/obra/employee/user sintéticos
  -> template biométrico sintético cifrado
  -> objeto sintético no storage biométrico
  -> backup PostgreSQL + manifesto + checksum
  -> checksum do storage
  -> banco vazio
  -> restore PostgreSQL
  -> restore do storage em diretório isolado
  -> validação de checksums
  -> aplicação restaurada
  -> health
  -> autenticação + RBAC + escopo
  -> descriptografia com chave
  -> falha esperada sem chave
  -> punch sintético pós-restore
  -> Compose
```

Após a primeira execução bem-sucedida, o workflow foi endurecido para mascarar a chave sintética gerada com `::add-mask::` e adicionar teste explícito de comportamento fail-closed quando o banco está indisponível.

## 4. Evidência do run #63

GitHub Actions Production Validation run `31437529880`, job `93614885716`:

```text
RESULT=PASS
MIGRATIONS_UP_DOWN_UP=PASS
REGRESSION=143_PASSED
WARNINGS=26_NON_BLOCKING
POSTGRES_HEALTH=PASS
POSTGRES_BACKUP=PASS
BACKUP_CHECKSUM=PASS
POSTGRES_RESTORE_EMPTY_DB=PASS
CI_DATABASE_RESTORE_DURATION=415ms
RESTORED_SCHEMA=PASS
BIOMETRIC_STORAGE_CHECKSUM_RESTORE=PASS
BIOMETRIC_TEMPLATE_DECRYPTION_WITH_KEY=PASS
DECRYPTION_WITHOUT_KEY=EXPECTED_FAIL_PASS
AUTHENTICATION_AFTER_RESTORE=PASS
RBAC_AFTER_RESTORE=PASS
COMPANY_WORKSITE_SCOPE_AFTER_RESTORE=PASS
SYNTHETIC_PUNCH_AFTER_RESTORE=PASS
COMPOSE_VALIDATION=PASS
```

Artefato publicado:

```text
NAME=production-validation-report
ARTIFACT_ID=9081579094
ZIP_SHA256=80a3aa236cdc1698c54b23cef52dcf1d6450fd00cafbd84893f4cb7a086c5eca
SIZE_BYTES=6538
```

Os dados usados são sintéticos. Nenhuma imagem facial real, template real ou chave operacional do piloto foi usada.

## 5. Interpretação

```text
SYNTHETIC_DB_RESTORE=PASS
SYNTHETIC_BIOMETRIC_STORAGE_RESTORE=PASS
SYNTHETIC_KEY_DEPENDENCY=PASS
SYNTHETIC_RBAC_AFTER_RESTORE=PASS
SYNTHETIC_ORG_SCOPE_AFTER_RESTORE=PASS
SYNTHETIC_PUNCH_AFTER_RESTORE=PASS
PILOT_REAL_DR_EXERCISE=NOT_PROVED_BY_CI
```

## 6. Runbook do piloto real

### Preparação

```text
1 congelar escrita do piloto
2 registrar início
3 identificar DATABASE_URL sem expor credenciais
4 identificar BIOMETRIC_STORAGE_FOLDER
5 confirmar chave por canal seguro
6 gerar backup PostgreSQL
7 registrar manifesto/checksum
8 registrar manifesto/checksum do storage biométrico
9 criar ambiente isolado sem sobrescrever o piloto
```

### Restore

```text
10 restaurar PostgreSQL em banco vazio
11 restaurar storage em diretório isolado
12 injetar chave pelo canal seguro
13 apontar instância isolada para DB/storage restaurados
14 subir aplicação
15 GET /health
16 autenticar administrador controlado
17 validar RBAC
18 validar empresa/obra
19 validar perfil biométrico autorizado
20 executar marcação controlada
21 verificar auditoria e ausência de duplicidade
```

### Evidência sanitizada

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

## 7. Contingência

### Câmera

```text
PUNCH_BY_FACE=UNAVAILABLE
DO_NOT_PRETEND_SUCCESS=YES
MANUAL_CONTINGENCY=REQUIRED
```

O operador registra ocorrência manual auditável; não se cria ponto facial retroativo fingindo biometria.

### Rede

```text
OFFLINE_QUEUE=NO
AUTOMATIC_SYNC=NO
```

A versão atual exige contingência manual controlada. Não armazenar biometria improvisadamente no cliente.

### Servidor

Falha deve ser visível. O retorno à operação exige serviço disponível e `/health` válido; registros manuais são reconciliados sem duplicidade.

### Banco

`/health` depende de `SELECT 1`. Banco indisponível não pode resultar em estado verde.

```text
DATABASE_UNAVAILABLE -> SERVICE_ERROR
NO_DB_WRITE -> NO_SUCCESS_RECEIPT
```

O head posterior ao run #63 contém teste automatizado específico para essa regra.

## 8. Reconciliação de contingência futura

Cada ocorrência manual deve carregar identificador, employee, empresa, obra, horário declarado, horário de registro, motivo, responsável, fonte, status de revisão e vínculo futuro com evento de jornada. A importação deverá ser idempotente e append-only/auditável.

## 9. RPO/RTO

```text
RTO_CI_OBSERVED_DB_RESTORE=415ms_RUN_63
RTO_PILOT=UNMEASURED
RPO_PILOT=UNDECIDED
```

RPO/RTO empresariais dependem do ambiente e decisão operacional humana; não são inferidos do CI.

## 10. Testes exigidos

### Unitários

- checksum adulterado falha;
- manifesto incorreto falha;
- confirmação diferente de `RESTORE` falha;
- chave ausente impede descriptografia;
- reconciliação futura é idempotente.

### Integração

- migrations up/down/up;
- DB -> dump -> banco vazio -> restore;
- DB + storage biométrico + chave sintética;
- autenticação/RBAC/escopo após restore;
- punch sintético após restore;
- DB indisponível produz erro, não estado saudável.

### Operacional físico

- câmera ausente;
- rede interrompida;
- servidor parado;
- banco parado;
- runbook executado por operador;
- restore real isolado sem tocar o piloto.

## 11. Estado

```text
BACKUP_CODE_AUDITED=YES
SYNTHETIC_FULL_RESTORE=PASS
RUN_63=PASS
RUN_63_REGRESSION=143_PASSED
RUN_63_DB_RESTORE=415ms
SYNTHETIC_KEY_MASKING_HARDENING=IMPLEMENTED_AFTER_RUN_63
DATABASE_FAIL_CLOSED_TEST=IMPLEMENTED_AFTER_RUN_63
LATEST_HEAD_CI=REQUIRES_FINAL_CONFIRMATION
PILOT_REAL_RESTORE=REQUIRES_PILOT_ENVIRONMENT
PHYSICAL_OUTAGE_EXERCISES=REQUIRE_OPERATOR_AND_PILOT
CONTINGENCY_RUNBOOK=DEFINED
LEGAL_CONFORMITY_DECLARED=NO
```