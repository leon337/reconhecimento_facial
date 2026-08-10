# LEA-133 — Auditoria independente MCF

**Papel:** Emily — auditoria independente  
**Missão:** `CPP-COMMERCIAL-REDESIGN-AI-OBS-001`  
**Classe:** C  
**Data:** 10/08/2026  
**PR:** #30  

## 1. Escopo da auditoria

Foram confrontados:

- PRF Classe C;
- estado da `main` e PR #29;
- LEA-85, LEA-95, LEA-96, LEA-97, LEA-98 e LEA-133;
- código vivo de punch, domínio de attendance, observabilidade, backup, biometria e RBAC;
- documentos `01` a `08` da LEA-133;
- workflow Production Validation;
- resultados do GitHub Actions;
- artefato de validação do run #63;
- logs do run #71 após hardening.

A auditoria não presume trabalho físico que não tenha evidência.

## 2. Testes e evidências observados

### Production Validation run #71

```text
RUN_ID=31438214366
JOB_ID=93617079958
RESULT=PASS
REGRESSION=143_PASSED
WARNINGS=26_NON_BLOCKING
MIGRATIONS_UP_DOWN_UP=PASS
POSTGRES_BACKUP=PASS
BACKUP_CHECKSUM=PASS
POSTGRES_RESTORE_EMPTY_DB=PASS
CI_DATABASE_RESTORE_DURATION=258ms
BIOMETRIC_STORAGE_CHECKSUM_RESTORE=PASS
BIOMETRIC_DECRYPTION_WITH_KEY=PASS
BIOMETRIC_DECRYPTION_WITHOUT_KEY=EXPECTED_FAIL_PASS
LOGIN_AFTER_RESTORE=PASS
RBAC_AFTER_RESTORE=PASS
COMPANY_WORKSITE_SCOPE_AFTER_RESTORE=PASS
SYNTHETIC_PUNCH_AFTER_RESTORE=PASS
DATABASE_UNAVAILABLE_FAIL_CLOSED=PASS_STATUS_500
COMPOSE_VALIDATION=PASS
SYNTHETIC_KEY_LOG_MASKING=PASS
```

Artefato do run #71:

```text
ARTIFACT_ID=9081842144
NAME=production-validation-report
SIZE_BYTES=6557
ZIP_SHA256=d16350a5c77c2ac36c5d509764bf68f9fb8a5c142334d7a0caad3c27b3f53793
```

O log do run #71 mostra `BIOMETRIC_ENCRYPTION_KEY: ***` após a geração da chave sintética, comprovando o hardening de mascaramento.

### CI principal

No commit auditado, o job de testes do CI executou sintaxe, testes, Compose de produção e validação Compose/Caddy do piloto com sucesso. A conclusão do job de Docker build deve permanecer verde antes do merge final.

## 3. Auditoria das oito ressalvas

### R1 — baseline GitHub/Linear desatualizada

**Antes:** `CHECKPOINT.md`/`PROJECT_STATE.md` tratavam PR #29 como Draft e LEA-125 como aberta.  
**Agora:** documentos do PR #30 registram PR #29 merged, LEA-125 a LEA-132 Done e FASE 12 ativa.

```text
R1=RESOLVED
```

### R2 — LEA-95 tecnicamente ambígua

A primeira reconciliação de 10/08 classificou incorretamente a LEA-95 como sem evidência. A leitura integral do histórico recuperou confirmação explícita das 20 tentativas e a alteração errada foi revertida mantendo a trilha.

```text
LEA_95=Done
TOTAL=20
NOTEBOOK=10
PHONE=10
SUCCESS=20_BY_OPERATOR_CONFIRMATION
FALSE_POSITIVE=0_REPORTED
ALL_TIMES_LT_10S=REPORTED
R2=RESOLVED
```

A lacuna verdadeira foi deslocada corretamente para LEA-96: os 20 tempos individuais não foram recuperados.

### R3 — LEA-133 não iniciada

Autorização humana ocorreu em 10/08/2026; issue foi movida para `In Progress`; branch, PRF e PR #30 foram criados.

```text
R3=RESOLVED
```

### R4 — fluxo vivo dependente de `Ponto`

O código confirma escrita viva em `Ponto.from_user()` e leitura anti-duplicidade via `Ponto.query`. O domínio `AttendanceEvent` existe, mas não recebe a escrita operacional. O PR #30 produziu mapa completo, mapeamento, sequência de convergência, idempotência, reconciliação e rollback.

```text
PONTO_DEPENDENCY=KNOWN_AND_MAPPED
MIGRATION_PLAN=DEFINED
MIGRATION_IMPLEMENTED=NO_BY_SCOPE
R4=RESOLVED_AS_BASELINE_AND_CONTROLLED_TECHNICAL_DEBT
```

A auditoria não aceita a frase “migrado para AttendanceEvent”. Isso seria falso.

### R5 — observabilidade parcial

A matriz distingue sinais reais, métricas em memória, sinais sem telemetria e componentes que ainda não existem. Foi criada regra explícita contra falso verde.

```text
SEM_TELEMETRIA != SAUDAVEL
R5=RESOLVED
```

Métricas duráveis/heartbeats continuam futuras funcionalidades; não são apresentadas como prontas.

### R6 — câmera/estação/backup/queue/IA sem telemetria

O PR não simula telemetria inexistente. Câmera/estação/backup do piloto aparecem como `TELEMETRY_UNAVAILABLE`; queue/IA/sync como não implementados/não aplicáveis. Backup/restore sintético ganhou evidência real no CI.

