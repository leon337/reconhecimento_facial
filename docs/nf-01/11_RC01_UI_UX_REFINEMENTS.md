# NF-01 — RC-01 de UI/UX e refinamentos aprovados

**Estado:** `REFINEMENTS_APPLIED_TO_SPEC`  
**Autorização humana:** Leandro concordou com as conclusões da RC e autorizou aplicar os refinamentos.  
**Escopo:** somente documentação/especificação da NF-01; sem código de produção e sem NF-02.

## 1. Problemas encontrados pela RC

1. sidebar inicial excessivamente carregada com roadmap futuro;
2. Dashboard misturava gestão operacional com diagnóstico técnico;
3. pós-cadastro indicava biometria mesmo para `manager`, que não possui `biometrics:manage`;
4. Design System não congelava algumas medidas necessárias para mockups consistentes;
5. Registrar Ponto exigia seleção Entrada/Saída, mas mantinha CTA genérico `Identificar e registrar`;
6. Saúde operacional podia sugerir recência global para sinais com fontes diferentes;
7. formulário de funcionário não agrupava visualmente dados pessoais, vínculo operacional e acesso.

## 2. Refinamentos aplicados

### Arquitetura e navegação

A arquitetura estratégica completa foi preservada, mas a navegação inicial passou a ser operacionalmente reduzida:

```text
Dashboard

OPERAÇÃO
├─ Registros
└─ Registrar Ponto ↗

GESTÃO
├─ Funcionários
└─ Empresas / Obras

SISTEMA
├─ Saúde operacional
└─ Eventos / Logs

Configurações
```

Jornada, Relatórios, PREDIX/Inteligência, Estações e Backup permanecem no roadmap e não ocupam a sidebar inicial por padrão.

### Dashboard

- operação da equipe passa a ser prioridade visual;
- saúde técnica deixa de competir com cards operacionais;
- valores só aparecem quando houver consulta real;
- dado ausente não é representado por `0` ilustrativo;
- PREDIX não ocupa card principal antes de existir capacidade real.

### Funcionário → Biometria

```text
Salvar funcionário
  → sucesso
  → possui biometrics:manage?
      → sim: oferecer Cadastrar biometria agora
      → não: concluir e voltar para funcionários
```

Nenhum CTA proibido é mostrado desabilitado.

### Design System

Foram congelados microtokens de referência para mockups:

```text
sidebar expanded = 248px
sidebar collapsed = 72px
topbar = 64px
input = 44px
button = 44px
CTA kiosk = 56px
table row default = 56px
table row compact = 48px
icons = 16 / 20 / 24px
desktop reference = 1440x1024
mobile reference = 360px
```

Manrope permanece como fonte de referência para a auditoria visual.

### Registrar Ponto

CTA passa a refletir a seleção:

```text
Entrada → Registrar entrada
Saída   → Registrar saída
```

A seleção permanece visível durante processamento e o shell continua separado do admin.

### Saúde operacional

Cada sinal declara:

```text
componente
estado textual
fonte
última atualização própria
impacto quando aplicável
```

Sem heartbeat ou sinal suficiente: `TELEMETRY_UNAVAILABLE`.

## 3. Arquivos atualizados

- `03_INFORMATION_ARCHITECTURE.md`;
- `04_ROLES_PERMISSIONS_AND_STATES.md`;
- `05_DESIGN_SYSTEM.md`;
- `07_WIREFRAMES.md`;
- `11_RC01_UI_UX_REFINEMENTS.md`.

## 4. Itens ainda não executados

```text
FIGMA_FOUNDATION=NEXT
FINAL_SCREEN_MOCKUPS=NOT_STARTED
SCREEN_EXPORTS=NOT_STARTED
VISUAL_AUDIT_LEANDRO=NOT_STARTED
NF01_FINAL_HUMAN_GATE=NOT_READY
NF02=NOT_STARTED
PRODUCTION_CODE=UNCHANGED
```

## 5. Próximo estágio

Criar a fundação visual editável no Figma antes da primeira tela final. A fundação deverá materializar tokens, tipografia, cores, grids, controles, estados e amostras de componentes sem iniciar a NF-02.

Depois da fundação:

```text
Design System visual
→ auditoria
→ Dashboard
→ auditoria
→ demais telas, uma por arquivo
→ auditoria final
→ gate formal NF-01
```

## 6. Decisão

```text
RC01=COMPLETE
RC01_FINDINGS=ACCEPTED_BY_LEANDRO
REFINEMENTS=APPLIED_TO_SPEC
READY_FOR_FIGMA_FOUNDATION=YES
READY_FOR_FINAL_NF01_GATE=NO
```