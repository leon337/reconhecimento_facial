# NF-01 — Responsividade e Acessibilidade Canônicas

> **Fonte canônica complementar:** `12_NF01_CANONICAL_DECISIONS_2026-08-11.md`.

## 1. Princípio responsivo

```text
RESPONSIVO != DIMINUIR_TUDO
RESPONSIVO = REORGANIZAR + REDISTRIBUIR + LIMITAR + EXPANDIR + COLAPSAR
```

Unidades e mecanismos oficiais seguem `05_DESIGN_SYSTEM.md`:

```text
rem
fr/minmax
clamp
vw/dvh quando necessário
container queries / cqi
ch
%
px apenas como exceção técnica
```

`360 / 768 / 1024 / 1440` são **alvos mínimos de teste**, não quatro layouts rígidos.

Também testar larguras intermediárias e containers independentes do viewport.

---

# 2. Shell por faixa de espaço

## Desktop largo

- sidebar expandida ou compacta, escolha do usuário;
- conteúdo recupera imediatamente a largura liberada;
- ContextDrawer abre sob demanda;
- formulário não cresce indefinidamente; mantém limite confortável de edição;
- Dashboard e DataTable usam espaço adicional para contexto útil, não para decoração.

## Aproximadamente 1024

- sidebar compacta por padrão/preferência;
- grid reduz colunas quando necessário;
- ContextDrawer pode virar overlay;
- tabela preserva campos essenciais e ações.

## Aproximadamente 768

- sidebar compacta e expansão overlay;
- stepper reduzido;
- formulário 1–2 colunas conforme container real;
- drawers/modais overlay;
- nenhuma dependência de hover.

## Aproximadamente 360

- sidebar não ocupa coluna permanente; vira menu overlay;
- wizard mostra `Etapa X de 8`, progresso simplificado e `Ver etapas` sob demanda;
- formulário em uma coluna;
- ação primária pode ocupar largura inteira;
- ContextDrawer full/near-full overlay;
- StickyFormActions entra em modo seguro para teclado virtual;
- sem overflow horizontal indevido.

---

# 3. Container-first

Componentes reutilizáveis devem responder ao espaço que realmente recebem quando isso for mais correto do que olhar apenas para o viewport.

Exemplo conceitual:

```text
mesmo componente
  ↓
Dashboard: container largo → 3 colunas
Drawer: container médio → 2 colunas
Mobile: container estreito → 1 coluna
```

Breakpoints estruturais devem nascer da perda de legibilidade/funcionalidade, não do nome do aparelho.

---

# 4. Ordem semântica

```text
READING_ORDER = FOCUS_ORDER = TASK_LOGIC
```

Grid/Flex podem redistribuir espaço, mas CSS não pode produzir uma ordem visual diferente da ordem de leitura/foco.

Exemplo correto:

```text
Desktop
Nome       CPF
Telefone   E-mail

Mobile
Nome
CPF
Telefone
E-mail
```

---

# 5. Acessibilidade obrigatória

## Foco

- foco visível;
- não remover outline sem substituição;
- modal/drawer gerenciam foco e devolvem ao trigger;
- step change move foco para o heading da nova etapa;
- erro múltiplo anuncia resumo e direciona ao primeiro erro quando apropriado.

## Teclado

Todas as ações administrativas relevantes devem funcionar sem mouse:

- sidebar;
- stepper;
- `Ver etapas`;
- filtros;
- tabelas/menus;
- combobox/entity picker;
- tabs;
- modal;
- drawer;
- paginação;
- wizard;
- câmera/ações de captura quando tecnicamente disponíveis.

Combobox:

```text
Tab      entra/sai
↑ ↓      percorre
Enter    seleciona
Esc      fecha
texto    pesquisa
```

## Labels

- label persistente;
- placeholder somente como exemplo;
- ajuda/erro associados por `aria-describedby`;
- obrigatório por semântica/contrato;
- opcional marcado `(opcional)`;
- condicional explicado por texto.

## Estado

Todo estado relevante usa texto explícito + semântica; ícone/cor são complementares.

## Targets

Alvo interativo confortável equivalente ao padrão aproximado de 44 CSS px quando aplicável, expresso preferencialmente em `rem` no Design System.

---

# 6. HorizontalStepper acessível

Visualmente icon-first, semanticamente completo.

Cada etapa precisa de:

- ícone oficial;
- tooltip desktop;
- `aria-label`;
- texto acessível invisível;
- `aria-current="step"` quando atual;
- estado concluída/futura/erro/needs-review sem depender só de cor.

`Ver etapas` oferece versão textual sob demanda.

Mobile não comprime oito ícones até ficarem ilegíveis.

---

# 7. ContextDrawer e modais

## Drawer

- botão possui `aria-expanded`/`aria-controls`;
- título associado;
- Escape fecha;
- overlay gerencia foco quando modal;
- foco retorna ao trigger;
- scroll interno não aprisiona usuário;
- abrir/fechar preserva formulário.

