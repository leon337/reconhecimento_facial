# 06 — Controle de ponto

## 1. Objetivo

Documentar o registro de entrada e saída, a proteção contra duplicidade, o cálculo diário da jornada, as tolerâncias, o banco de horas e o fechamento mensal.

## 2. Escopo

O núcleo atual cobre:

- registro de `ENTRADA` e `SAIDA`;
- reconhecimento facial antes da gravação;
- bloqueio de batidas duplicadas;
- jornada contínua ou com intervalo;
- cálculo diário por pares de registros;
- atraso e saída antecipada;
- tolerâncias configuráveis;
- saldo bruto e saldo tratado;
- banco de horas por período;
- fechamento mensal sem pendências.

Ficam fora do escopo atual:

- persistência do fechamento mensal;
- ajustes manuais auditáveis;
- aprovação de justificativas;
- escalas alternadas e banco de folgas;
- adicional noturno;
- feriados e calendários regionais;
- integração com folha de pagamento.

## 3. Componentes

- `app/punch/routes.py`: endpoint de registro.
- `app/punch/rules.py`: proteção contra duplicidade.
- `app/jornada.py`: interpretação do horário contratado.
- `app/calculo_jornada.py`: cálculo diário e tolerâncias.
- `app/banco_horas.py`: consolidação e fechamento mensal.
- `app/models.py`: modelos `User` e `Ponto`.

## 4. Fluxo de registro

```text
Imagem + tipo de ponto
          │
          ▼
Validação da solicitação
          │
          ▼
Reconhecimento facial
          │
          ▼
Usuário identificado?
   ├── não ─► rejeitar
   └── sim
          │
          ▼
Batida recente dentro da janela?
   ├── sim ─► HTTP 409
   └── não
          │
          ▼
Persistir Ponto
          │
          ▼
Retornar HTTP 201
```

Essa sequência funciona como uma linha de montagem: validação, identificação, regra antifraude e persistência. Nenhuma etapa posterior deve ocorrer quando uma etapa anterior falha.

## 5. Tipos de ponto

O endpoint aceita somente:

```text
ENTRADA
SAIDA
```

Um tipo diferente é rejeitado com HTTP 400.

O modelo persiste:

- usuário;
- data e hora UTC;
- tipo do ponto.

## 6. Bloqueio de duplicidade

A aplicação verifica se o mesmo usuário possui uma batida recente dentro da janela configurada.

Configuração atual:

```text
PUNCH_DUPLICATE_WINDOW_SECONDS=60
```

Quando bloqueada, a solicitação retorna:

```json
{
  "status": "error",
  "code": "duplicate_punch",
  "message": "Aguarde antes de registrar um novo ponto.",
  "retry_after_seconds": 60
}
```

O retorno HTTP é `409 Conflict`, e nenhum novo registro é criado.

## 7. Jornada

São aceitos dois formatos principais:

```text
08:00-17:00
08:00-12:00,13:00-17:00
```

O primeiro representa jornada contínua. O segundo desconta o intervalo informado.

A duração prevista é calculada pela diferença entre início e fim, menos o intervalo quando presente.

## 8. Cálculo diário

Os registros são ordenados e processados em pares:

```text
entrada 1 → saída 1
entrada 2 → saída 2
```

Cada par válido contribui para o total trabalhado.

Um número ímpar de registros marca o dia como incompleto:

```text
registros_incompletos=true
```

O resultado diário preserva:

- duração prevista;
- duração trabalhada;
- atraso tratado;
- saída antecipada tratada;
- saldo tratado;
- atraso bruto;
- saída antecipada bruta;
- saldo bruto;
- indicador de incompletude.

## 9. Tolerâncias

Valores padrão:

| Regra | Tolerância |
|---|---:|
| Atraso | 5 minutos |
| Hora extra | 10 minutos |
| Neutralização do saldo | 5 minutos |

Regras:

