# NF-01 — Wireframes Conceituais Canônicos

> **Fonte canônica complementar:** `12_NF01_CANONICAL_DECISIONS_2026-08-11.md`.
> Este documento substitui a direção espacial anterior quando houver conflito.

**Natureza:** estrutura e hierarquia, não UI de produção.  
**Regra:** nenhuma funcionalidade futura é apresentada como viva.

---

# 1. Shell administrativo canônico

```text
┌──────────────┬───────────────────────────────────────────────────────┐
│ SIDEBAR  ↔   │ TOP HEADER                                            │
│ compactável  ├───────────────────────────────────────────────────────┤
│              │ BREADCRUMB                                            │
│              │ PAGE HEADER                                           │
│              │                                                       │
│              │                MAIN WORKSPACE                         │
│              │                                                       │
│              │                                                       │
└──────────────┴───────────────────────────────────────────────────────┘
```

Estrutura:

```text
AppShell
├─ CollapsibleSidebar
├─ TopHeader
└─ MainWorkspace
   ├─ Breadcrumb
   ├─ PageHeader
   └─ Conteúdo
```

Regras:

- Dashboard, Funcionários, Empresas/Obras, Registros, Saúde, Eventos/Logs e Configurações compartilham o mesmo shell;
- sidebar expandida/compacta, com largura liberada destinada ao conteúdo;
- `/punch` permanece fora do shell administrativo;
- contexto do header não altera silenciosamente dados do formulário;
- responsividade reorganiza o shell por espaço real.

---

# 2. Dashboard — shell reconciliado

```text
┌───────┬──────────────────────────────────────────────────────────────┐
│ SIDE  │ Controle de Ponto       Visualizando: Potiguar      [Usu]   │
│ BAR ↔ ├──────────────────────────────────────────────────────────────┤
│       │ Dashboard                                                   │
│       │ Visão geral da operação                                    │
│       │                                                             │
│       │ [Funcionários] [Registros hoje] [Biometria pendente]       │
│       │                                                             │
│       │ ┌─────────────────────────┐ ┌─────────────────────────────┐ │
│       │ │ Atividade recente       │ │ Atenção necessária          │ │
│       │ │ dados reais             │ │ somente fontes reais        │ │
│       │ └─────────────────────────┘ └─────────────────────────────┘ │
│       │                                                             │
│       │ [Ver registros]                     [Saúde operacional]     │
└───────┴──────────────────────────────────────────────────────────────┘
```

Regras:

- operação da equipe é protagonista;
- saúde técnica não compete com métricas operacionais principais;
- dado ausente não vira `0` ilustrativo;
- PREDIX/IA não ocupa card principal antes de capacidade real;
- sidebar compacta pode devolver mais largura aos cards/tabelas.

---

# 3. Funcionários — shell reconciliado

```text
┌───────┬──────────────────────────────────────────────────────────────┐
│ SIDE  │ Gestão > Funcionários                         [+ Funcionário]│
│ BAR ↔ │                                                             │
│       │ [ Total ] [ Biometria pendente ] [ outros reais ]          │
│       │                                                             │
│       │ 🔎 Buscar funcionário                      [ Filtros ]       │
│       │                                                             │
│       │ ┌─────────────────────────────────────────────────────────┐ │
│       │ │ Nome │ Matrícula │ Unidade │ Biometria │ Status │ ⋮  │ │
│       │ └─────────────────────────────────────────────────────────┘ │
│       │                                                             │
│       │ 1–20 de 24                          Anterior  1 2  Próxima │
└───────┴──────────────────────────────────────────────────────────────┘
```

Regras:

- busca permanece diretamente acessível;
- filtros frequentes ficam visíveis; secundários podem migrar para popover/drawer quando crescerem;
- ações de biometria respeitam `biometrics:manage`;
- CTA proibido não é mostrado apenas desabilitado;
- mobile não espreme tabela até ilegibilidade: usar resumo/lista + detalhe quando necessário.

Empty:

```text
Nenhum funcionário cadastrado.
[ Cadastrar primeiro funcionário ] ← somente se users:create
```

