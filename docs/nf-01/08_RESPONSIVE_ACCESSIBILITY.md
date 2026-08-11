# NF-01 — Responsividade e Acessibilidade

## 1. Matriz de responsividade

### 360 px — telefone mínimo

**Navegação**
- admin: header compacto + botão de menu; sidebar vira drawer;
- breadcrumb mostra pai imediato + página atual;
- Registrar Ponto permanece sem menu admin.

**Cards**
- uma coluna;
- sem métricas lado a lado se o rótulo perder leitura;
- prioridade ao estado e ação.

**Tabelas**
- não comprimir colunas até ilegibilidade;
- converter visão principal em cards/linhas resumidas quando necessário;
- detalhes secundários em `DetailDrawer` full-screen;
- manter acesso a cabeçalhos/semântica tabular quando tabela horizontal for usada.

**Formulários**
- uma coluna;
- campos 100%;
- labels acima do controle;
- ação primária 100% quando melhora alcance.

**Câmera**
- preview ocupa largura disponível;
- controles logo abaixo;
- instruções curtas;
- resultado deve permanecer no viewport sem exigir procurar a mensagem.

**Modais/drawers**
- drawer de detalhe pode ocupar tela inteira;
- confirmation modal com margens mínimas e ações empilhadas quando necessário.

### 768 px — tablet

- navegação pode permanecer em drawer ou sidebar compacta conforme espaço real;
- cards em duas colunas quando comparáveis;
- formulários permitem duas colunas somente para campos curtos relacionados;
- tabelas preservam colunas essenciais e scroll horizontal controlado;
- câmera continua central, sem painéis laterais concorrentes;
- drawers usam 70–85% da largura.

### 1024 px — notebook/tablet landscape

- sidebar persistente permitida;
- header mostra empresa/unidade/usuário sem ocultar título;
- cards em 2–4 colunas;
- DataTable usa densidade padrão/compacta;
- filtros podem ser inline;
- formulários usam grid de duas colunas com leitura linear coerente;
- DetailDrawer lateral de aproximadamente 420–520 px.

### 1440 px — desktop de dados

- sidebar persistente;
- conteúdo limitado por max-width, sem esticar texto indefinidamente;
- dashboard pode usar 12 colunas;
- tabelas ganham colunas secundárias, mas ações permanecem agrupadas;
- health cards e eventos podem coexistir em regiões lado a lado;
- Registrar Ponto continua centralizado e não usa espaço extra para adicionar complexidade.

## 2. Prioridade de informação por breakpoint

| Recurso | 360 | 768 | 1024 | 1440 |
|---|---|---|---|---|
| Funcionário | nome, matrícula, biometria | + função | + unidade | + metadados autorizados |
| Registro | hora, pessoa, tipo | + unidade | + origem/status | + IDs/detalhes curtos |
| Health | estado + componente | + recência | + fonte | + tendência quando existir |
| Camera | preview + ação | igual | igual | igual, largura limitada |

Aumento de viewport aumenta contexto, não adiciona recursos inexistentes.

## 3. Acessibilidade — requisitos obrigatórios

### Contraste

- texto normal: mínimo WCAG AA 4.5:1;
- texto grande: mínimo 3:1;
- componentes/foco essenciais: mínimo 3:1 contra adjacentes;
- combinações principais dos tokens já foram verificadas em `05_DESIGN_SYSTEM.md`;
- NF-02 deve checar estados hover/disabled/focus e combinações reais.

### Foco visível

- ring de 3 px + offset 2 px;
- nunca depender do browser default após removê-lo;
- modal/drawer captura foco e devolve ao disparador;
- skip link visível ao foco no AppShell;
- câmera e ações seguem ordem lógica.

### Teclado

Todas as ações administrativas devem ser operáveis sem mouse:
- menu;
- filtros;
- tabela/menus de linha;
- tabs;
- modal;
- drawer;
- paginação;
- cadastro;
- remoção biométrica.

A câmera pode depender de hardware, mas seus controles devem ser acionáveis por teclado.

### Labels

- todo input possui label persistente;
- placeholder é exemplo/ajuda, nunca substituto de label;
- ajuda e erro conectados por `aria-describedby`;
- campos obrigatórios indicados por texto/semântica, não somente asterisco/cor.

### Áreas clicáveis

- mínimo 44×44 px;
- IconButton com nome acessível;
- linhas de tabela não se tornam “clicáveis invisíveis” sem foco e sem semântica;
- links mantêm affordance de link.

### Estado não dependente apenas de cor

Cada estado usa:

```text
texto explícito
+ ícone opcional
+ cor semântica complementar
```

Exemplos:
- `Ativa` + ícone + cor;
- `Telemetria indisponível` + ícone neutro + texto;
- `Degradado` + descrição do impacto.

### Live regions

