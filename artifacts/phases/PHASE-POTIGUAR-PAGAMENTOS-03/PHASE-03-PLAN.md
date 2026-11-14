# Plano fase 03 — mapeamento de colunas legadas

- Missão: MCF-POTIGUAR-PAGAMENTOS-20261113, Issue MCF #522.
- Risco: Classe C por dados trabalhistas/financeiros.
- Base: branch `feat/potiguar-pagamentos-preflight-gpu-20261113`, SHA `c723445c3ecc96ea00d151b805c465108ad2a344`.
- Objetivo: comparar cabeçalhos das cinco fontes contábeis e implementar uma prévia de mapeamento sem extrair dados pessoais ou migrar registros.
- Escopo: criar mapeador somente estrutural, UI de revisão, tests de variantes e isolamento, documentação e PRF.
- Fora do escopo: gravação de linhas reais, valores, PIX, tabelas adicionais, transferências, staging/prod, merge.
- Critérios: identificar ambas variantes (diária/hora), preservar diferenças semânticas, não retornar nomes/PIX/valores, respeitar RBAC/CSRF, manter sistema existente intacto, testes e checkpoints.
- Autoridades: LEANDRO humano final; MESTRE orquestrador; revisão/gate independente por LÉO/Emily não simulada.
- Decisão de GPU: parser XML é CPU/I/O bound, GPU não é rota de aceleração adequada nesta fase; preservar suíte GPU sintética anterior.
- Estado inicial: PLANEJADO; alvo final de desenvolvimento: DEV_IMPLEMENTED_REVIEW_PENDING.
