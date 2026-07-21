# FASE 10.1 — HTTPS, câmera exclusiva, prova de vida e desempenho

## Objetivo

O fluxo operacional não aceita fotografias da galeria, arquivos enviados ou imagens previamente salvas. Cadastro e marcação de ponto usam somente a câmera ao vivo, desafio de prova de vida de uso único e identificação automática pelo `face_recognition`.

## Fluxo

```text
câmera HTTPS
→ sequência curta de 6 quadros
→ desafio: piscar uma vez
→ validação de um único rosto
→ verificação de iluminação, nitidez e distância
→ geração do encoding facial
→ identificação automática do funcionário
→ persistência do ponto
```

No cadastro, antes de gravar o perfil, o sistema compara o encoding com os demais funcionários da empresa e rejeita o mesmo rosto associado a outro usuário.

## Orçamento de desempenho

| Etapa | Meta |
|---|---:|
| Abertura e estabilização da câmera | 1–2 s |
| Captura da prova de vida | até 2 s |
| Validação e encoding | até 3 s |
| Comparação e persistência | até 2 s |
| Total alvo por funcionário | abaixo de 10 s |
| Limite máximo do piloto | 15 s |
| P95 desejado | até 8 s |

O JavaScript interrompe a requisição depois de 12 segundos no ponto e 15 segundos no cadastro. O servidor local usa dois workers por padrão para permitir duas validações simultâneas quando houver mais de um dispositivo.

Uma estação física continua atendendo uma pessoa por vez. Para 10–20 pessoas chegando juntas, o objetivo é fluxo contínuo de aproximadamente uma conclusão a cada 3–6 segundos depois do primeiro atendimento. Mais de uma estação ou telefone HTTPS aumenta a vazão.

## HTTPS no celular

Depois de executar:

```bash
bash scripts/start_local_pilot.sh
```

o terminal exibirá:

```text
phone_url=https://IP_LOCAL:8443
certificate_url=http://IP_LOCAL:8000/local-ca.crt
```

No Android:

1. abra `certificate_url` e baixe `potiguar-local-ca.crt`;
2. abra as configurações de segurança;
3. instale o arquivo como certificado de autoridade certificadora para VPN e aplicativos;
4. feche e reabra o navegador;
5. acesse `phone_url`;
6. autorize a câmera.

A chave privada da autoridade certificadora permanece no volume interno do Caddy. O endpoint HTTP disponibiliza somente o certificado público necessário para estabelecer confiança no navegador.

## Limites de segurança

A prova de vida por piscada reduz fraude com fotografia impressa ou imagem estática em outra tela. Ela não é equivalente a uma solução certificada de anti-spoofing com câmera de profundidade, infravermelho ou modelo especializado. O piloto deve registrar tentativas rejeitadas e evoluir para uma camada especializada antes de cenários com risco elevado de fraude.

## Testes obrigatórios

- testes unitários da piscada e do desafio de uso único;
- testes de integração do cadastro e do ponto;
- teste de rosto duplicado;
- verificação de ausência de `input type=file` nas telas operacionais;
- validação do Compose e build Docker;
- teste real no notebook e no celular;
- medição de 20 marcações consecutivas para calcular média e P95.