1. atraso até 5 minutos é neutralizado;
2. saldo negativo de até 5 minutos é neutralizado;
3. hora extra abaixo de 10 minutos não gera crédito;
4. valores brutos são preservados para auditoria;
5. tolerâncias negativas são rejeitadas.

## 10. Banco de horas

A consolidação considera apenas o saldo já tratado pelas tolerâncias.

O resumo contém:

- saldo anterior;
- créditos;
- débitos;
- saldo do período;
- saldo acumulado;
- dias processados;
- dias pendentes.

Dias incompletos não alteram o saldo e são registrados como pendentes.

```text
saldo do período = créditos - débitos
saldo acumulado = saldo anterior + saldo do período
```

## 11. Fechamento mensal

O fechamento exige:

- mês entre 1 e 12;
- todos os resultados pertencentes ao mês informado;
- ausência de dias pendentes.

O fechamento é representado por uma estrutura imutável contendo:

- ano e mês;
- saldo anterior;
- créditos;
- débitos;
- saldo do mês;
- saldo acumulado;
- dias processados;
- instante do fechamento.

Atualmente, essa estrutura ainda não é persistida em banco de dados.

## 12. Casos de erro

| Situação | Resultado |
|---|---|
| imagem ausente | HTTP 400 |
| tipo de ponto inválido | HTTP 400 |
| reconhecimento falhou | HTTP 422 |
| batida duplicada | HTTP 409 |
| mês inválido | `ValueError` |
| resultado de outro mês | `ValueError` |
| registro incompleto no fechamento | `ValueError` |
| tolerância negativa | `ValueError` |

## 13. Auditoria

Antes de produção, o sistema deve registrar de forma rastreável:

- criação do ponto;
- tentativa duplicada;
- alteração manual;
- justificativa;
- responsável pela correção;
- valor anterior e novo valor;
- fechamento e eventual reabertura;
- exportação de relatórios.

Nenhum ajuste manual deve apagar o histórico original.

## 14. Testes

### Testes unitários

Devem cobrir:

- interpretação de jornadas;
- duração prevista com e sem intervalo;
- registros em ordem diferente;
- registros incompletos;
- atraso e saída antecipada;
- cada tolerância no limite, abaixo e acima;
- saldo positivo, negativo e neutro;
- consolidação de créditos e débitos;
- saldo anterior e acumulado;
- bloqueio de fechamento com pendências;
- rejeição de mês inválido ou dados de outro mês.

### Testes de integração

Devem confirmar:

- gravação de ponto reconhecido;
- ausência de gravação em erros;
- bloqueio de duplicidade;
- códigos HTTP e payloads;
- integração entre reconhecimento, regras e banco.

## 15. Faça e veja

Em ambiente de teste, use horários sintéticos e compare:

```text
08:00, 12:00, 13:00, 17:00  → jornada completa
08:04, 12:00, 13:00, 17:00  → atraso tolerado
08:06, 12:00, 13:00, 17:00  → atraso contabilizado
08:00, 12:00, 13:00          → dia pendente
08:00, 12:00, 13:00, 17:09  → extra não creditada
08:00, 12:00, 13:00, 17:10  → extra creditada
```

As variações devem ser validadas por testes unitários e de integração.

## 16. Problemas conhecidos

- horários são gravados em UTC, mas ainda falta política explícita de apresentação por fuso;
- o fechamento não é persistido;
- não há fluxo de justificativa e aprovação;
- não há trilha completa para correções manuais;
- feriados e escalas especiais não são tratados;
- o modelo atual aceita apenas `ENTRADA` e `SAIDA`.

## 17. Evoluções futuras

- persistência do fechamento mensal;
- reabertura controlada;
- justificativas e anexos;
- fluxo de aprovação;
- calendário de feriados;
- escalas múltiplas;
- adicional noturno;
- integração com folha;
- relatórios e exportações;
- assinatura eletrônica do espelho de ponto.
