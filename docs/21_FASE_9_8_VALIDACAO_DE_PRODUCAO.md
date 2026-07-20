# FASE 9.8 — Validação de produção

## Objetivo

Executar uma homologação reproduzível antes de qualquer implantação real. Esta fase não introduz biometria real nem autoriza produção por si só.

## Linha de montagem da validação

```text
código aprovado
→ migrations em PostgreSQL
→ suíte automatizada
→ smoke test HTTP
→ isolamento multiempresa e RBAC
→ backup e restauração
→ infraestrutura
→ evidências
→ decisão GO / NO-GO
```

## Gates obrigatórios

| Gate | Evidência automatizada | Critério |
|---|---|---|
| PostgreSQL | serviço PostgreSQL 16 no GitHub Actions | conexão saudável |
| Migrations | `upgrade → downgrade base → upgrade` | zero erro e schema reconstruído |
| Testes | suíte completa em PostgreSQL | 100% dos testes aprovados |
| Ponta a ponta | `/health` e `/punch` via cliente Flask | respostas válidas e headers presentes |
| Multiempresa | testes existentes de escopo organizacional | nenhum acesso cruzado |
| Concorrência/idempotência | testes do domínio de ponto e fechamento | sem duplicação silenciosa |
| Permissões | testes RBAC e rotas administrativas | acesso negado sem permissão |
| Segurança | CSP, anti-frame, anti-MIME e sessão | headers obrigatórios presentes |
| Backup | `pg_dump` real + manifesto + checksum | arquivo íntegro criado |
| Restauração | `pg_restore` em banco separado | banco restaurado e consultável |
| Infraestrutura | `docker compose config --quiet` | configuração válida |
| Artefato | relatório JUnit de homologação | publicado por 14 dias |

## Checklist operacional manual

Antes do GO definitivo, registrar em ambiente de homologação:

- [ ] domínio e HTTPS válidos;
- [ ] `SECRET_KEY` exclusiva e rotacionável;
- [ ] `BIOMETRIC_ENCRYPTION_KEY` armazenada fora do repositório;
- [ ] PostgreSQL gerenciado ou volume persistente monitorado;
- [ ] volume biométrico persistente e com acesso restrito;
- [ ] backup automático agendado;
- [ ] cópia externa do backup em local independente;
- [ ] restauração cronometrada dentro do RTO definido;
- [ ] teste com duas empresas fictícias e duas obras fictícias;
- [ ] teste de perfis administrador, gestor, operador e auditor;
- [ ] teste concorrente de registro de ponto com dados sintéticos;
- [ ] revisão de logs confirmando ausência de senhas e templates biométricos;
- [ ] responsável operacional e canal de incidente definidos;
- [ ] plano de rollback aprovado.

## Regra de decisão

### GO técnico

Somente quando todos os jobs automatizados estiverem verdes, não houver thread de revisão pendente e o checklist manual estiver documentado como concluído em homologação.

### NO-GO

Qualquer falha de migration, isolamento, permissão, backup, restauração, segurança ou persistência bloqueia a produção.

## Limites

O CI valida software e infraestrutura declarativa. Ele não comprova sozinho DNS, certificado, armazenamento externo, rotina real do provedor, capacidade de carga ou procedimentos humanos. Esses itens exigem homologação no ambiente escolhido.
