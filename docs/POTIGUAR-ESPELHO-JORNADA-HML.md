# Jornada e espelho de ponto na homologação

A referência padrão é 08:00–17:00 no horário de Recife. O intervalo, os dias de trabalho e a tolerância não são presumidos e aparecem como não configurados. Dias sem registro não são faltas.

A configuração operacional é feita por variáveis de ambiente do processo:
- `POTIGUAR_JORNADA_INICIO` e `POTIGUAR_JORNADA_FIM`, formato HH:MM (padrão 08:00 e 17:00);
- `POTIGUAR_JORNADA_DIAS`, opcional; números 0–6 separados por vírgulas, 0=segunda, 6=domingo;
- `POTIGUAR_JORNADA_TOLERANCIA_MIN`, opcional, 0–120;
- `POTIGUAR_JORNADA_INTERVALO_MIN`, opcional, 0–480, apenas informação de referência.

Os horários fora da referência são indicadores, não um cálculo de atrasos ou horas extras de folha. A tolerância não configurada significa comparação direta, sem afirmar regra de tolerância. Não há desconto automático de intervalo: o tempo soma pares válidos efetivamente marcados. Dias de trabalho informados não geram faltas automáticas. O espelho individual pode ser impresso ou salvo em PDF pelo navegador; contém dados simulados identificados.

A configuração é global ao processo, não individual ou por empresa, e não constitui histórico versionado de regras. Para uso com empregados reais e regras variadas, é necessário armazenamento por organização/vigência, auditoria e validação de conformidade.

Para construir a imagem de homologação, com a imagem-base local disponível:
`docker build -f Dockerfile.homologacao-ponto -t potiguar-ponto-hml:espelho-20261118 .`

A imagem não contém o banco, credenciais ou biometria; a aplicação precisa dos volumes, variáveis, política de rede e segredos adequados do ambiente de homologação. Não usar para produção sem processo próprio de revisão.
