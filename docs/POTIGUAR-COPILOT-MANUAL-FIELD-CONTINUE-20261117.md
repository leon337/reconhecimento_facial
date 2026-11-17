# Potiguar V2 — continuidade do preenchimento manual

Data: 2026-11-17. Escopo: ambiente privado de desenvolvimento.

## Sintoma e causa

No cadastro V2, o operador clicava em **Preencher no formulário** diante de um campo protegido. O executor `focus_current_field` apenas focalizava o campo e ocultava o painel de conversa. O avanço automático dependia do evento `change` (em campos de texto, normalmente disparado ao perder foco). Sem sair do campo, não havia ação visível para concluir aquela resposta; o fluxo parecia travado.

## Correção

- O executor agora exibe, **ao lado do campo protegido aberto**, um controle local **Salvar e continuar**. Para campos opcionais vazios, também exibe **Pular sem informar**.
- O clique em Salvar e continuar valida o preenchimento, persiste o rascunho no Flask e só então avança à próxima pergunta. Não exige desfocar o campo manualmente.
- Campos vazios ou inválidos não avançam silenciosamente. Se o salvamento falhar, o botão e o campo permanecem disponíveis com erro visível.
- Os controles são removidos ao avançar, mudar de etapa ou interromper a orientação. Consentimentos e campos condicionais críticos não podem ser pulados.
- Somente o formulário autenticado processa o valor protegido; `postMessage` e o Gemini recebem estado e nome de campo, nunca seu conteúdo. A sessão Live permanece aberta.
- Nenhuma alteração foi feita no fluxo de produção, no banco de produção ou na política de conclusão humana.

## Evidências

- 40/40 testes unittest Flask.
- 24 verificações do E2E sintético do formulário V2, inclusive entrada manual sem `blur`, campo vazio e pulo opcional local, revisão humana e rejeição de conflito.
- 18 verificações E2E do shell persistente, com Gemini Live real, usuário/dados **sintéticos**, abertura do campo protegido, botão local, gravação sem `blur`, continuação e retorno da voz; 1 WebSocket, 0 encerramentos, 0 erros JS.
- O contêiner privado de desenvolvimento foi recriado preservando banco, rascunhos e credenciais; hash SHA256 do script servido foi igual ao fonte após publicação.

## Uso

No ambiente privado do computador, abra a tela do cadastro V2, clique em **Preencher no formulário**, preencha somente no formulário e clique no botão **Salvar e continuar** que aparece imediatamente sob o campo. Caso o campo seja opcional e não precise preenchê-lo, use **Pular sem informar**. A revisão final continua obrigatória antes de concluir registros reais.

**Não inserir dados pessoais em scripts, issues ou conversas com o Gemini.**