```text
FALSE_STATUS_REMOVED=YES
SYNTHETIC_RESTORE_EVIDENCE=PASS
MISSING_COMPONENTS_EXPLICIT=YES
R6=RESOLVED_AS_TRUTHFUL_STATE_MODEL
```

### R7 — decisões jurídicas fora da autoridade de engenharia

Arquitetura registra direção comercial sem inferir REP-P/PTRP/SREP/LGPD conforme. Itens regulatórios permanecem sob validação especializada.

```text
CURRENT_REGULATORY_CLAIM=NONE
LEGAL_CONFORMITY_DECLARED=NO
R7=RESOLVED
```

### R8 — IA não pode tomar decisões trabalhistas/autoritativas

Guardrails proíbem aprovação/alteração de jornada, pagamento, punição, override biométrico, acesso, exclusão biométrica, fraude e conformidade jurídica. Primeiro módulo candidato é diagnóstico/explicação somente leitura.

```text
AUTONOMOUS_LABOR_DECISION=PROHIBITED
R8=RESOLVED
```

## 4. Achados adicionais

### A-01 — série dos 20 tempos não recuperada

**Severidade:** alta para homologação; baixa para fechamento da baseline.  
**Estado:** aberto como dívida explícita.

```text
EXACT_MEAN=UNAVAILABLE
EXACT_MEDIAN=UNAVAILABLE
EXACT_P95=UNAVAILABLE
EXACT_MAX=UNAVAILABLE
STRICT_P95_8S=NOT_PROVABLE
LEA_96=PASS_WITH_WARNINGS
PRODUCTION_HOMOLOGATION=BLOCKED
```

Não há correção honesta possível sem repetir a bateria e preservar os dados.

### A-02 — disaster recovery físico do piloto não foi executado por CI

**Severidade:** alta para homologação.  
**Estado:** dependência de ambiente físico, explicitamente preservada.

O CI prova restore sintético de DB + storage + chave + RBAC + escopo + punch, mas não tem acesso ao volume/chave/dispositivos reais do Linux Mint.

```text
PILOT_REAL_DR=NOT_PROVED
RPO_PILOT=UNDECIDED
RTO_PILOT=UNMEASURED
PRODUCTION_HOMOLOGATION=BLOCKED
```

### A-03 — warning de submódulo no pós-checkout

O job Production Validation termina `success`, porém o post-job registra:

```text
fatal: No url found for submodule path 'app/libs/face_recognition_models' in .gitmodules
```

**Severidade:** baixa nesta missão; dívida de higiene Git/GitHub. Não alterou resultado dos testes porque o pacote `face-recognition-models` é instalado por dependência Python, mas merece tarefa própria antes de o submódulo voltar a ser usado como fonte.

### A-04 — warnings de API legada SQLAlchemy

143 testes passam, mas existem warnings de `Query.get()` legado em rotas/admin.

**Severidade:** baixa. Não bloqueia merge da baseline; registrar para refatoração futura.

### A-05 — higiene da chave sintética

O run #63 usou chave totalmente sintética, sem relação com o piloto, mas o valor gerado aparecia no log. O workflow foi corrigido com `::add-mask::`; o run #71 mostra a variável como `***`.

```text
REAL_SECRET_EXPOSED=NO
SYNTHETIC_LOG_HYGIENE_FINDING=FIXED
```

## 5. Segurança de artefato

O artefato do run #63 foi aberto e inspecionado. Continha JUnit, diagnósticos, lista de restore, métricas e checksums. A busca por chave biométrica, `SECRET_KEY`, DSN, private keys e senha sintética não encontrou segredo operacional real. O JUnit contém apenas nomes de testes.

## 6. Veredito por objetivo

```text
RESERVATIONS_1_TO_8=RESOLVED_AT_BASELINE_GOVERNANCE_ARCHITECTURE_LEVEL
FALSE_CLAIMS_FOUND=NO_AFTER_CORRECTIONS
APPLICATION_REDESIGN_IMPLEMENTED=NO
AI_IMPLEMENTED=NO
PONTO_MIGRATION_IMPLEMENTED=NO
PRODUCTION_HOMOLOGATION=NO
LEGAL_CONFORMITY=NO
```

O termo `RESOLVED` significa que as ressalvas deixaram de ser inconsistências abertas e passaram a ter fonte de verdade, evidência, decisão, plano e gate. Não significa que os módulos futuros descritos nos planos já existam.

## 7. Critério de merge do PR #30

```text
FINAL_PRODUCTION_VALIDATION=PASS_REQUIRED
FINAL_CI_TESTS=PASS_REQUIRED
FINAL_DOCKER_BUILD=PASS_REQUIRED
NO_NEW_UNREVIEWED_FUNCTIONAL_CHANGE=REQUIRED
```

Se esses requisitos permanecerem verdes no head que contém esta auditoria:

```text
EMILY_VERDICT=APPROVE_WITH_WARNINGS_FOR_BASELINE_MERGE
```

Warnings não negociáveis pós-merge:

- produção continua não homologada;
- P95 estrito não comprovado;
- exercício real do piloto ainda necessário para homologação;
- validação jurídica especializada continua externa;
- próxima fase funcional depende de novo gate de Leandro.

## 8. Recomendação ao Léo

Após CI verde no head final, autorizar o merge do PR #30 **somente como fechamento/reconciliação da baseline da FASE 12**. Não interpretar esse merge como autorização de NF-01, redesign, IA, migração ou homologação.

```text
RECOMMENDATION=MERGE_BASELINE_AFTER_FINAL_GREEN_CI
NEXT_FUNCTIONAL_GATE=LEANDRO
```