Error:

```text
Não foi possível carregar os funcionários.
[ Tentar novamente ]
```

`EMPTY != ERROR`.

---

# 4. Novo Funcionário — shell e wizard canônicos

A direção anterior com **stepper vertical + painel direito permanente** foi substituída.

```text
┌───────┬──────────────────────────────────────────────────────────────┐
│ SIDE  │ Funcionários > Novo funcionário               [ℹ Resumo]   │
│ BAR ↔ │                                                             │
│       │ ○   ●   ○   ○   ○   ○   ○   ○        [Ver etapas]         │
│       │                 Etapa 2 de 8                                │
│       │                                                             │
│       │ DADOS PESSOAIS                                              │
│       │ Informe os dados principais do trabalhador.                 │
│       │                                                             │
│       │ Nome completo                         CPF                    │
│       │ [____________________________]       [________________]     │
│       │                                                             │
│       │ Nascimento        Sexo          Raça/cor                    │
│       │ [___________]    [________]    [____________]              │
│       │                                                             │
│       │ Telefone                              E-mail (opcional)      │
│       │ [____________________________]       [________________]     │
│       │                                                             │
│       │ ▼ Informações complementares                               │
│       │                                                             │
│       ├─────────────────────────────────────────────────────────────┤
│       │ Descartar   Salvar e sair              Voltar   Continuar │
└───────┴──────────────────────────────────────────────────────────────┘
```

## 4.1 HorizontalStepper

Visualmente icon-first, semanticamente completo.

```text
[relação] [pessoa] [local] [vínculo] [pagamento] [acesso] [face] [revisão]
    ✓        ✓        !        ●          ○          ○       ○       ○
```

Estados:

```text
✓ COMPLETED
● CURRENT
○ FUTURE
! NEEDS_REVIEW
⚠ ERROR
```

O nome completo da etapa fica no heading do formulário, não permanentemente dentro da barra.

## 4.2 Ver etapas

```text
✓ Tipo de relação
✓ Dados pessoais
! Endereço — revisar
● Vínculo
○ Pagamento
○ Acesso
○ Biometria
○ Revisão
```

Desktop: popover/drawer curto.  
Mobile: sheet/drawer textual sob demanda.

## 4.3 ContextDrawer

```text
[ℹ Resumo]
       ↓
┌──────────────────────────────┐
│ Resumo do cadastro       [X] │
│                              │
│ Nome: Maria Silva            │
│ Relação: CLT comum           │
│ Etapa atual: Vínculo         │
│                              │
│ Contexto                     │
│ Empresa: Potiguar            │
│ Unidade: Galpão              │
│                              │
│ Pendências                   │
│ ! Gestor ainda não definido  │
│ ! Biometria para depois      │
│                              │
│ [Ir para Vínculo]            │
└──────────────────────────────┘
```

- não contém campos obrigatórios editáveis;
- abrir/fechar não perde dados;
- desktop sob demanda;
- tablet/mobile overlay.

## 4.4 StickyFormActions

Etapas 0–6:

```text
Descartar      Salvar e sair                    Voltar   Continuar
```

Etapa 7:

```text
Descartar      Salvar e sair                    Voltar   Concluir cadastro
```

`Concluir cadastro` não existe nas etapas 0–6.

---

# 5. Novo Funcionário — Etapas

## 5.1 Etapa 0 — Tipo de relação

```text
TIPO DE RELAÇÃO

( ) CLT comum
( ) CLT intermitente
( ) Sem vínculo empregatício
( ) Outros [selecionar do catálogo mestre]
```

Alterar uma decisão estrutural posterior pode gerar aviso de impacto e `NEEDS_REVIEW`.

## 5.2 Etapa 1 — Dados pessoais

Usa `ResponsiveFormGrid`, `FormSection` e `FieldGroup`.

