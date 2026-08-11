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
MERGE_AUTHORIZED=NO
```

O objetivo é reduzir a distância entre especificação e implementação sem alterar a aplicação viva.

## Estrutura atual

```text
prototype/
├── index.html
├── README.md
├── NEW_EMPLOYEE_V2_UX_SPEC.md
├── assets/
│   ├── design-tokens.css
│   ├── components.css
│   ├── dashboard-v3.css
│   ├── employees-v1.css
│   ├── employees-v1.js
│   ├── new-employee-v1.css
│   ├── new-employee-v1.js
│   ├── new-employee-v2.css
│   ├── new-employee-v2.js
│   └── interactions.js
├── components/
│   └── catalog.html
└── screens/
    ├── 02.01-dashboard.html
    ├── 03.01-funcionarios.html
    ├── 03.03-novo-funcionario.html
    └── 03.04-novo-funcionario-v2.html
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
http://localhost:4173/screens/03.04-novo-funcionario-v2.html
```

## Estado visual

```text
Dashboard Desktop V3........... padrão visual congelado provisoriamente
Funcionários Desktop V1........ aprovado em auditoria visual
Novo Funcionário Desktop V1.... preservado para comparação
Novo Funcionário Desktop V2.... criado para auditoria humana
```

## Novo Funcionário V2

O contrato funcional foi fechado antes do desenho. A especificação detalhada está em:

```text
NEW_EMPLOYEE_V2_UX_SPEC.md
```

O wizard possui oito etapas:

```text
0 Tipo de relação
1 Dados pessoais
2 Endereço
3 Vínculo
4 Pagamento
5 Acesso ao sistema
6 Biometria
7 Revisão e conclusão
```

### Regras demonstradas

- uma etapa por vez;
- stepper lateral no desktop;
- progresso compacto em largura reduzida;
- rascunho persistente via `localStorage` somente para demonstração;
- `Salvar e sair`;
- retomada do ponto em que o protótipo parou;
- validações por etapa;
- formulários condicionais por relação/endereço/pagamento/acesso/biometria;
- resumo lateral do rascunho;
- revisão consolidada com `Editar` por seção;
- matrícula representada como geração somente na conclusão;
- conta administrativa separada do funcionário;
- biometria separada da foto administrativa;
- captura biométrica apenas simulada, sem câmera, upload, template ou backend;
- sucesso final apenas demonstrativo.

### Importante sobre o rascunho do mockup

O `localStorage` existe apenas para demonstrar a experiência de autosave/retomada. Durante auditoria, utilizar **dados fictícios**. Não inserir dados pessoais reais no Design Lab.

## O que deve ser auditado

- hierarquia visual;
- legibilidade em zoom normal e ampliado;
- clareza das oito etapas;
- densidade dos formulários;
- diferenciação entre campo obrigatório, opcional e pendência;
- clareza das escolhas condicionais;
- qualidade da revisão final;
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

## Novo Funcionário V1 — referência anterior

A V1 preservava os campos existentes no formulário real e os reorganizava em Dados pessoais, Vínculo operacional e Acesso. Ela permanece no laboratório apenas para comparação visual/histórica.

O V2 **não autoriza** alteração do backend, migração de modelo, criação de novas roles ou implementação real de biometria/pagamento.

## Próximos testes

```text
unitário:
- transições do wizard
- validações e estados
- serialização/restauração do rascunho

integração:
- avançar/voltar
- editar a partir da revisão
- autosave/retomada
- formulários condicionais

visual:
- screenshots 360/768/1024/1440

acessibilidade:
- Tab / Shift+Tab
- foco no primeiro erro
- focus-visible
- contraste
- árvore semântica
```

O Design Lab funciona como uma estação de pré-montagem: a peça visual é validada aqui antes de entrar na linha de produção da NF-02.
