# PHASE-NF01 — DECISIONS

## D-01 — Não reescrever framework

Flask/Jinja/JS permanecem a base para a NF-02. Redesign não autoriza rewrite.

## D-02 — Separar estação e administração

`Registrar Ponto` continua como shell independente, orientado a uma tarefa.

## D-03 — Verdade operacional

`TELEMETRY_UNAVAILABLE != HEALTHY`; marca verde não implica saúde.

## D-04 — Não inventar telas existentes

Dashboard, empresas/obras dedicadas, registros, saúde e logs são arquitetura de informação/especificação; não foram classificados como UI atual.

## D-05 — Preservar RBAC real

Papéis/permissões atuais são copiados de `app/rbac.py`; permissões futuras citadas são requisitos candidatos, não backend entregue.

## D-06 — Legado de upload

`templates/form.html` e `templates/result.html` são classificados para depreciação por não pertencerem aos blueprints registrados atuais. A NF-01 não os remove.

## D-07 — Legado de jornada

A rota viva continua gravando `Ponto`. A NF-01 não executa nem antecipa a migração para `AttendanceEvent`.

## D-08 — IA

IA permanece futura, assistiva e read-only. Primeiro direcionamento continua diagnóstico + explicação de eventos; nenhum chatbot genérico é objetivo da NF-01.

## D-09 — Acessibilidade

Contraste, foco, teclado, labels, live regions, reduced motion, câmera e baixo letramento são critérios de aceite, não melhorias opcionais.

## D-10 — Gate humano

Publicação/auditoria em PR não equivale ao fechamento formal. LEANDRO mantém o gate de encerramento da NF-01; NF-02 não começa antes dele.
