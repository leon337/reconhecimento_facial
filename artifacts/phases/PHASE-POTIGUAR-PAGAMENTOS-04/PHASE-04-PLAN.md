# Plano de execução — Fase 04

Missão: MCF-POTIGUAR-PAGAMENTOS-20261113 (Issue #522).
Classe: C — dados de remuneração e cadastro funcional.
Base de desenvolvimento: `feat/potiguar-pagamentos-mapeamento-fase03-20261114@ee093b90bbd647f0b0d6e0b08b94db377a6bb58a`.
Objetivo: integrar a prévia de planilhas ao banco funcional existente Potiguar V2, sem criar base paralela e sem transferências.
Escopo: identificação provisória por nomes, checagem de existência de ficha V2, isolamento empresa/obra, feedback anonimizado, integrações de rotas/navegação, teste de dados sintéticos e fonte real sem banco.
Não incluído: importação definitiva, edição de cadastro, pagamentos ou salário, alteração do registro financeiro, edição do V2 criptografado, merge/deploy.
Aceite: testes V2 + módulos de pagamentos; parse de nomes em colunas mescladas; detecção de nomes repetidos, homônimos, legados, inativos e dados inválidos; sem exposição ou persistência de PII; integridade do SQLite em testes e fonte original.
Risco conhecido: match por nome é apenas indicação; origem Excel tem #REF!, e dados da coluna B não são chave de identidade forte.
Revisão independente LÉO/Emily: pendente. Gate produção/pagamentos por LEANDRO permanece obrigatório.
