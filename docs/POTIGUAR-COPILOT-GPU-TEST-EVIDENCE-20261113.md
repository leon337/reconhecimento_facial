# Potiguar Copiloto — evidência de testes de cadastro conversacional
**Data:** 13/11/2026
**Escopo:** branch local feat/potiguar-conversational-controller-20261113, derivada de 5d7d4fd.
**Ambiente:** notebook leo-N43SM, testes sintéticos; nenhuma alteração de produção.

## Resultados
| Camada | Resultado | Evidência |
| --- | --- | --- |
| JavaScript/VAD/contrato | 21/21 PASS | npm test em frontend/copilot |
| Flask (dois módulos de onboarding) | 18/18 PASS | unittest em Docker isolado, sem rede; SQLite de teste |
| Navegador Chrome headless (emulação 412 x 896) | 11/11 verificações PASS | scripts/potiguar_onboarding_browser_e2e.cjs |
| Stress GPU Vulkan (RX 580 2048SP) | PASS, 0 divergências GPU x CPU | scripts/potiguar_gpu_onboarding_stress.py |
| Build frontend | PASS | npm run build em frontend/copilot |

## GPU e telemetria
- Backend: Vulkan com RADV (Mesa 25.2.8), placa AMD Radeon RX 580 2048SP, 8 GiB de VRAM.
- 4.194.304 amostras de casos; 626.963 padrões de entrada distintos.
- 200 despachos de computação sobre o lote, equivalentes a 838.860.800 avaliações de contrato.
- Aprovados: 35.985. Rejeitados: 4.158.319. Divergências CPU x GPU: **0**.
- Pico de ocupação GPU observado: 100%; temperatura máxima observada: 42 °C.
- Pico de VRAM total ocupada observado: 1.388,7 MiB. Pico de CPU do sistema observado: 27,8%; RAM usada total observada: 11,24 GiB.
- Telemetria amostrada a cada aproximadamente 100 ms, com apenas 3 amostras durante a execução; os máximos não representam medição contínua e incluem outros processos.
- O teste GPU verifica uma abstração numérica da whitelist e validações de campos, não a inferência do Gemini Live.

## E2E: verificações
1. HTML real das oito etapas renderizado pelo Flask de testes.
2. Inicialização com uma pergunta por vez.
3. Rejeição de mensagem de janela incorreta.
4. Aplicação e salvamento automático do campo permitido.
5. Transição de campo permitido para protegido.
6. CPF fictício preenchido e salvo localmente em viewport móvel.
7. Nenhum CPF enviado nos eventos do iframe.
8. Percurso das oito etapas com regras condicionais e campos opcionais pulados.
9. Revisão final e confirmação humana necessária, sem criação automática.
10. Retorno a etapa anterior para correção.
11. Bloqueio por conflito de versão HTTP 409 sem criação de funcionário.

## Falha encontrada e corrigida
O controlador interrompia a seleção de próximo campo quando o drawer estava oculto para o preenchimento protegido em celular. Removida a dependência de visibilidade do painel em guideNext(); a progressão ocorre no formulário, e os eventos à IA continuam suprimidos enquanto o painel está oculto. Teste E2E foi repetido com sucesso.

## Isolamento e limites
- Flask executado com banco temporário em contêiner sem rede; app produtivo não foi reiniciado.
- O browser usa backend mockado local somente para simular salvamento e conflito; a API real é coberta pelos 18 testes Flask separados.
- Nenhum dado pessoal real nem chave permanente do Gemini foi empregado nos testes.
- A cobertura não prova o diálogo real com Gemini 3.8 Live, a qualidade da voz nem as permissões de microfone em telefone físico.
- O teste não é homologação LGPD, teste de segurança exaustivo, teste de implantação ou autorização de produção.

## Como repetir em ambiente autorizado
1. Usar Python com numpy, psutil e wgpu e GPU Vulkan compatível; executar:
   POTIGUAR_GPU_CASES=4194304 POTIGUAR_GPU_ROUNDS=200 python scripts/potiguar_gpu_onboarding_stress.py
2. Rodar os 18 testes Flask em ambiente isolado com dependências de requirements.txt e banco de teste:
   python -m unittest tests.test_copilot_onboarding_runtime_unittest tests.test_onboarding_v2_unittest -v
3. Na pasta frontend/copilot: npm test && npm run build.
4. Preparar o HTML sintético com scripts/potiguar_onboarding_e2e_fixture.py em ambiente Flask de teste. Executar o navegador com POTIGUAR_E2E_HTML, POTIGUAR_E2E_SCREENSHOT, POTIGUAR_PUPPETEER_MODULE e POTIGUAR_CHROME_BIN definidos conforme ambiente.
5. Validar manualmente microfone e conversas reais em homologação antes da publicação.