```text
DADOS PRINCIPAIS
Nome | CPF
Nascimento | Sexo | Raça/cor
Telefone | E-mail (opcional)

▼ INFORMAÇÕES COMPLEMENTARES
Estado civil (opcional)
Naturalidade (opcional)
Nome social (opcional/condicional)

▼ CONTATO DE EMERGÊNCIA

▼ DEPENDENTES — somente quando aplicável

▼ PcD/REABILITAÇÃO — restrito/condicional
```

## 5.3 Etapa 2 — Endereço

```text
País [Brasil ▼]
Tipo [Urbano | Rural/localidade]

Brasil urbano:
CEP | Logradouro
Número | Complemento (opcional)
Bairro | Cidade | UF
Referência (opcional)
```

CEP pode preencher automaticamente, mas edição manual/fallback permanecem disponíveis.

## 5.4 Etapa 3 — Vínculo

```text
Empresa contratante [EntityPicker]
Matrícula [Gerada na conclusão]
Unidade [EntityPicker]
Setor [EntityPicker]
Cargo/Função [EntityPicker]
Gestor [EntityPicker]
Jornada/Horário [EntityPicker]
```

Campos adicionais variam por relação. Alteração de empresa/unidade/relação recalcula dependências e pode marcar etapas posteriores para revisão.

## 5.5 Etapa 4 — Pagamento

```text
Forma principal
( ) Conta bancária
( ) Conta-salário
( ) PIX
( ) Outra forma configurada
```

Subformulário aparece conforme escolha. Dados ocultos não permanecem ativos no payload final.

## 5.6 Etapa 5 — Acesso

```text
Este funcionário precisa de acesso ao sistema?
( ) Não — padrão
( ) Sim
```

Se Sim:

```text
Perfil [super_admin/admin/manager/operator/auditor]
Escopo [empresa/unidade/equipe quando suportado]
Resumo das permissões efetivas
```

RH não define senha permanente.

## 5.7 Etapa 6 — Biometria

```text
Biometria facial

( ) Cadastrar agora
( ) Configurar depois
```

Se cadastrar agora e tiver permissão:

```text
┌──────────────────────────────┐
│       CÂMERA AO VIVO         │
└──────────────────────────────┘
Câmera pronta
[Iniciar captura]
```

Sem `biometrics:manage`, ação proibida não aparece.

## 5.8 Etapa 7 — Revisão

```text
REVISÃO

Tipo de relação ........... [Editar]
Dados pessoais ............ [Editar]
Endereço .................. [Editar]
Vínculo ................... [Editar]
Pagamento ................. [Editar]
Acesso .................... [Editar]
Biometria ................. [Editar]

[Concluir cadastro]
```

Erros bloqueantes impedem conclusão. Pendências administrativas aparecem explicitamente.

---

# 6. Estados críticos do wizard

## Autosave

```text
Salvando...
Salvo
Alterações ainda não salvas
Falha ao salvar [Tentar novamente]
Sem conexão — alterações ainda não salvas no servidor
```

## Conflito

```text
Este cadastro foi alterado em outro lugar.
Há uma versão mais recente.

[Carregar versão mais recente]
[Revisar antes de continuar]
```

Conclusão bloqueada enquanto conflito persistir.

## Dependência alterada

```text
Esta alteração afetará:
! Vínculo
! Pagamento

Os dados compatíveis serão preservados.
Os demais precisarão ser revisados.

[Cancelar] [Alterar e revisar]
```

## Submit desconhecido

```text
Não foi possível confirmar o resultado do cadastro.
Estamos verificando o que aconteceu.

[Verificar novamente]
```

Nunca mostrar falha definitiva se o resultado ainda for desconhecido.

---

# 7. Responsividade do wizard

## Desktop largo

```text
sidebar compacta/expandida
+ stepper horizontal
+ formulário amplo e limitado para leitura
+ ContextDrawer sob demanda
```

## ~1024

```text
sidebar compacta por padrão
form grid reduz colunas conforme conteúdo
ContextDrawer overlay quando necessário
```

## ~768

```text
sidebar compacta/overlay
stepper reduzido
formulário 1–2 colunas conforme container
ContextDrawer overlay
```

## ~360

