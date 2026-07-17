# 12 — Backup e Restauração

## 1. Objetivo

Definir uma rotina verificável de backup e restauração para banco, configurações e arquivos necessários à operação do Controle de Ponto Potiguar.

## 2. Princípios

- backup sem teste de restauração não é considerado válido;
- dados biométricos devem receber proteção equivalente à sua classificação sensível;
- backups não devem ser versionados no Git;
- credenciais e chaves não devem ser incluídas em texto aberto;
- cada execução deve gerar evidência de data, origem, destino e resultado.

## 3. Escopo mínimo

```text
Banco de dados
Arquivos biométricos autorizados
Configurações não secretas
Manifesto de versão
Logs necessários à auditoria
```

Segredos devem ser recuperados pelo gerenciador de segredos ou procedimento administrativo, não copiados para o repositório.

## 4. Frequência recomendada

| Tipo | Frequência | Retenção inicial |
|---|---:|---:|
| Operacional | diária | 7 dias |
| Semanal | semanal | 5 semanas |
| Mensal | mensal | 12 meses |
| Antes de mudança crítica | sob demanda | até validação da mudança |

A retenção definitiva depende da política da empresa, da necessidade trabalhista e da revisão LGPD.

## 5. Procedimento para SQLite

Com a aplicação sem novas gravações ou usando mecanismo consistente de snapshot:

```bash
mkdir -p backups
cp instance/ponto.db "backups/ponto-$(date +%Y%m%d-%H%M%S).db"
```

Gerar hash:

```bash
sha256sum backups/ponto-*.db > backups/SHA256SUMS.txt
```

Em produção, preferir ferramenta própria do banco e armazenamento externo criptografado.

## 6. Arquivos biométricos

Caso fotos de referência sejam mantidas por decisão legal e técnica:

- armazenar fora do diretório público sempre que possível;
- criptografar em repouso;
- restringir leitura a processo autorizado;
- incluir no inventário de backup;
- registrar exclusões e expiração;
- nunca usar dados reais em testes.

## 7. Restauração controlada

```text
selecionar backup
→ verificar hash
→ copiar para ambiente isolado
→ restaurar banco e arquivos
→ iniciar aplicação
→ executar testes de integridade
→ registrar resultado
```

Exemplo para ambiente isolado:

```bash
cp backups/ponto-AAAAmmdd-HHMMSS.db instance/ponto-restaurado.db
```

Não sobrescrever diretamente a base ativa antes da validação.

## 8. Testes de restauração

```text
[ ] hash confere
[ ] banco abre sem erro
[ ] tabelas esperadas existem
[ ] usuários sintéticos podem ser consultados
[ ] registros de ponto permanecem íntegros
[ ] aplicação inicia com a cópia restaurada
[ ] autenticação continua funcionando
[ ] logs não revelam segredos
```

## 9. Evidência obrigatória

Cada teste deve registrar:

```text
BACKUP_ID
DATA_HORA_UTC
VERSAO_APLICACAO
ORIGEM
DESTINO
HASH
RESPONSAVEL
RESTORE_TEST
RESULTADO
OBSERVACOES
```

## 10. Incidentes

Em suspeita de corrupção ou perda:

1. suspender gravações quando seguro;
2. preservar evidências;
3. identificar o último backup íntegro;
4. restaurar em ambiente isolado;
5. validar integridade;
6. decidir a troca da base ativa;
7. registrar impacto e dados potencialmente afetados.

## 11. Gate

```text
BACKUP_AUTOMATION_DEFINED=PASS
ENCRYPTED_STORAGE=PASS
RETENTION_POLICY=PASS
RESTORE_TEST=PASS
INCIDENT_PROCEDURE=PASS
OWNER_APPROVAL=PASS
```

Até esses itens serem comprovados no ambiente real, `PRODUCTION_BACKUP_READY=NO`.

## 12. Testes unitários e de integração

O código de negócio continua coberto pelos testes existentes. A rotina de backup exige adicionalmente testes de integração de infraestrutura e um exercício periódico de restauração em homologação.
