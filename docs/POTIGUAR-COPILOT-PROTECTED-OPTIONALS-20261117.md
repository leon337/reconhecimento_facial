# Correção: Copiloto V2 parava após Nome Completo / CPF

Data: 2026-11-17. Ambiente: desenvolvimento privado `develop`.
O usuário observou que, após o nome completo ser salvo, o Copiloto parava no campo CPF, sem prosseguir com as perguntas.

## Causa reproduzida

O campo CPF, assim como outros campos pessoais, é protegido e opcional no contrato declarativo V2. O fluxo recebia `safe=false`, desligava o microfone e aguardava preenchimento no formulário, sem oferecer uma ação explícita de continuação. Isso era interpretado como travamento, embora o valor do nome tivesse sido salvo.

## Solução implementada

- No painel do Copiloto, para campos protegidos opcionais: **Preencher no formulário**, **Pular este campo**, **Seguir sem opcionais protegidos**. O último comportamento depende de escolha explícita do operador, nunca ativada por padrão; há botão de desativação.
- As ações de pular são executadas localmente, mediante recibos reais da interface. **Nenhum CPF, documento, endereço, salário, PIX ou dado protegido é enviado ao Gemini** para realizar essa operação.
- Os dados omitidos permanecem vazios e visivelmente sinalizados, inclusive para a revisão final. O operador deve preenchê-los quando necessários ao registro real.
- Se o microfone estava ativo antes de uma pausa de privacidade, a voz é retomada ao voltar a um campo seguro, sem encerrar a sessão Live.
- O servidor/formulário não permite ignorar um campo opcional já preenchido (mesmo que ainda não salvo). Campos obrigatórios e condicionais de confirmação (consentimento sensível, biometria, terceiro titular, perfis de acesso) **não são autoignoráveis**.
- A conclusão do funcionário continua sujeita a revisão e aprovação humana no formulário, RBAC e resposta confirmada do Flask. A demonstração pública não é usada para funcionários reais.

## Evidências

- `npm test`: **41/41** JavaScript PASS; `npm run build`: compilação Vite PASS.
- `python -m unittest discover -s tests -p '*_unittest.py'`: **40/40** PASS.
- Chrome, com Gemini Live real e banco sintético privado, `scripts/potiguar_protected_optional_browser_e2e.cjs`: **16 verificações PASS**, incluindo nome salvo, CPF protegido, pulo individual, pulo em lote até Escolaridade, retomada do microfone, 1 WebSocket aberto/0 encerramentos, nenhum erro JS.
- `scripts/potiguar_onboarding_browser_e2e.cjs`: **22 verificações PASS** no navegador móvel sintético, cobrindo as oito etapas, recusa de pular valor protegido não salvo, recusa de pular consentimento biométrico condicional, falha 409, revisão final humana e nenhuma criação automática.
- Desenvolvimento privado foi atualizado e o SHA256 do bundle servido pelo contêiner conferiu com o código compilado.
- Produção `main` não modificada; não se introduziu nova instância pública.

## Operação

Abra `http://127.0.0.1:18953/admin/copilot` no computador, autentique-se e recarregue o navegador para receber a versão nova. Abra um rascunho de funcionário. Após o nome completo, no campo CPF, escolha preencher manualmente ou prosseguir pelos opcionais protegidos. Antes de concluir, confira as pendências no formulário.

**Observação:** não houve cadastro de funcionário real neste teste; use dados reais somente na instância privada com autorização e revisão humana.
