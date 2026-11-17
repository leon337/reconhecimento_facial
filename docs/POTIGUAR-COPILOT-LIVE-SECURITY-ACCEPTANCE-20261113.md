# Potiguar — Relatório de validação Gemini Live, microfone e privacidade

**Data:** 13/11/2026
**Escopo:** `feat/potiguar-conversational-controller-20261113` em worktree isolada; sem deploy.
**Dados:** testes exclusivamente sintéticos, sem dados reais de funcionários.

## Resultado técnico

| Verificação | Resultado | Evidência |
| --- | --- | --- |
| Gemini 3.8 Live: conexão real com token efêmero | PASS | Sessão Google autorizada com token temporário do cofre da aplicação |
| Gemini 3.8 Live: function calling real | PASS em v1beta | `suggest_onboarding_fields` pediu só `relation_type=CLT intermitente`; sem criação de funcionário |
| Gemini 3.8 Live: voz e transcrição real | PASS em v1alpha | 11 blocos áudio, 4 trechos de transcrição pt-BR, encerramento normal |
| Gemini 3.8 Live: voz em v1beta | FAIL observado | Sessão conectou mas falhou antes de gerar áudio, motivo definitivo não identificado |
| Compatibilidade do protocolo efêmero | CORRIGIDA | Frontend alterado para `httpOptions.apiVersion=v1alpha` conforme aviso do SDK e teste de voz |
| Microfone USB do computador | PASS | 2 s de ALSA `plughw:2,0` convertidos para PCM 16 kHz; saída descartada em `/dev/null` |
| Microfone no Chrome móvel emulado | PASS | `scripts/potiguar_onboarding_browser_microphone_e2e.cjs`: 11 frames PCM, fechamento da trilha/AudioContext, zero exceções |
| Vue iframe sob CSP reforçada | PASS | `scripts/potiguar_onboarding_browser_csp_e2e.cjs`: 9 verificações, sem erro CSP ou requisição externa não autorizada |
| Frontend JS/VAD/privacidade | 25/25 PASS | `npm test` na pasta `frontend/copilot` |
| Flask/RBAC/onboarding | 18/18 PASS | `unittest` em Docker isolado, sem rede |
| Compilação Vue | PASS | `npm run build` |
| Formulário de oito etapas em Chrome móvel emulado | PASS anteriormente | `scripts/potiguar_onboarding_browser_e2e.cjs`: 11 verificações, backend de rascunho simulado |
| Smartphone físico Android/iPhone | PENDENTE | Nenhum aparelho apareceu em `adb devices`; não é simulação equivalente |

## Controles verificados

1. Chave permanente Gemini no cofre local; tokens temporários de sessão; token não impresso nem colocado no Git.
2. Autenticação, autorização de `USERS_CREATE` no iframe, validação por etapa, escopo de rascunho e CSRF verificados por testes Flask.
3. Rascunho protegido com Fernet e revisão humana indispensável antes de criar funcionários.
4. Cabeçalhos `Cache-Control: no-store`, `X-Frame-Options: SAMEORIGIN` e `Permissions-Policy: microphone=(self), camera=()` no iframe.
5. `style-src 'unsafe-inline'` removido do CSP do iframe; Vue compilado ainda carrega normalmente.
6. Entrada de texto com CPF/CNPJ, e-mail, números longos, termos bancários/financeiros ou endereço óbvio é bloqueada localmente antes de `live.sendText`. Três testes específicos adicionados.
7. Homologação ativa: sessão com cookie `Secure`, segredo configurado, chave Fernet em arquivo de permissão restrita e limite diário de sessão.
8. Testes não criaram funcionários nem realizaram biometria ou operação bancária.

## Riscos e gates pendentes

- **BLOQUEADOR DE HOMOLOGAÇÃO MÓVEL:** microfone, consentimento, permissão HTTPS, reconexão e cancelamento devem ser testados no navegador de pelo menos um celular físico com usuário de teste.
- **BLOQUEADOR DE ACEITE INTEGRADO:** testar via interface real o modelo `gemini-3.8-live` com `v1alpha`, voz de entrada/saída, function calling, validação Flask e conclusão manual em uma única sessão. Os testes atuais cobrem partes reais e partes simuladas; não provam a cadeia inteira.
- **REVISÃO LGPD:** nome completo também é dado pessoal; consentimento do operador para enviar dados ao Gemini não estabelece necessariamente a base legal para processar dados do empregado. Validar bases legais, transparência, retenção, transferência internacional, controle de acesso e contratos do provedor com responsáveis pela proteção de dados.
- **LIMITAÇÃO TÉCNICA:** filtros de padrões por texto não identificam todos os dados sensíveis e não podem impedir alguém de ditar informações protegidas enquanto o microfone estiver ativo para um campo permitido. Avisos e bloqueio de mic em campos protegidos reduzem, mas não eliminam o risco.
- **TOKEN DO PROVEDOR:** modelo escolhido é validado no servidor, mas as restrições de modelo do token temporário não foram impostas no contrato do fornecedor em `v1beta`; o risco de reutilização indevida e quotas deve ser reavaliado.
- **PUBLICAÇÃO:** branch sem merge, staging e produção não recebem estas correções até promoção governada e aceite humano.

## Evidências reexecutáveis

```bash
cd frontend/copilot
npm test && npm run check && npm run build

# Python/Flask com dependências instaladas, banco e usuários de TESTE:
python -m unittest tests.test_copilot_onboarding_runtime_unittest tests.test_onboarding_v2_unittest -v
python -m scripts.potiguar_onboarding_e2e_fixture

# Puppeteer e Chrome instalados localmente; definir caminhos por ambiente:
node scripts/potiguar_onboarding_browser_e2e.cjs
node scripts/potiguar_onboarding_browser_csp_e2e.cjs
node scripts/potiguar_onboarding_browser_microphone_e2e.cjs
```

**Decisão:** verificações automatizadas aprovadas na cobertura descrita; liberação final para produção NÃO autorizada. Não afirmar certificação em celular físico ou homologação legal.
