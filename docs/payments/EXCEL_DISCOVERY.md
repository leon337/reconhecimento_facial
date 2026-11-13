# Potiguar — inventário estrutural do Excel de pagamentos

**Fonte:** arquivo original `01.08 A 07.08.2025 - AJUDANTES.xlsx`, localizado na pasta privada Google Drive `PLANILHAS CONTABILIDADE`. Consulta de leitura em 2026-11-13.

## Evidências estruturais (sem dados pessoais)
- 133 planilhas internas; 21 visíveis e 112 ocultas.
- 185 ocorrências da sequência `#REF!` em partes XML de oito abas. Essa contagem é de ocorrências de texto nos arquivos internos do Excel, não de células únicas nem de erros financeiros confirmados.
- 130 partes de aba contêm referências externas ao livro `[1]Folha rosto`; devem ser reavaliadas antes de quaisquer cálculos.
- A estrutura contém lançamentos de entrada, saída, intervalos, totalizadores de jornada, rubricas e referências a pagamentos; detalhes financeiros, nomes e PIX não são reproduzidos neste documento.
- Existem cinco arquivos encontrados na pasta: Ajudantes, Montagem, Montagem-Buíque, Serralharia e Diversos, todos datados de 1º a 7 de agosto de 2025.

## Riscos
1. **Cálculo incorreto:** referências quebradas e valores cacheados podem divergir de fórmulas atuais.
2. **Semântica tarifária desconhecida:** o rótulo “DIÁRIA” aparece em expressões envolvendo horas; não se deve inferir valor/hora ou valor/dia.
3. **Esquema Excel não é banco:** uma aba por trabalhador induz duplicações e relacionamento frágil.
4. **Dados sensíveis:** nomes, PIX e possíveis detalhes contratuais não devem aparecer em logs, testes e repositório.

## Limite do recorte
Nesta fase não houve ingestão de linhas reais no sistema, importação financeira, cálculo de remuneração ou validação contábil dos cinco arquivos. O levantamento foi estrutural para orientar a modelagem segura.
