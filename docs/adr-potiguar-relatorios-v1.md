# ADR — Relatórios de ponto Potiguar (MVP)

**Situação:** implementado em branch de homologação

## Decisões
- Preservar o monólito modular Flask/SQLAlchemy e o banco atual; não criar microsserviço nem outro banco.
- Consultas protegidas por `Permission.PUNCH_VIEW`, sempre limitadas ao escopo organizacional da sessão.
- Usar a tabela de pontos `Ponto` como fonte operacional de eventos; não criar ou editar eventos ao consultar relatórios.
- Datas armazenadas como UTC sem fuso no legado; interpretar como UTC e converter para `America/Recife` em filtros e apresentação.
- Resumo conservador: só apurar tempo de pares ENTRADA/SAIDA cronologicamente inequívocos com até 24h; sequências ambíguas e períodos abertos exigem revisão humana.
- Turnos que cruzam a meia-noite têm o tempo creditado ao dia da entrada. Isso **não** equivale a cálculo legal de jornada.
- Exportar eventos brutos em CSV com BOM e separador ponto e vírgula, sanitização contra fórmula e cabeçalhos sem cache.
- Limitar período a 31 dias e até 10 mil eventos por consulta; recusar consultas maiores em vez de truncá-las.
- Não calcular atrasos, horas extras, banco de horas, adicional noturno ou folha sem jornada estruturada aprovada e regras auditadas.
- Não exportar templates biométricos, imagens, senhas, segredos ou identificadores sensíveis desnecessários.
- Preservar contêiner anterior e backup do SQLite para reversão no ambiente de homologação.

## Evolução posterior
1. Configurar empresa/obra e vincular administrador e funcionários.
2. Criar jornada contratual estruturada e política de tolerâncias por vínculo e período.
3. Revisão humana de inconsistências, trilha de auditoria e fechamento por período.
4. Relatórios para folha somente após validação jurídica e testes de múltiplos turnos, intervalos e feriados.
