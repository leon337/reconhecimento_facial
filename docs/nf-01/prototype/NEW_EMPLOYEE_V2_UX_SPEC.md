# Novo Funcionário — Desktop V2

## Estado

```text
PHASE=NF01_UX_UI_NEW_EMPLOYEE_V2
FUNCTIONAL_CONTRACT=FROZEN
IMPLEMENTATION_SCOPE=PROTOTYPE_ONLY
PRODUCTION_CODE_CHANGED=NO
BACKEND_CHANGED=NO
NF02_STARTED=NO
MERGE_AUTHORIZED=NO
HUMAN_VISUAL_AUDIT=PENDING
```

Este documento transforma o contrato funcional aprovado do onboarding em uma especificação de UX/UI para o Design Lab da NF-01.

## Princípio do fluxo

O cadastro funciona como uma linha de montagem. Cada etapa trata um domínio, preserva o que já foi preenchido e só entrega o vínculo efetivo depois da revisão final.

```text
0 Tipo de relação
  ↓
1 Dados pessoais
  ↓
2 Endereço
  ↓
3 Vínculo
  ↓
4 Pagamento
  ↓
5 Acesso ao sistema
  ↓
6 Biometria
  ↓
7 Revisão e conclusão
```

## Regras globais do wizard

- uma etapa visível por vez;
- navegação anterior/próxima sem perda de dados;
- rascunho persistente no protótipo via `localStorage`;
- ação explícita `Salvar e sair`;
- validação antes de avançar quando houver campos obrigatórios da etapa;
- etapas concluídas podem ser revisitadas;
- etapas futuras não podem ser puladas por clique;
- em telas estreitas, exibir `Etapa X de 8` e barra de progresso;
- CTA `Concluir cadastro` somente na revisão;
- matrícula somente é representada como “será gerada na conclusão”;
- o protótipo não envia dados para backend;
- dados de exemplo nunca devem ser apresentados como dados reais.

## Estados do onboarding

```text
INITIAL
DRAFT
STEP_VALID
STEP_ERROR
REVIEW
SUBMITTING
SUCCESS
ERROR
UNSAVED_CHANGES
```

## Etapa 0 — Tipo de relação

Opções aprovadas:

- CLT comum;
- CLT intermitente;
- Sem vínculo empregatício;
- Outros, vindo de cadastro mestre do RH.

A escolha dirige campos condicionais nas etapas posteriores. A classificação do software não equivale a conclusão jurídica sobre a relação real.

## Etapa 1 — Dados pessoais

### Identificação

- Nome completo — obrigatório;
- CPF — obrigatório e identificador primário;
- Data de nascimento — obrigatória;
- RG — opcional;
- foto administrativa — opcional e separada da biometria.

### Dados civis

- Sexo — obrigatório;
- Raça/cor (autodeclaração) — obrigatório;
- Grau de instrução — obrigatório;
- Nacionalidade — obrigatória;
- País de nascimento — obrigatório;
- Estado civil — opcional;
- Naturalidade — opcional;
- Nome social — condicional/opcional.

### Contato

- Telefone principal — obrigatório operacionalmente;
- WhatsApp — opcional;
- E-mail pessoal — opcional;
- contato para recados/emergência — pelo menos um obrigatório.

### Complementares

- dependentes — bloco condicional;
- PcD/reabilitação — bloco condicional e restrito;
- trabalhador estrangeiro — campos condicionais;
- anexos — opcionais e com finalidade definida.

### Integridade

- CPF duplicado bloqueia criação de outra pessoa;
- nome + nascimento semelhante gera aviso, não bloqueio;
- readmissão deve reutilizar a pessoa e criar novo vínculo.

## Etapa 2 — Endereço

### Regras

- país primeiro, padrão Brasil;
- endereço brasileiro e estrangeiro suportados;
- Brasil: CEP com busca automática, edição manual e fallback;
- urbano e rural/localidade possuem formulários diferentes;
- um endereço residencial vigente por padrão;
- histórico e data de vigência preservados.

### Brasil urbano

- CEP — obrigatório;
- logradouro — obrigatório;
- número ou Sem número — obrigatório;
- complemento — opcional;
- bairro — obrigatório;
- cidade — obrigatória;
- UF — obrigatória;
- ponto de referência — opcional.

### Brasil rural/localidade

- CEP — opcional quando inexistente;
- localidade/comunidade — obrigatória;
- estrada/rodovia — opcional;
- km — opcional;
- sítio/fazenda/lote — opcional;
- município — obrigatório;
- UF — obrigatória;
- referência — recomendada;
- descrição de acesso — opcional.

## Etapa 3 — Vínculo

### Estrutura

- empresa contratante — cadastro mestre;
- matrícula — automática, somente na confirmação;
- unidade base — cadastro mestre;
- setor/departamento — cadastro mestre;
- cargo/função — cadastro mestre;
- gestor responsável — pode gerar pendência;
- jornada/horário — cadastro mestre com vigência;
- jornada e escala permanecem conceitos separados;
- remuneração contratual fica no vínculo;
- dados bancários ficam na etapa 4;
- benefícios/vale-transporte habitual ficam no vínculo;
- transporte de obra/evento fica fora do onboarding.

### CLT comum

- prazo indeterminado;
- experiência;
- prazo determinado.

### CLT intermitente

- fluxo próprio;
- data de admissão;
- valor/hora;
- jornada/regra própria.

### Sem vínculo

- natureza da relação via cadastro mestre;
- formulário condicional por categoria;
- vigência/histórico;
- linguagem adequada ao tipo de relação.

### Status do vínculo

