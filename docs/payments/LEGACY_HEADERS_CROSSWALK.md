# Potiguar — reconciliação estrutural das cinco planilhas (sem dados de trabalhadores)

## Escopo e proveniência
Arquivos de origem presentes na pasta `PLANILHAS CONTABILIDADE` do Google Drive da Potiguar. Leitura em 2026-11-14, sem alteração do conteúdo original. Somente **cabeçalhos**, posição técnica de aba e metadados de tamanho/quantidade de abas foram utilizados neste documento. Todos os cinco arquivos referem-se ao intervalo 01–07/08/2025.

| Origem | Abas | Aba XML de resumo | Linha de cabeçalho | Modelo da tarifa da coluna F | SHA-256, prefixo |
|---|---:|---|---:|---|---|
| Ajudantes | 133 | `sheet4.xml` | 3 | `DIÁRIA` | `dd7db28840c75988` |
| Montagem | 100 | `sheet4.xml` | 3 | `DIÁRIA` | `696f9eb76bc72bf2` |
| Montagem — Buíque | 102 | `sheet4.xml` | 3 | `DIÁRIA` | `44630a7335996d43` |
| Serralharia | 47 | `sheet3.xml` | 3 | `VALOR UNIT DA HS` | `96aaa2603885ef1a` |
| Diversos | 29 | `sheet2.xml` | 3 | `VALOR UNIT DA HS` | `caa59f6fd4becdc8` |

A numeração XML da aba é um identificador técnico, não o nome da aba, nem necessariamente sua posição de apresentação no Excel. Não há nomes privados de trabalhadores ou planilhas individuais neste documento.

## Cruzamento de cabeçalhos de resumo (A3:P3)
As cinco fontes seguem o mesmo desenho de colunas, com **diferenças semânticas em F, H, I e J**. Os textos abaixo são rótulos, não valores, fórmulas ou decisões sobre remuneração.

| Coluna | Ajudantes / Montagem / Buíque | Serralharia / Diversos | Classificação proposta |
|---|---|---|---|
| A | Funcionários | Funcionários | `employee` |
| B | vazia | vazia | sem mapeamento |
| C | Função | Função | `position` |
| D | Dias trab. | Dias trab. | `days` |
| E | HS trab. | HS trab. | `worked_hours` |
| F | Diária | Valor unit. da HS | `daily` **ou** `hour_unit` |
| G | Valor total | Valor total | `total` (não validado) |
| H | Horas dom./fer. | HS trab. dom./feriado | `sunday_holiday_hours` |
| I | Dom. e feriado | Valor unit. da HS dom. e feriado | `sunday_holiday` **ou** `holiday_hour_unit` |
| J | Total dom./fer. | Total HS dom./feriado | `sunday_holiday_total` |
| K | Total a pagar horas | Total a pagar horas | `hours_payable_total` |
| L | Adicional | Adicional | `additional` |
| M | Desconto | Desconto | `discount` |
| N | Total a pagar | Total a pagar | `total_payable` |
| O | Tipo | Tipo | `payment_type` (sem interpretação) |
| P | PIX | PIX | `pix` (somente o campo/posição) |

## Regras desta fase
- O sistema identifica apenas **coordenadas de cabeçalho e enums conhecidos**, jamais retorna o texto de células de trabalhadores.
- Cada modelo de tarifa é distinto; não converter diária em hora, nem atribuir encargos/descontos por inferência.
- Os totais G/J/K/N são **totalizadores diferentes** e permanecem bloqueados para migração financeira.
- Abas individuais, vínculos, duplicidade de pessoas, fontes de pagamentos e fórmulas requerem reconciliação humana antes de qualquer importação de dados reais.
- Dados de PIX, CPF, remuneração e nome de trabalhador **não foram incluídos no Git**.

## Próxima decisão
A equipe de contabilidade precisará fornecer casos revisados de cada modelo de tarifa, explicitando critérios de jornada e natureza dos totais. Nenhuma transferência poderá ser executada a partir desta comparação.
