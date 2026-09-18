# PHASE-NF01 — REPORT

## Resultado funcional desta fase

A NF-01 produziu uma especificação documental para orientar a NF-02 sem alteração do código de produção.

### Decisões materializadas

- produto congelado preservado;
- três experiências separadas: Funcionário, Gestor/Admin e Suporte;
- Registrar Ponto continua fora do shell administrativo;
- inventário atual diferencia UI viva, legado não registrado e telas futuras;
- árvore oficial de navegação fechada;
- RBAC atual transcrito sem criar autoridade fictícia;
- modelo de estados fechado, incluindo `TELEMETRY_UNAVAILABLE`;
- tokens visuais definidos com contraste-base verificado;
- 26 componentes obrigatórios especificados;
- wireframes das oito superfícies mínimas produzidos;
- responsividade 360/768/1024/1440 e acessibilidade formalizadas;
- contrato de testes para NF-02 definido.

## Riscos preservados

- `Ponto` continua sendo o live write atual;
- `AttendanceEvent` não foi migrado;
- health atual prova apenas app+banco;
- métricas continuam não duráveis;
- câmera/estação/backup não receberam nova telemetria;
- IA não foi implementada;
- nenhum claim jurídico/regulatório foi criado;
- homologação de produção continua bloqueada.

## Mudanças deliberadamente não realizadas

```text
app/** = unchanged
static/** = unchanged
templates/** = unchanged
migrations/** = unchanged
infra/deploy = unchanged
DECISOES_CONGELADAS.md = unchanged
```

## Estado pré-gate

O pacote pode ser auditado e publicado em PR. Encerramento formal depende do gate humano de LEANDRO; enquanto esse gate não ocorrer, NF-02 permanece não autorizada.
