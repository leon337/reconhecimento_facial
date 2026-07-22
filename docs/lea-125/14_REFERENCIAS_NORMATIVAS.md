# Referências normativas auditáveis

**Data de consulta:** 22/07/2026  
**Escopo:** fontes oficiais usadas para verificar afirmações técnicas e normativas da LEA-125.  
**Limite:** esta lista sustenta uma análise informativa e de engenharia; não substitui parecer jurídico, validação trabalhista ou orientação da autoridade competente.

## 1. Registro eletrônico de ponto

### 1.1 Portaria MTP nº 671, de 8 de novembro de 2021 — texto consolidado

- Fonte oficial: Ministério do Trabalho e Emprego.
- Endereço: https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/legislacao/portarias-1/portarias-vigentes-3/portarias-consolidadas-nova/legislacao/legislacao-por-hierarquia-normativa/portarias-1/portaria-671.html/view
- Pontos relacionados:
  - art. 74: vedação a marcação automática e alteração dos dados registrados;
  - art. 75: tipos REP-C, REP-A e REP-P;
  - art. 77: REP-A dependente de instrumento coletivo;
  - art. 78: definição de REP-P;
  - art. 81: geração de AFD pelos sistemas de registro eletrônico;
  - art. 82: função do Programa de Tratamento de Registro de Ponto;
  - Anexos V, VI, VII, VIII e IX: leiautes e requisitos técnicos aplicáveis.

### 1.2 Registro Eletrônico de Ponto — página temática do MTE

- Fonte oficial: Ministério do Trabalho e Emprego.
- Endereço: https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/fiscalizacao-do-trabalho/rep
- Pontos relacionados:
  - apresentação dos três tipos de registradores eletrônicos;
  - distinção entre REP-C, REP-A e REP-P;
  - contexto regulatório do Decreto nº 10.854/2021 e da Portaria nº 671/2021.

### 1.3 Perguntas e Respostas — Portaria nº 671/2021

- Fonte oficial: Ministério do Trabalho e Emprego.
- Endereço: https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/fiscalizacao-do-trabalho/Perguntas%20e%20Respostas%20REP
- Pontos relacionados:
  - pergunta 13: REP-A e ausência de homologação ministerial;
  - pergunta 14: diferença entre REP-A e REP-P e referência ao registro do programa no INPI;
  - perguntas 18 a 20: substituição de AFDT/ACJEF pelo AEJ e função do PTRP;
  - perguntas 22 e 43: Atestado Técnico e Termo de Responsabilidade;
  - perguntas 41 e 42: NSR e AFD;
  - pergunta 52: marcação offline no REP-P;
  - perguntas 53, 54, 57 e 58: fuso, intervalos, jornada e preenchimento do AEJ.

## 2. Proteção de dados e biometria

### 2.1 Lei nº 13.709/2018 — Lei Geral de Proteção de Dados Pessoais

- Fonte oficial: Presidência da República, texto compilado.
- Endereço: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm
- Pontos relacionados:
  - art. 5º, II: dado biométrico vinculado a pessoa natural como dado pessoal sensível;
  - art. 6º: princípios do tratamento;
  - art. 11: hipóteses para tratamento de dados pessoais sensíveis;
  - arts. 18 e seguintes: direitos do titular;
  - arts. 37 a 41: registros, responsabilidades e encarregado;
  - arts. 46 a 49: segurança e boas práticas.

### 2.2 Direitos dos titulares

- Fonte oficial: Autoridade Nacional de Proteção de Dados.
- Endereço: https://www.gov.br/anpd/pt-br/assuntos/titular-de-dados-1/direito-dos-titulares
- Pontos relacionados:
  - informação, confirmação, acesso e correção;
  - necessidade de processo verificável para atendimento dos pedidos.

### 2.3 Glossário da ANPD

- Fonte oficial: Autoridade Nacional de Proteção de Dados.
- Endereço: https://www.gov.br/anpd/pt-br/documentos-e-publicacoes/glossario-anpd
- Pontos relacionados:
  - conceito de dado pessoal sensível;
  - referência expressa a dado biométrico vinculado a pessoa natural.

### 2.4 Materiais da ANPD sobre biometria

- Fonte oficial: Autoridade Nacional de Proteção de Dados.
- Endereços:
  - https://www.gov.br/anpd/pt-br/assuntos/noticias/biometria-e-tema-do-segundo-volume-da-serie-radar-tecnologico
  - https://www.gov.br/anpd/pt-br/assuntos/noticias/coleta-de-dados-biometricos-pela-empresa-tools-for-humanity
- Pontos relacionados:
  - riscos de erro, discriminação, segurança e impacto sobre titulares;
  - biometria como categoria sensível;
  - importância de transparência, finalidade e avaliação de riscos.

## 3. Assinaturas eletrônicas

### 3.1 Lei nº 14.063/2020

- Fonte oficial: Presidência da República.
- Endereço: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14063.htm
- Pontos relacionados:
  - art. 4º: assinaturas eletrônicas simples, avançadas e qualificadas;
  - uso de certificado ICP-Brasil na assinatura qualificada;
  - necessidade de analisar o documento, o signatário e a norma específica antes de definir o padrão.

## 4. Matriz de rastreabilidade das afirmações críticas

| Afirmação técnica da análise | Fonte primária | Local de verificação | Tratamento no projeto |
|---|---|---|---|
| O canal coletor não define sozinho REP-C, REP-A ou REP-P. | Portaria nº 671/2021 | arts. 75 a 78 | decisão arquitetural pendente |
| REP-P possui requisitos próprios e referência a registro de programa. | Portaria nº 671/2021 e Q&A MTE | art. 78, art. 91/Anexo IX e pergunta 14 | exige validação especializada |
| Todos os sistemas eletrônicos devem gerar AFD nas condições aplicáveis. | Portaria nº 671/2021 | art. 81 | não implementado; papel do produto pendente |
| O PTRP trata os dados e gera Espelho e AEJ. | Portaria nº 671/2021 e Q&A MTE | arts. 82–83 e perguntas 18–20 | cadeia regulatória pendente |
| Não se deve tratar “homologação” como requisito genérico de REP-A/PTRP. | Q&A MTE | pergunta 13 e explicações sobre PTRP | evitar alegação comercial |
| Biometria vinculada a pessoa natural é dado pessoal sensível. | LGPD e Glossário ANPD | art. 5º, II | controles de privacidade obrigatórios |
| Consentimento não é automaticamente a única hipótese do art. 11. | LGPD | art. 11, I e II | base legal depende de finalidade e contexto |
| Padrão de assinatura não deve ser escolhido genericamente. | Lei nº 14.063/2020 e Portaria nº 671/2021 | art. 4º e anexos/requisitos específicos | matriz documento × assinatura pendente |

## 5. Regra de uso

1. Toda afirmação normativa deve apontar para a fonte e o dispositivo aplicável.
2. Perguntas e Respostas do MTE são material administrativo dinâmico; registrar a data de consulta e verificar atualizações antes de decisões.
3. Nenhuma referência autoriza declarar que o CPP é REP-P, PTRP, homologado, aderente à LGPD ou conforme à Portaria nº 671/2021.
4. Implementações de AFD, AEJ, comprovantes, assinaturas, retenção e base legal dependem de decisão arquitetural e validação especializada.
5. Em caso de conflito, mudança normativa ou dúvida interpretativa, abrir decisão jurídica e suspender a implementação do requisito afetado.