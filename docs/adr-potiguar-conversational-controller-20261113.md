# ADR — Controlador de Cadastro Conversacional Potiguar (13/11/2026)

**Estado:** implementação local em branch de desenvolvimento isolada. NÃO publicada em produção ou homologação.

## Contexto
O formulário de oito etapas e o painel Gemini Live já existiam na branch feat/potiguar-copilot-onboarding-20261112, porém as sugestões da IA exigiam confirmação manual e não havia cursor determinístico de campo ativo.

## Decisão
- O formulário continua sendo fonte de verdade visual; o servidor Flask continua autorizando, normalizando, criptografando, auditando e persistindo cada versão.
- O módulo static/admin-onboarding-controller.js mantém uma política determinística de próximo campo, condições e lista de campos autorizados para a IA.
- O iframe Gemini recebe somente metadados de etapa/campo/pergunta; nenhum valor já armazenado no formulário é transmitido ao modelo.
- Somente campos seguros da etapa atual e do campo ativo podem ser sugeridos. O navegador valida, preenche visualmente, salva no servidor e avança apenas após resposta bem-sucedida.
- Documentos, contatos, endereço residencial completo, dados financeiros, sensíveis, acesso e biometria continuam no formulário protegido. Ao chegar a um desses campos, o microfone é desligado e a interface orienta o preenchimento local.
- Correções por voz ou texto são restritas a campos ou etapas já alcançados, sem acesso direto ao banco de dados.
- Criação do funcionário, ativação de permissões e biometria exigem controles humanos existentes; nenhum deles é executado pela ferramenta do modelo.
- Em caso de erro de rede/conflito otimista, o formulário bloqueia o avanço.

## Cobertura
- 21 testes JavaScript passaram, incluindo VAD, segurança de sugestões, campos condicionais, seleção do próximo campo e validação local.
- Frontend Vue compilado com Vite.
- Testes Flask do host ficaram bloqueados por dependência Flask ausente no Python de sistema. Nenhum banco produtivo foi usado.
- Voz real no celular e aceitação LGPD ainda não foram validados.

## Limitações e gates
1. Testar Gemini Live real, chamadas de função, desconexões e VAD com dados fictícios.
2. Validar microfone e acessibilidade em celular.
3. Executar testes Flask em ambiente isolado com dependências completas.
4. Revisar privacidade, necessidade dos dados e base legal.
5. Exigir autorização humana antes de publicar; preservar rollback.
