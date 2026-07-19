# FASE 9.5 — Ponto imutável, jornada e fechamento

## Objetivo

Garantir que batidas originais não sejam alteradas ou removidas silenciosamente, registrar correções em trilha separada e permitir fechamento de períodos com cálculo de minutos trabalhados e extras.

## Modelo

- `WorkSchedule`: jornada prevista por empresa e obra.
- `AttendanceEvent`: evento original imutável.
- `AttendanceAdjustment`: correção append-only com justificativa e autor.
- `AttendanceClosure`: fechamento único por colaborador e período.

## Regras

1. Eventos seguem a sequência entrada, início de intervalo, fim de intervalo e saída.
2. Horários devem ser estritamente crescentes.
3. Evento original não pode ser atualizado nem excluído.
4. Correção nunca substitui o registro original.
5. Fechamento já concluído não pode ser executado novamente.
6. Horas extras são calculadas pela diferença positiva entre minutos trabalhados e previstos.
7. Testes usam apenas dados sintéticos.

## Compatibilidade

A tabela legada `pontos` permanece disponível durante a migração incremental. A adoção do novo modelo poderá ocorrer por adaptadores sem apagar o histórico anterior.
