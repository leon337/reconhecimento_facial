# NF-01 — Prompt de continuidade para novo chat

Copiar e colar o bloco abaixo em um novo chat dentro do projeto **CONTROLE DE PONTO**.

---

```text
@GitHub

PROJETO=Controle de Ponto Potiguar
REPOSITORIO=leon337/reconhecimento_facial
FASE=NF-01 — Produto + Design System
BRANCH=docs/nf-01-produto-design-system
PR=32
MODO=CONTINUIDADE_CANONICA
IMPLEMENTACAO_PRODUCAO=PROIBIDA
NF02=PROIBIDA
MERGE=PROIBIDO_SEM_AUTORIZACAO_EXPLICITA_DE_LEANDRO

MISSÃO

Dar continuidade à NF-01 a partir do estado REAL registrado no repositório, sem depender de memória de chats anteriores.

IMPORTANTE

Não assuma que o contexto resumido do ChatGPT é fonte de verdade.
Não reconstrua decisões pela memória.
Não avance por inferência.
Leia primeiro os documentos canônicos no GitHub e use o repositório como fonte de verdade operacional desta continuidade.

ORDEM OBRIGATÓRIA DE RECUPERAÇÃO

1. Ler `DECISOES_CONGELADAS.md`.
2. Ler integralmente `docs/nf-01/12_NF01_CANONICAL_DECISIONS_2026-08-11.md`.
3. Ler integralmente `docs/nf-01/13_NF01_REMAINING_WORK_ROADMAP.md`.
4. Ler `docs/nf-01/10_NF01_CLOSEOUT.md`.
5. Ler `docs/nf-01/06_COMPONENT_CATALOG.md`.
6. Ler `docs/nf-01/05_DESIGN_SYSTEM.md`.
7. Ler `docs/nf-01/08_RESPONSIVE_ACCESSIBILITY.md`.
8. Ler `docs/nf-01/09_TEST_AND_ACCEPTANCE_STRATEGY.md`.
9. Ler `docs/nf-01/prototype/NEW_EMPLOYEE_V2_UX_SPEC.md`.
10. Consultar o estado atual da branch `docs/nf-01-produto-design-system` e do PR #32.

REGRA DE PRECEDÊNCIA

`DECISOES_CONGELADAS.md`
    ↓
`12_NF01_CANONICAL_DECISIONS_2026-08-11.md`
    ↓
`13_NF01_REMAINING_WORK_ROADMAP.md` para status do trabalho restante
    ↓
demais documentos/protótipos da NF-01

Se encontrar conflito documental:
- não escolha silenciosamente;
- identifique o conflito;
- aplique a precedência acima;
- proponha correção documental antes de avançar se necessário.

ESTADO CONCEITUAL QUE DEVE SER CONFIRMADO NO REPOSITÓRIO

- contrato funcional do Novo Funcionário com 8 etapas está congelado;
- política de dimensionamento está congelada;
- CollapsibleSidebar, HorizontalStepper, ContextDrawer, StickyFormActions, ResponsiveFormGrid, FormSection, FieldGroup, EntityPicker e Date/Time/Period já passaram por revisão individual;
- RC transversal fechou 6/6 críticas, 9/9 altas e 6/6 médias em nível de especificação;
- `COMPONENT_CATALOG_BASELINE=FROZEN`;
- `COMPONENT_INDIVIDUAL_REVIEW=IN_PROGRESS`;
- ainda existem componentes do catálogo que precisam de revisão individual profunda;
- o próximo item oficial deve ser obtido do primeiro checkbox pendente de `13_NF01_REMAINING_WORK_ROADMAP.md`;
- no estado esperado ao criar este handoff, o próximo item era `A1 — AppShell`, mas CONFIRME no roadmap antes de continuar.

FORMA DE TRABALHO

Continuar um componente por vez.

Para cada componente, revisar:

1. propósito;
2. anatomia;
3. variantes;
4. estados;
5. comportamento/interações;
6. dependências;
7. RBAC/privacidade quando aplicável;
8. responsividade e Container Queries;
9. teclado/foco/screen reader;
10. loading/empty/error/offline quando aplicável;
11. anti-padrões;
12. testes unitários futuros;
13. testes de integração futuros;
14. testes responsivos/a11y futuros;
15. fazer uma RC curta perguntando se ainda existe melhoria aplicável não incorporada;
16. pedir minha aprovação antes de congelar o componente.

NÃO pule diretamente para wireframes visuais enquanto a revisão individual dos componentes ainda estiver pendente no roadmap.

ANALOGIA OPERACIONAL

Trate o Design System como uma linha de montagem:
catálogo = peças identificadas;
revisão individual = inspeção de cada peça;
RC transversal = teste das interfaces entre peças;
Design Lab = pré-montagem;
NF-02 = produção futura, ainda proibida.

GUARDRAILS

- Não alterar `app/**`.
- Não alterar `templates/**`.
- Não alterar `static/**`.
- Não alterar migrations.
- Não alterar rotas/backend.
- Não alterar `DECISOES_CONGELADAS.md`.
- Não iniciar NF-02.
- Não migrar `Ponto -> AttendanceEvent`.
- Não implementar IA.
- Não implementar observabilidade backend.
- Não fazer deploy.
- Não declarar conformidade jurídica/regulatória.
- Não fazer merge do PR #32 sem minha autorização explícita final.

TESTES

Nesta NF-01, não alegue testes unitários/integrados da nova UI como executados se não foram realmente executados.
Sempre diferencie:
- contrato de testes futuro;
- validação conceitual;
- validação visual no Design Lab;
- testes automatizados reais.

PRIMEIRA RESPOSTA DESTE NOVO CHAT

Antes de propor qualquer nova decisão:

1. confirme que leu as fontes canônicas;
2. informe o HEAD atual da branch e estado do PR #32;
3. mostre um resumo curto do que já está congelado;
4. mostre os próximos 5 itens pendentes do roadmap;
5. indique exatamente qual é o próximo item oficial;
6. não faça nenhuma alteração no repositório nessa primeira resposta;
7. aguarde minha autorização para iniciar a revisão do próximo componente.
```

---

## Finalidade

Este prompt é uma ponte de contexto. O novo chat deve recuperar o estado no GitHub e não confiar no texto deste arquivo quando o repositório mostrar que o roadmap evoluiu depois.
