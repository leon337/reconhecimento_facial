# Potiguar — Pré-análise XLSX sem importação financeira

O endpoint /admin/pagamentos/importacoes/analisar faz somente análise estrutural do arquivo enviado por um usuário autenticado e autorizado. Não persiste nem exibe nomes de abas pessoais, nomes de trabalhadores, CPF, PIX, salários ou valores de células.

## Segurança
- Permissão PAYMENTS_EDIT e empresa obrigatórias.
- Arquivo .xlsx até 12 MiB; limite HTTP pontual de 13 MiB, sem modificar o padrão global de 5 MiB.
- Análise ZIP Office Open XML em memória; não extrai arquivos nem executa fórmulas.
- Rejeita caminhos maliciosos, macros, anexos ativos, zip inválido e XML inconsistente.
- Limites: 2.000 partes ZIP; 160 MiB total descompactado; 64 MiB por parte; 4 milhões de células.
- Exibe apenas contagens agregadas, alertas e 16 dígitos do SHA-256.
- Dados são descartados após a requisição; nenhuma importação de pessoas, jornadas ou dinheiro nesta fase.

## A GPU no projeto
scripts/gpu_payment_scenarios.py é um utilitário opcional de QA com moderngl/OpenGL 4.3 (EGL) e NumPy. Testa horários sintéticos em lote numa GPU física; recusa llvmpipe. Não usa dados pessoais e não altera o cálculo canônico de Flask. Executar: python scripts/gpu_payment_scenarios.py --scenarios 524288.

O sistema não depende de CUDA, ROCm, PyTorch ou GPU para operar. Uma única medição não garante aceleração para outras cargas de trabalho.