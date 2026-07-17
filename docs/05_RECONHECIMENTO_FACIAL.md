# 05 — Reconhecimento facial

## 1. Objetivo

Documentar o fluxo de identificação biométrica usado pelo Controle de Ponto Potiguar, seus limites atuais, mensagens de erro, requisitos de segurança e testes associados.

## 2. Escopo

O módulo reconhece exatamente uma pessoa por imagem enviada ao endpoint de ponto. Ele compara o encoding facial capturado com os encodings previamente cadastrados no banco de dados.

Ficam fora do escopo atual:

- reconhecimento contínuo por vídeo;
- prova de vida;
- múltiplos rostos na mesma captura;
- reconhecimento offline em dispositivo móvel;
- criptografia do encoding biométrico em repouso;
- persistência de consentimento e revogação.

Esses itens devem ser tratados antes de produção quando aplicáveis.

## 3. Componentes

- `app/punch/service.py`: carrega a imagem, extrai o encoding e procura o usuário mais próximo.
- `app/punch/routes.py`: recebe a imagem, interpreta o resultado e registra o ponto.
- `app/models.py`: armazena `face_encoding` e `photo_url` no cadastro do usuário.
- `face_recognition`: biblioteca de detecção, encoding e distância facial.
- `numpy`: conversão e validação dos vetores biométricos.

## 4. Fluxo

```text
Imagem enviada
      │
      ▼
Validação do arquivo
      │
      ▼
Extração dos rostos
      │
      ├── nenhum rosto ───────► no_face
      ├── mais de um rosto ───► multiple_faces
      │
      ▼
Encoding facial de 128 valores
      │
      ▼
Leitura dos encodings cadastrados
      │
      ├── nenhum válido ──────► no_registered_faces
      │
      ▼
Cálculo das distâncias
      │
      ▼
Menor distância <= tolerância?
      ├── não ────────────────► unknown_face
      └── sim ────────────────► usuário reconhecido
```

O pipeline funciona como uma linha de montagem: cada etapa valida e entrega uma saída para a seguinte. Se uma estação falhar, o processo para antes de gravar o ponto.

## 5. Regras implementadas

1. A imagem deve ser enviada no campo `image`.
2. A captura deve conter exatamente um rosto.
3. Encodings cadastrados inválidos são ignorados.
4. O encoding persistido deve representar um vetor de 128 números.
5. O usuário com a menor distância é selecionado.
6. A identificação só é aceita quando a distância é menor ou igual à tolerância configurada.
7. Nenhum ponto é persistido quando o reconhecimento falha.

## 6. Configuração

A tolerância é obtida pela aplicação por meio de:

```text
FACE_MATCH_TOLERANCE
```

Valor padrão atual:

```text
0.6
```

Quanto menor o valor, mais rigorosa é a comparação. Alterações devem passar por testes com dados sintéticos, sem biometria real.

## 7. Respostas do reconhecimento

| Código | Significado | HTTP usado no endpoint |
|---|---|---:|
| `invalid_image` | Arquivo inválido ou não processável | 422 |
| `no_face` | Nenhum rosto detectado | 422 |
| `multiple_faces` | Mais de um rosto detectado | 422 |
| `no_registered_faces` | Nenhuma biometria válida cadastrada | 422 |
| `unknown_face` | Rosto não corresponde a usuário conhecido | 422 |
| `matched` | Usuário identificado | continua o fluxo |

## 8. Dados tratados

| Dado | Classificação | Uso |
|---|---|---|
| Foto enviada | dado pessoal sensível | extração temporária do rosto |
| Encoding facial | dado biométrico sensível | comparação facial |
| Identificador do usuário | dado pessoal | associação do resultado |
| Foto de referência | dado biométrico sensível | apoio ao cadastro e auditoria |

O ambiente de desenvolvimento deve usar somente dados sintéticos. Fotos e encodings reais não podem ser versionados no Git.

## 9. Segurança obrigatória

Antes de produção:

- proteger encodings biométricos em repouso;
- restringir acesso administrativo ao cadastro biométrico;
- registrar auditoria de cadastro, substituição e exclusão;
- definir política de retenção e descarte;
- aplicar HTTPS;
- validar extensão, conteúdo e tamanho do upload;
- avaliar prova de vida para reduzir fraude por fotografia;
- revisar a base legal e a documentação de privacidade.

## 10. Testes

### Testes unitários

Devem cobrir:

- imagem inválida;
- nenhuma face;
- múltiplas faces;
- ausência de encodings cadastrados;
- encoding persistido inválido;
- usuário desconhecido;
- usuário reconhecido dentro da tolerância;
- rejeição acima da tolerância.

### Testes de integração

Devem confirmar:

- resposta HTTP correta para cada erro;
- ausência de gravação quando o reconhecimento falha;
- gravação do ponto apenas após reconhecimento válido;
- bloqueio de batida duplicada após reconhecimento.

## 11. Faça e veja

Com dados totalmente sintéticos, varie a tolerância em ambiente de teste e compare os resultados:

```text
0.45  mais rigoroso
0.50  rigoroso
0.60  padrão atual
```

Nenhuma alteração deve ser promovida sem testes unitários, de integração e revisão dos falsos positivos e falsos negativos.

## 12. Problemas conhecidos

- o encoding é armazenado como JSON em campo de texto;
- não há criptografia de campo implementada;
- não existe prova de vida;
- não há versionamento formal do cadastro biométrico;
- a captura depende da qualidade da imagem e da iluminação;
- o fluxo atual considera apenas uma imagem por solicitação.

## 13. Evoluções futuras

- criptografia de campo;
- prova de vida;
- trilha de auditoria biométrica;
- recadastro controlado;
- detecção de qualidade da imagem;
- reconhecimento offline;
- política automatizada de retenção e exclusão.
