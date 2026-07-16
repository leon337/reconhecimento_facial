# 11 — Manual do Usuário

## 1. Objetivo

Orientar o colaborador no registro de entrada e saída por reconhecimento facial.

## 2. Antes de registrar o ponto

Confirme:

- seu cadastro está ativo;
- sua biometria foi cadastrada pelo administrador;
- a câmera está funcionando;
- há somente uma pessoa diante da câmera;
- o rosto está bem iluminado e visível.

## 3. Acessar a tela de ponto

Abra:

```text
/punch
```

A tela permite escolher o tipo de registro e enviar a imagem capturada pela câmera.

## 4. Registrar entrada

1. Selecione `ENTRADA`.
2. Posicione o rosto diante da câmera.
3. Mantenha apenas uma pessoa no enquadramento.
4. Faça a captura.
5. Aguarde a confirmação.

Quando o reconhecimento e a gravação forem concluídos, o sistema informa que a entrada foi registrada com sucesso.

## 5. Registrar saída

1. Selecione `SAIDA`.
2. Posicione o rosto corretamente.
3. Faça a captura.
4. Aguarde a confirmação.

O sistema registra o horário no servidor. O horário do telefone ou computador do usuário não é a fonte oficial.

## 6. Fluxo do registro

```text
captura da imagem
→ validação
→ detecção de uma única face
→ comparação com biometrias cadastradas
→ verificação de duplicidade
→ gravação do ponto
→ confirmação
```

## 7. Mensagens comuns

| Mensagem | O que fazer |
|---|---|
| Envie uma imagem da câmera | Faça nova captura e confirme a permissão da câmera |
| Tipo de ponto inválido | Escolha somente `ENTRADA` ou `SAIDA` |
| Imagem inválida ou não processável | Refazer a captura |
| Nenhum rosto foi detectado | Melhorar iluminação e enquadramento |
| Mantenha apenas uma pessoa diante da câmera | Retirar outras pessoas do enquadramento |
| Nenhuma biometria está cadastrada | Procurar o administrador |
| Rosto não reconhecido | Reposicionar-se e, se persistir, solicitar revisão biométrica |
| Aguarde antes de registrar um novo ponto | Evitar batida duplicada e aguardar o tempo informado |
| Entrada/Saída registrada com sucesso | Registro concluído |

## 8. Como melhorar o reconhecimento

- fique de frente para a câmera;
- evite luz forte diretamente atrás da cabeça;
- não cubra o rosto;
- mantenha distância adequada;
- limpe a lente da câmera quando necessário;
- não mova o dispositivo durante a captura.

## 9. Batida duplicada

O sistema possui uma janela padrão de 60 segundos para impedir registros repetidos acidentais.

Quando a duplicidade for detectada:

- o segundo registro não é gravado;
- a tela informa quanto tempo falta para tentar novamente;
- não pressione repetidamente o botão.

## 10. Registro incompleto

A jornada é calculada por pares de horários:

```text
entrada → saída
```

Um número ímpar de registros deixa o dia incompleto. Exemplo:

```text
08:00 ENTRADA
12:00 SAIDA
13:00 ENTRADA
```

Nesse caso, falta uma saída. O fechamento mensal fica bloqueado até a pendência ser tratada por procedimento administrativo autorizado.

## 11. Tolerâncias

O sistema pode aplicar tolerâncias de jornada definidas pela empresa. Os padrões técnicos atuais são:

```text
atraso: até 5 minutos
efeito mínimo de hora extra: 10 minutos
neutralização de saldo: até 5 minutos
```

Esses parâmetros técnicos não substituem contrato, acordo coletivo, política interna ou orientação jurídica.

## 12. Banco de horas

O sistema calcula:

- créditos;
- débitos;
- saldo do período;
- saldo anterior;
- saldo acumulado.

A interface de consulta individual do banco de horas ainda não está disponível no estado atual. Consulte o responsável administrativo pelos canais oficiais da empresa.

## 13. Correção de registro

A correção manual auditável ainda não está disponível na interface atual.

Ao identificar erro:

```text
1. anote a data e o horário aproximado;
2. informe o tipo correto de registro;
3. comunique o administrador ou RH;
4. não tente compensar criando várias batidas;
5. aguarde o procedimento oficial de correção.
```

## 14. Privacidade

A biometria facial é dado pessoal sensível.

O usuário deve:

- não compartilhar sua conta;
- não enviar fotos biométricas por canais não autorizados;
- comunicar suspeita de uso indevido;
- usar somente o equipamento e o fluxo autorizados;
- solicitar informações ao responsável interno sobre tratamento, retenção e exclusão.

## 15. Funções previstas, mas ainda indisponíveis

- consulta individual de histórico;
- consulta individual de banco de horas;
- solicitação digital de correção;
- justificativa de ausência;
- notificações;
- recadastro biométrico pelo próprio usuário;
- aplicativo móvel dedicado.

## 16. Contingência

Quando o sistema, a câmera ou a rede estiverem indisponíveis:

- comunique imediatamente o responsável;
- siga o procedimento alternativo definido pela empresa;
- não use conta de outra pessoa;
- não tente alterar o relógio do dispositivo;
- registre a ocorrência pelos meios oficiais.