```text
menu overlay
Etapa X de 8
progresso simplificado
Ver etapas sob demanda
formulário 1 coluna
sticky actions em modo keyboard-safe
ContextDrawer full/near-full overlay
```

Os valores são alvos de teste, não layout rígido.

---

# 8. Cadastro biométrico dedicado

```text
┌─────────────────────────────────────────────────────┐
│ Funcionários > Pessoa > Biometria                  │
│ Cadastro biométrico facial                         │
│                                                    │
│ [aviso de transparência]                           │
│                                                    │
│ ┌────────────────────────────────────────────────┐ │
│ │                CÂMERA AO VIVO                 │ │
│ └────────────────────────────────────────────────┘ │
│                                                    │
│ Status: Câmera pronta                             │
│ [Iniciar captura]                                 │
└─────────────────────────────────────────────────────┘
```

Estados: aguardando permissão, indisponível, pronta, capturando, validando qualidade, processando, sucesso, falha.

Upload/galeria não pertence ao fluxo normal.

---

# 9. Empresas / Obras

```text
┌───────┬──────────────────────────────────────────────────────────────┐
│ SIDE  │ Gestão > Empresas / Obras                                  │
│ BAR ↔ │                                                             │
│       │ Contexto atual                                              │
│       │ Potiguar Locações • Galpão principal                       │
│       │                                                             │
│       │ [Buscar_________________________]                           │
│       │                                                             │
│       │ Código    Nome                 Estado     Ações             │
│       │ GAL-01    Galpão principal     Ativa      Ver              │
└───────┴──────────────────────────────────────────────────────────────┘
```

Não adicionar mutação inexistente apenas para completar a tela.

---

# 10. Registros

```text
Operação > Registros
[Período] [Unidade] [Tipo] [Buscar funcionário]

Hora  Funcionário  Tipo  Unidade  Status  Detalhe
```

Dados atuais permanecem ligados ao modelo real vigente até fase própria. NF-01 não executa migração `Ponto → AttendanceEvent`.

---

# 11. Saúde operacional

```text
Sistema > Saúde operacional

[API]        [Banco]        [Estação]
Disponível   Disponível     Telemetria indisponível
Fonte real   Fonte real     Sem heartbeat
Recência     Recência       —
```

Cada sinal possui fonte/recência próprias. Sem sinal suficiente, nunca usar verde/healthy.

---

# 12. Eventos / Logs

```text
Sistema > Eventos / Logs
[Período] [Resultado] [Componente] [Request ID]

timestamp | evento | resultado | componente | duração | detalhe
```

NF-01 não cria backend de logs/observabilidade.

---

# 13. Registrar Ponto — shell separado

```text
┌──────────────────────────────────────────────┐
│              CONTROLE DE PONTO               │
│                                              │
│ ┌──────────────────────────────────────────┐ │
│ │              CÂMERA AO VIVO              │ │
│ └──────────────────────────────────────────┘ │
│                                              │
│ O que deseja registrar?                      │
│ [ ENTRADA ]            [ SAÍDA ]             │
│                                              │
│ [ REGISTRAR ENTRADA ]                        │
└──────────────────────────────────────────────┘
```

CTA reflete o tipo selecionado. Resultado final só mostra sucesso após confirmação.

---

# 14. Decisão

```text
WIREFRAMES=RECONCILED_WITH_CANONICAL_UX
APP_SHELL=SHARED
COLLAPSIBLE_SIDEBAR=FROZEN
VERTICAL_ONBOARDING_STEPPER=SUPERSEDED
HORIZONTAL_STEPPER=FROZEN
PERMANENT_CONTEXT_PANEL=SUPERSEDED
CONTEXT_DRAWER=FROZEN
STICKY_FORM_ACTIONS=FROZEN
DASHBOARD_CONTENT=PRESERVED_FOR_RECONCILIATION
EMPLOYEES_CONTENT=PRESERVED_FOR_RECONCILIATION
NEW_EMPLOYEE_FUNCTIONAL_CONTRACT=PRESERVED
PRODUCTION_CODE=UNCHANGED
```
