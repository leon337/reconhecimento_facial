# NF-01 — Revisão individual B2 + B3

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Data:** 2026-08-17  
**Autoridade humana:** LEANDRO  
**Produção:** inalterada  
**NF-02:** não iniciada

---

## B2 — IconButton

```text
B2_ICON_BUTTON=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
```

Contrato aprovado:

- uso para ações secundárias, contextuais ou espaciais;
- ação primária/ambígua não deve virar icon-only;
- família de ícones Lucide; emoji não é linguagem de produção;
- alvo interativo mínimo aproximado de 44x44 px;
- variantes: `ghost`, `subtle`, `destructive`;
- estados: `default`, `hover`, `focus-visible`, `active`, `disabled`, `loading`;
- nome acessível obrigatório;
- tooltip normalmente obrigatório quando não há texto visível, sem substituir `aria-label`;
- mobile não pode depender de hover;
- alvo não deve encolher em telas menores;
- ação sem permissão não fica apenas `disabled`: deve desaparecer quando a política de RBAC assim determinar;
- loading preserva dimensões e usa semântica de ocupação adequada;
- múltiplas ações em tabela devem preferir menu contextual quando isso reduzir ruído e erro;
- toggle icon-only exige estado acessível, como `aria-pressed`, quando aplicável;
- `IconButton` não substitui `Switch`/`Checkbox` em configuração binária genérica.

Testes futuros previstos: unitários, integração com Tooltip/Drawer/Menu/Sidebar, teclado, responsividade e acessibilidade.

---

## B3 — Tooltip

```text
B3_TOOLTIP=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
```

Contrato aprovado:

- tooltip contém apenas informação complementar curta;
- informação obrigatória, regra de negócio, erro crítico ou instrução necessária não pode ficar escondida em tooltip;
- tooltip não substitui nome acessível nem `aria-label`;
- abre por hover e por foco;
- fecha ao perder interação e por `Escape` quando visível;
- não recebe focus trap;
- não contém formulário, botão, link ou outro conteúdo interativo;
- posicionamento pode usar top/bottom/left/right com prevenção de overflow;
- hover usa atraso moderado; foco recebe resposta rápida;
- touch/mobile não depende de tooltip para descoberta essencial;
- long-press não é mecanismo obrigatório;
- `aria-describedby` pode ser usado quando semanticamente adequado, sem duplicação desnecessária do nome acessível;
- largura é limitada e responsiva; tipografia não encolhe para caber;
- estados conceituais suficientes: `hidden`, `opening`, `visible`, `closing`;
- se for necessário carregar dados remotos, conteúdo longo ou interação, outro componente deve ser usado.

Testes futuros previstos: unitários, integração com IconButton/Sidebar/controles, teclado, reposicionamento responsivo e acessibilidade.

---

## Estado da Fase B após os HUMAN_GATES

```text
[x] B1 Button
[x] B2 IconButton
[x] B3 Tooltip
[ ] B4 Tabs

NEXT_OFFICIAL_ITEM=B4_TABS_COMPONENT_REVIEW
```

## Invariantes preservados

```text
PRODUCTION_CODE_CHANGED=NO
NF02_STARTED=NO
BACKEND_CHANGED=NO
DEPLOY=NO
PR32_MERGE=NOT_AUTHORIZED
FINAL_HUMAN_GATE=NOT_READY
```

Este registro preserva as aprovações explícitas de LEANDRO e serve como evidência de continuidade da revisão individual do catálogo.