## ConfirmationModal

- `role=dialog`/`aria-modal=true`;
- título e consequência explícitos;
- foco inicial seguro;
- Enter não dispara destruição por acidente;
- Escape cancela quando permitido;
- foco retorna à origem.

---

# 8. Erros

Hierarquia:

```text
SISTEMA/WIZARD
→ ETAPA
→ SECAO
→ CAMPO
```

Após tentativa inválida:

1. manter valores seguros;
2. mostrar resumo quando houver múltiplos problemas;
3. associar erro ao campo;
4. abrir/indicar seção recolhida com erro;
5. mover foco de forma previsível.

Taxonomia:

```text
VALIDATION_ERROR
BUSINESS_RULE_ERROR
PERMISSION_ERROR
CONFLICT_ERROR
NETWORK_ERROR
SYSTEM_ERROR
SUBMIT_OUTCOME_UNKNOWN
```

Erro crítico não é somente toast.

---

# 9. Sessão, conflito e navegação

## Browser

- refresh restaura o mesmo draft e mesma etapa quando possível;
- back/forward respeitam o histórico do wizard;
- navigation guard só aparece com risco real de perda;
- link direto para etapa futura respeita pré-requisitos.

## Sessão expirada

```text
sessao expirou
→ login
→ revalidar identidade/permissao/revision
→ retomar ou detectar conflito
```

Frames biométricos brutos não entram em recuperação local genérica.

## Conflito

- conflito é persistente;
- autosave pausa;
- dados locais são preservados temporariamente;
- conclusão bloqueada até resolução.

---

# 10. Mobile keyboard safe

StickyFormActions não é “fixa a qualquer custo”.

Quando teclado virtual reduzir o viewport:

- não cobrir campo focado;
- usar `dvh`, safe-area, scroll-padding e scroll-to-field quando necessário;
- reorganizar ações;
- permitir que a barra volte ao fluxo normal temporariamente.

Teste também orientação portrait/landscape quando relevante.

---

# 11. Reduced motion

```text
prefers-reduced-motion: reduce
```

- remover movimentos não essenciais;
- remover shimmer quando aplicável;
- reduzir transições de drawer/sidebar/modal;
- manter mudança de estado perceptível imediatamente;
- nunca remover informação junto com a animação.

---

# 12. Ícones

Família oficial: **Lucide**.

Regras:

```text
decorativo → aria-hidden
acao       → aria-label + tooltip quando necessário
estado     → texto acessível + icone
```

Emoji não é iconografia de produção.

---

# 13. CameraPanel

Estados acessíveis:

```text
AGUARDANDO_PERMISSAO
CAMERA_INDISPONIVEL
PRONTA
CAPTURANDO
VALIDANDO_QUALIDADE
PROCESSANDO
SUCESSO
FALHA
```

- preview com nome/descrição acessível apropriada;
- progresso textual;
- live region sem spam;
- câmera negada/indisponível com orientação acionável;
- upload/galeria não pertence ao onboarding biométrico normal.

---

# 14. PunchResult

Funcionário precisa compreender:

```text
Funcionou?
Por que nao funcionou?
O que fazer agora?
```

- success/failure como heading/status claro;
- foco pode ir ao resultado final quando melhorar leitura;
- CTA vem logo após a mensagem;
- detalhes técnicos/request ID ficam fora da superfície principal do funcionário.

---

# 15. Zoom e reflow

Obrigatório validar:

- zoom 200%;
- sem perda funcional;
- sem clipping de texto;
- sem sobreposição de StickyFormActions;
- sidebar/drawer/stepper adaptam-se;
- textos com `ch`/limites de leitura não quebram o fluxo.

---

# 16. Matriz mínima de validação

| Cenário | Deve validar |
|---|---|
| 360 | overlay menu, wizard simplificado, 1 coluna, keyboard safe, sem overflow |
| 768 | sidebar compacta/overlay, drawer íntegro, grid coerente |
| 1024 | sidebar compacta, tabela/form legíveis, foco coerente |
| 1440 | conteúdo útil sem esticar excessivamente, shell expandido/compacto |
| 200% zoom | reflow sem perda funcional |
| keyboard-only | fluxo completo das ações permitidas |
| reduced motion | sem animação não essencial |
| screen reader | headings, stepper, erros, drawer/modal, camera e resultado |

---

# 17. Decisão

```text
RESPONSIVE_SPEC=CANONICALIZED
ACCESSIBILITY_SPEC=CANONICALIZED
TARGET_WIDTHS=360_768_1024_1440_PLUS_INTERMEDIATE
CONTAINER_QUERIES=ADOPTED_WHEN_APPROPRIATE
SEMANTIC_DOM_ORDER=FROZEN
MOBILE_KEYBOARD_SAFE=FROZEN
STEP_FOCUS_MANAGEMENT=FROZEN
STEPPER_DISCOVERABILITY=FROZEN
REDUCED_MOTION=FROZEN
```
