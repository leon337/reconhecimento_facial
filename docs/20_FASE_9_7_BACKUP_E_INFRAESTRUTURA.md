# FASE 9.7 — Backup e infraestrutura

## Objetivo

Tornar a implantação reproduzível e estabelecer backup verificável, restauração controlada, persistência de PostgreSQL e biometria, gestão externa de segredos e plano de recuperação.

## Componentes

- `docker-compose.production.yml`: PostgreSQL 16, aplicação e job de backup em rede interna;
- volume `postgres_data`: dados do banco;
- volume `biometric_data`: imagens biométricas privadas;
- volume `backup_data`: arquivos `.dump` e manifestos;
- `scripts/backup_postgres.py`: executa `pg_dump` no formato custom, gera SHA-256 e aplica retenção;
- `scripts/restore_postgres.py`: valida manifesto e checksum antes de executar `pg_restore`;
- `app/infrastructure/backup.py`: núcleo testável e independente da interface de linha de comando.

## Segredos obrigatórios

Os valores abaixo devem ser fornecidos pelo ambiente de implantação e nunca gravados no repositório:

- `SECRET_KEY`;
- `BIOMETRIC_ENCRYPTION_KEY`;
- `POSTGRES_PASSWORD`;
- `POSTGRES_USER`;
- `POSTGRES_DB`.

## Operação de backup

```bash
docker compose -f docker-compose.production.yml run --rm backup
```

Cada execução produz:

```text
database-AAAAMMDDTHHMMSSZ.dump
database-AAAAMMDDTHHMMSSZ.manifest.json
```

O manifesto não contém senha nem a URL completa do banco. Ele registra data, host, nome lógico do banco, nome do arquivo e checksum SHA-256.

## Restauração

A restauração deve ocorrer em ambiente isolado antes de qualquer uso em produção:

```bash
python scripts/restore_postgres.py /caminho/database-AAAAMMDDTHHMMSSZ.dump --confirm RESTORE
```

O comando falha quando:

- a confirmação explícita não é fornecida;
- o arquivo ou manifesto está ausente;
- o checksum não corresponde;
- a URL não aponta para PostgreSQL;
- `pg_restore` retorna erro.

## Política inicial

- backup diário;
- retenção padrão de 30 dias;
- cópia externa do volume de backup;
- teste de restauração mensal;
- acesso restrito aos volumes;
- criptografia de disco ou armazenamento no provedor;
- monitoramento da última execução e do tamanho do backup.

## HTTPS e borda

A aplicação deve ficar atrás de proxy reverso confiável com HTTPS. Apenas o proxy publica portas externas. O PostgreSQL permanece na rede interna. Cabeçalhos encaminhados só podem ser aceitos após configuração explícita de proxy confiável.

## RPO e RTO iniciais

- RPO: até 24 horas;
- RTO: até 4 horas em incidente simples;
- valores devem ser reavaliados após homologação.

## Plano de recuperação

1. declarar incidente e congelar gravações;
2. preservar logs e volumes atuais;
3. provisionar ambiente limpo;
4. restaurar o PostgreSQL após validar checksum;
5. restaurar o volume biométrico correspondente;
6. executar migrations pendentes;
7. validar `/health`, autenticação, isolamento e ponto;
8. liberar acesso gradualmente;
9. registrar evidências e causa raiz.

## Limites

- o agendamento diário depende do orquestrador, cron ou serviço de tarefas do provedor;
- a cópia para armazenamento externo depende do provedor escolhido;
- o backup do banco e o volume biométrico precisam ser versionados de forma coordenada;
- a validação completa de produção pertence à FASE 9.8.
