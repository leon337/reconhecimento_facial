# NF-01 — Design Lab

Laboratório visual isolado para materializar e auditar a NF-01 no navegador antes da NF-02.

## Regra de isolamento

Este diretório **não é produção**.

```text
PROTOTYPE_SCOPE=docs/nf-01/prototype/**
PRODUCTION_TEMPLATES_CHANGED=NO
FLASK_ROUTES_CHANGED=NO
BACKEND_CHANGED=NO
NF02_STARTED=NO
```

O objetivo é reduzir a distância entre especificação e implementação sem alterar a aplicação viva.

## Estrutura

```text
prototype/
├── index.html
├── README.md
├── assets/
│   ├── design-tokens.css
│   ├── components.css
│   └── interactions.js
├── components/
│   └── catalog.html
└── screens/
    └── 02.01-dashboard.html
```

## Como abrir localmente

Na raiz do repositório:

```bash
python3 -m http.server 4173 -d docs/nf-01/prototype
```

Depois abra:

```text
http://localhost:4173/
```

Dashboard V2:

```text
http://localhost:4173/screens/02.01-dashboard.html
```

## O que deve ser auditado

- hierarquia visual;
- legibilidade em zoom normal e ampliado;
- hover, focus-visible e active/pressed;
- profundidade e separação entre superfícies;
- coerência do Design System;
- comportamento em 360, 768, 1024 e 1440 px;
- foco por teclado;
- ausência de dependência funcional do backend;
- ausência de números ou estados apresentados como reais sem aviso de mockup.

## Critério visual do Dashboard V2

A V2 aplica a RC Visual 02 aprovada:

- tipografia mais confortável;
- cards com elevação sutil e superfícies em níveis;
- atalhos reconstruídos;
- botões e links com estados reais de interação;
- tabela/lista com melhor rastreamento visual;
- microinterações moderadas;
- `prefers-reduced-motion` respeitado;
- alvos interativos mínimos de 44 px;
- design administrativo moderno, sem efeitos excessivos.

## Próximos testes

Após o padrão visual estabilizar, a NF-01 pode adicionar testes visuais automatizados sem acoplar o protótipo à produção:

```text
unitário: tokens/estados/classes utilitárias do lab
integração: navegação e estados do protótipo
visual: screenshots 360/768/1024/1440
acessibilidade: teclado, focus-visible, contraste e árvore semântica
```

O Design Lab funciona como uma estação de pré-montagem: a peça visual é validada aqui antes de entrar na linha de produção da NF-02.
