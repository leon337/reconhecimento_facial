# Central de ocorrências e interface Potiguar

Objetivo: o RH ou gestor encontra marcações que precisam de conferência, abre o dia do funcionário e registra justificativa, revisão ou proposta de ajuste. A proposta não modifica marcações, não registra ponto e não altera o cálculo do espelho.

Regras:
- A listagem usa o mesmo escopo organizacional, período e limite do relatório existente.
- Apenas perfis com permissão de revisão podem registrar eventos; consulta continua separada da escrita.
- Cada evento é acrescentado ao histórico, com responsável, data, motivo criptografado e chave de idempotência. Os dados originais do ponto não são substituídos.
- Uma proposta pode referir uma marcação do mesmo funcionário e dia, ou indicar um horário ausente; permanece pendente e não é aplicada.
- A identificação de pontos simulados é preservada. Nenhum dado de teste é confundido com batidas reais.
- Entrada/saída e intervalo são considerados a partir de registros disponíveis; intervalos ausentes não são inventados.

A interface conserva a paleta Potiguar, as rotas, os filtros e as funcionalidades; o trabalho de legibilidade e navegação é compartilhado entre as telas administrativas. A captura facial, a autenticação e o Copiloto mantêm seus fluxos próprios.

Segurança: POST exige CSRF e permissão própria; consulta e alvos são filtrados por empresa e obra; o horário proposto deve ser válido e uma marcação referenciada precisa pertencer ao usuário e ao dia; auditoria não recebe a justificativa. O texto é criptografado com o mesmo cofre do onboarding e fica indisponível se a chave não estiver acessível.

O fluxo implementado registra propostas; não há aprovação/aplicação de alterações no ponto, exportação fiscal de ajustes ou fechamento de folha.

A migração formal `20261118_10` atende instalações com Alembic. A homologação local criada sem tabela de versão exige criação explícita e segura apenas da nova tabela, após backup consistente. A implantação de produção requer avaliação de migração e dados pela equipe responsável.

Validação planejada: testes unitários e HTTP para escopo, permissões, CSRF, criptografia, idempotência, integridade das batidas e quatro marcações; verificação funcional das telas de dashboard, histórico, relatórios, ocorrências, cadastro e Copiloto.
