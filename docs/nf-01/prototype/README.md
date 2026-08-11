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

## Estrutura atual

```text
prototype/
├── index.html
├── README.md
├── assets/
│   ├── design-tokens.css
│   ├── components.css
│   ├── dashboard-v3.css
│   ├── employees-v1.css
│   ├── employees-v1.js
│   ├── new-employee-v1.css
│   ├── new-employee-v1.js
│   └── interactions.js
├── components/
│   └── catalog.html
└── screens/
    ├── 02.01-dashboard.html
    ├── 03.01-funcionarios.html
    └── 03.03-novo-funcionario.html
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

Telas atuais:

```text
http://localhost:4173/screens/02.01-dashboard.html
http://localhost:4173/screens/03.01-funcionarios.html
http://localhost:4173/screens/03.03-novo-funcionario.html
```

## Estado visual

```text
Dashboard Desktop V3........... padrão visual congelado provisoriamente
Funcionários Desktop V1........ aprovado em auditoria visual
Novo Funcionário Desktop V1.... aguardando auditoria visual
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

## Critério visual compartilhado

O padrão atual preserva:

- navegação lateral com conforto tipográfico;
- tipografia operacional ampliada;
- hierarquia de elevação entre superfícies;
- hover, focus-visible e pressed reais;
- microinterações moderadas;
- `prefers-reduced-motion` respeitado;
- alvos interativos mínimos de 44 px;
- design administrativo moderno, sem efeitos excessivos.

## Novo Funcionário V1

A tela preserva os campos existentes no formulário real atual e os reorganiza em:

```text
DADOS PESSOAIS
→ Nome completo
→ Endereço

VÍNCULO OPERACIONAL
→ Matrícula
→ Função
→ Horário
→ Tipo de passagem

ACESSO
→ Usuário
→ Senha
```

Regras da NF-01:

- labels permanecem visíveis;
- placeholder não substitui label;
- o protótipo não envia dados ao backend;
- campos obrigatórios refletem a interface real atual;
- o fluxo pós-cadastro respeita `biometrics:manage` e não mostra CTA proibido para quem não possui essa permissão.

## Próximos testes

Após o padrão visual estabilizar, a NF-01 pode adicionar testes visuais automatizados sem acoplar o protótipo à produção:

```text
unitário: tokens/estados/classes utilitárias do lab
integração: navegação e estados do protótipo
visual: screenshots 360/768/1024/1440
acessibilidade: teclado, focus-visible, contraste e árvore semântica
```

O Design Lab funciona como uma estação de pré-montagem: a peça visual é validada aqui antes de entrar na linha de produção da NF-02.