- `PunchResult`: `aria-live="polite"` para progresso e resultado esperado; `assertive` apenas para falha crítica que exija atenção imediata;
- captura biométrica: progresso anunciado sem repetir a cada 100 ms;
- toasts não duplicam anúncio crítico;
- erros de formulário recebem foco/resumo quando submissão falhar.

### Reduced motion

Ao detectar `prefers-reduced-motion: reduce`:
- remover shimmer animado;
- reduzir/zerar transições de drawer/modal;
- nenhum movimento decorativo;
- não alterar tempo operacional de challenge/captura que seja tecnicamente necessário, mas não representar esse tempo com animação intensa.

## 4. Leitura de erros

### Formulário

Após submit inválido:
1. mostrar resumo curto no topo quando houver múltiplos erros;
2. mover foco para resumo ou primeiro campo inválido conforme padrão escolhido;
3. associar mensagem ao campo;
4. preservar valores não sensíveis;
5. não apagar todo formulário.

### Erro técnico

Admin/suporte:

```text
Não foi possível carregar os registros.
Tente novamente.
ID de suporte: abc123 [Copiar]
```

Funcionário:

```text
Não foi possível concluir a marcação.
Tente novamente. Se continuar, chame o responsável.
```

Detalhe técnico não deve vazar para o funcionário.

## 5. Fluxo acessível da câmera

### Antes de abrir

- texto explica que a câmera será usada para identificação;
- botão com nome claro;
- em permissão negada, explicar como permitir sem culpar o usuário.

### Câmera pronta

- preview com label acessível;
- texto `Câmera pronta`;
- instrução “mantenha uma pessoa no enquadramento”.

### Captura

- progresso textual (`Capturando 3 de 6`);
- não exigir acompanhar animação;
- controles bloqueados recebem estado disabled real.

### Processamento

- anunciar `Identificando e registrando…`;
- impedir duplo envio;
- manter foco previsível.

### Resultado

- sucesso/falha vira heading/status claro;
- foco pode ser movido para resultado final quando isso melhorar leitura por tecnologia assistiva;
- CTA de próxima ação vem imediatamente após a mensagem.

## 6. Baixo letramento

A interface deve favorecer:
- verbos diretos: `Registrar ponto`, `Tentar novamente`, `Cadastrar funcionário`;
- frases curtas;
- evitar siglas como RBAC/P95/REP na experiência do funcionário;
- ícone + texto em ações principais;
- uma instrução por etapa na câmera;
- números com unidade (`8,2 s`, `42 s`);
- confirmação nominal para reduzir dúvida sobre quem foi identificado.

Não utilizar voz como requisito do MVP visual; isso pertence a fase futura.

## 7. Login

- labels explícitas;
- autocomplete apropriado;
- erro genérico de credencial para não revelar conta existente;
- estado de rate limit legível e com orientação temporal;
- foco preservado após erro.

## 8. Tabela acessível

Quando DataTable permanecer como tabela:
- `<table>` semântico;
- `<caption>` ou título associado;
- `<th scope>`;
- ordenação com `aria-sort`;
- botões de ação com nome incluindo contexto quando necessário;
- paginação navegável por teclado;
- scroll horizontal com indicação visual e sem aprisionar foco.

## 9. Modal de remoção biométrica

- `role=dialog`/`aria-modal=true`;
- título associado;
- consequência textual;
- foco inicial em `Cancelar`, salvo justificativa de padrão diferente;
- Escape cancela;
- Enter não deve acionar destruição por acidente quando foco não está no botão destrutivo;
- ao fechar, foco retorna à ação originária.

## 10. Critérios por largura para aceite da NF-02

### 360
- sem overflow horizontal da página;
- menu acessível;
- botão primário e camera utilizáveis;
- texto não sobreposto;
- ações com 44 px.

### 768
- sem colisão de filtros/títulos;
- modal/drawer íntegros;
- tabela ou lista mantém hierarquia.

### 1024
- sidebar e conteúdo não competem;
- DataTable legível;
- teclado percorre navegação na ordem visual.

### 1440
- conteúdo não fica excessivamente esticado;
- densidade não sacrifica leitura;
- cards e tabelas alinham ao grid.

## 11. Checklist de revisão Marina

```text
[ ] contraste
[ ] foco visível
[ ] teclado
[ ] labels persistentes
[ ] alvos >= 44x44
[ ] estados não dependem só de cor
[ ] live regions
[ ] reduced motion
[ ] erros legíveis
[ ] câmera acessível
[ ] linguagem simples
[ ] zoom/reflow sem perda funcional
```

## 12. Decisão

```text
RESPONSIVE_SPEC=COMPLETE
ACCESSIBILITY_SPEC=COMPLETE
WIDTHS=360_768_1024_1440
LOW_LITERACY=ADDRESSED
CAMERA_ACCESSIBILITY=DEFINED
```