# Potiguar — mapeador de cabeçalhos XLSX (Fase 03)

## Contrato
A pré-análise da fase 02 permanece intacta. O botão adicional **Mapear colunas** no mesmo formulário de upload é um modo exclusivamente read-only. Resultado em memória da requisição; não cria pagamentos, empregados, períodos ou entradas. Nenhuma linha real de trabalhador é importada.

## Componentes
- `app/payment_mapping.py`: reconhece rótulos aprovados, de maneira estrita, a partir de `xl/sharedStrings.xml` ou `inlineStr`. Não copia texto de origem para o retorno; só enum canônico, posição da coluna, número técnico da parte XML e linha de cabeçalho.
- `app/admin/payments_import.py`: depois do pré-analisador de ZIP/segurança, opcionalmente calcula o mapeamento. Reutiliza limites de 12 MiB, controles existentes de autenticação, CSRF e empresa.
- `templates/admin/payments_import.html`: mostra as colunas mapeadas com avisos de revisão obrigatória, sem dados pessoais.
- `tests/test_payment_mapping.py`: dois modelos de resumo sintéticos, variantes `sharedStrings` e `inlineStr`, CSRF, RBAC, privacidade, sem persistência.

## Limites e defesas
- Pré-análise existente valida ZIP, partes, limites e risco de macros/ativos antes do mapeamento.
- Varredura de mapeamento limitada a até 250 partes de aba e 20 linhas de cabeçalho por aba; no máximo 10 sugestões, sem retornar nomes das abas.
- Uma candidata exige pelo menos seis categorias de rótulos numa mesma linha, incluindo funcionário e algum rótulo de totalizador.
- Campos repetidos recebem aviso. Totalizadores distintos mantêm categorias separadas.
- Não lê conteúdo das linhas de trabalhadores para construir a resposta.
- Estado de importação sempre desabilitado (`can_import=False`), até regras futuras e HUMAN_GATE.

## Testabilidade e compatibilidade
O serviço não depende de bibliotecas pesadas de Excel, OCR, GPU nem serviços externos; usa apenas a biblioteca padrão de Python. A GPU AMD continua reservada para testes sintéticos que realmente se beneficiem de paralelismo.

## Escopo não coberto
Não faz conciliação, associação com cadastro de funcionários, importação persistente, correção de planilhas, cálculo financeiro, comparação de valores, PIX ou deploy.
