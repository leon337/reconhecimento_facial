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
│   ├── dashboard-v3.css
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

Dashboard V3:

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

## Critério visual do Dashboard V3

A V3 preserva a estrutura aprovada da V2 e aplica a RC Visual seguinte:

- remoção do contexto duplicado da sidebar;
- correção do botão hambúrguer que aparecia indevidamente no desktop;
- navegação lateral com melhor conforto tipográfico;
- tratamento de scrollbar somente quando a altura realmente exigir rolagem;
- KPIs alinhados no mesmo eixo visual;
- tipografia operacional ampliada;
- hierarquia de elevação entre KPI, painel principal e painéis auxiliares;
- painel de atenção simplificado para não transformar estado neutro em alerta;
- atalhos com maior altura e legibilidade;
- manutenção de hover, focus-visible e pressed reais;
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