```text
RASCUNHO
PENDENTE
PROGRAMADO
ATIVO
AFASTADO
ENCERRADO
```

O status é derivado do ciclo de vida, não um simples seletor ativo/inativo.

## Etapa 4 — Pagamento

### Forma principal

- conta bancária;
- conta-salário;
- PIX;
- outra forma configurada pela empresa.

### Conta bancária

- banco via lista pesquisável;
- tipo de conta;
- agência;
- conta;
- dígito.

### Titularidade

- próprio funcionário;
- terceiro, excepcional, com justificativa e revisão do RH.

### PIX

- CPF;
- CNPJ;
- e-mail;
- telefone;
- chave aleatória.

Estados:

```text
INCOMPLETO
PENDENTE_DE_VALIDACAO
VERIFICADO
INCONSISTENTE
INATIVO
```

Comprovante bancário é opcional, restrito e auxiliar.

## Etapa 5 — Acesso ao sistema

Regra padrão:

```text
ESTE_FUNCIONARIO_TEM_ACESSO=NO
```

Se houver acesso:

- conta inicia como convite pendente;
- usuário ativa a própria conta;
- RH não define senha permanente;
- perfil RBAC é escolhido entre os papéis canônicos existentes;
- permissões são exibidas como resumo;
- perfil e escopo são conceitos diferentes;
- escopo pode ser empresa/unidade/equipe;
- mudanças de escopo/perfil devem ser auditáveis.

Perfis canônicos:

```text
super_admin
admin
manager
operator
auditor
```

## Etapa 6 — Biometria

- pode ser cadastrada agora ou depois;
- quem não possui `biometrics:manage` não recebe CTA proibido;
- foto administrativa e biometria são conceitos separados;
- captura normal usa câmera ao vivo;
- multiquadro;
- validação de qualidade;
- upload/galeria fora do fluxo normal;
- frames temporários são descartados após processamento;
- template protegido e versionado;
- aviso de transparência obrigatório antes da captura;
- conflito de unicidade bloqueia conclusão automática;
- conflito biométrico não significa fraude confirmada;
- desligamento inativa o uso, e retenção/eliminação seguem política especializada.

Estados propostos:

```text
NAO_CADASTRADA
PENDENTE
EM_CADASTRO
ATIVA
COM_PROBLEMA
INATIVA
RETIDA
ELIMINADA
```

## Etapa 7 — Revisão e conclusão

A revisão é obrigatória e contém blocos resumidos com `Editar`.

Classificação de problemas:

```text
ERRO_BLOQUEANTE
PENDENCIA_ADMINISTRATIVA
INFORMACAO_OPCIONAL_AUSENTE
```

Somente aqui existe:

```text
[ Concluir cadastro ]
```

A conclusão futura deverá ser transacional e protegida contra duplo envio. No protótipo, a ação apenas demonstra o estado de sucesso.

## Rascunho

O rascunho:

- não gera matrícula;
- não cria vínculo ativo;
- não cria convite de acesso;
- não ativa biometria;
- não aparece como funcionário ativo;
- pode ser retomado;
- pode ser descartado com confirmação.

## Estrutura visual Desktop V2

```text
┌─────────────────────────────────────────────────────────────┐
│ Header / contexto                                           │
├──────────────┬──────────────────────────────────────────────┤
│ Etapas       │ Título da etapa                             │
│ 0 Relação    │ Ajuda contextual                            │
│ 1 Pessoais   │                                              │
│ 2 Endereço   │ Formulário da etapa                         │
│ 3 Vínculo    │                                              │
│ 4 Pagamento  │                                              │
│ 5 Acesso     │                                              │
│ 6 Biometria  │                                              │
│ 7 Revisão    │                                              │
│              │                                              │
│ Rascunho     │ [Salvar e sair] [Voltar] [Continuar]        │
└──────────────┴──────────────────────────────────────────────┘
```

A navegação do produto continua no shell administrativo. O stepper pertence apenas ao fluxo de onboarding.

## Responsividade

### 1440

- sidebar administrativa + stepper lateral + conteúdo amplo.

### 1024

- sidebar administrativa preservada quando houver espaço;
- stepper pode ficar compacto;
- formulário em uma ou duas colunas conforme o grupo.

### 768

- stepper horizontal/compacto;
- formulário prioritariamente em uma coluna;
- CTA inferior continua acessível.

### 360

- `Etapa X de 8`;
- barra de progresso;
- nomes completos das etapas não ficam todos visíveis;
- ações ocupam largura disponível;
- nenhuma dependência de hover.

## Acessibilidade

- labels sempre visíveis;
- `fieldset`/`legend` para escolhas exclusivas;
- erros associados por `aria-describedby`;
- foco movido para o primeiro erro ao tentar avançar;
- stepper informa `aria-current="step"`;
- estados dinâmicos anunciados em região `aria-live`;
- navegação completa por teclado;
- alvos mínimos de 44 px;
- contraste preservado;
- `prefers-reduced-motion` respeitado.

## Estratégia de testes futura

```text
UNITÁRIO
- transições do wizard
- validações por etapa
- serialização/restauração do rascunho
- regras condicionais

INTEGRAÇÃO
- avançar/voltar sem perder dados
- editar seção a partir da revisão
- autosave/retomada
- relação escolhida alterando campos posteriores
- acesso Sim/Não
- biometria agora/depois

VISUAL
- 360 / 768 / 1024 / 1440

ACESSIBILIDADE
- Tab / Shift+Tab
- foco em erro
- ordem de leitura
- `aria-current`
- contraste
```

## Gate

O V2 somente poderá ser classificado como aprovado após auditoria visual humana explícita.
