# Jornada e espelho de ponto na homologação

Referência informada: entrada 08:00, intervalo 12:00–13:00, saída 17:00, no horário de Recife. A referência dos limites é de até 5 minutos por marcação e 10 minutos diários, conforme art. 58, §1º, da CLT; variações são indicativas e não representam cálculo definitivo de folha, descontos, horas extras ou decisão jurídica. Jornada, intervalos, instrumentos coletivos e circunstâncias individuais precisam de validação.

Não são geradas batidas de almoço nem é feito desconto automático. A duração do intervalo só é exibida quando duas saídas e duas entradas estão registradas em sequência inequívoca. Intervalo não confirmado e jornada longa exigem revisão; um intervalo inferior a 1h é sinalizado para conferência separada. Dias sem registro não são automaticamente faltas. O tempo apresentado soma pares válidos e, sem batidas de almoço, inclui o período entre entrada e saída.

Parâmetros operacionais: `POTIGUAR_JORNADA_INICIO`, `POTIGUAR_JORNADA_FIM`, `POTIGUAR_INTERVALO_INICIO`, `POTIGUAR_INTERVALO_FIM` (HH:MM); `POTIGUAR_JORNADA_DIAS` opcional com 0–6, 0=segunda. A tolerância de referência da implementação é fixa em 5/10 minutos e não altera marcações ou valores de folha. A regra atual é global ao processo e não tem vigência histórica nem configuração por empregado.

A identificação SIMULADO decorre da tabela de rastreabilidade de homologação. O espelho pode ser impresso ou salvo em PDF pelo navegador. As marcações de demonstração devem permanecer identificadas e não servir a folha.

A imagem pode ser construída com `docker build -f Dockerfile.homologacao-ponto -t potiguar-ponto-hml:intervalo-20261118 .`. Ela depende da imagem-base local identificada no Dockerfile. Não contém banco, credenciais ou biometria.

Fontes primárias consultadas: https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452compilado.htm e https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/fiscalizacao-do-trabalho/Perguntas%20e%20Respostas%20REP .
