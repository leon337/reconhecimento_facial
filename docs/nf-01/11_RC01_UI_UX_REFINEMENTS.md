# NF-01 — RC-01 de UI/UX — Registro Histórico

**Estado:** `HISTORICAL__SUPERSEDED_WHERE_CONFLICTING`  
**Escopo original:** documentação/especificação da NF-01.  
**Produção:** não alterada.

> A RC-01 permanece registrada para preservar a evolução das decisões, porém a direção atual de UX/UI foi aprofundada em 11/08/2026.
>
> **Fonte canônica atual:** `12_NF01_CANONICAL_DECISIONS_2026-08-11.md`.
>
> Em caso de conflito, usar o registro canônico atual, sempre subordinado a `DECISOES_CONGELADAS.md`.

## 1. Achados históricos da RC-01

A RC-01 identificou:

1. sidebar inicial excessivamente carregada com roadmap futuro;
2. Dashboard misturando gestão operacional e diagnóstico técnico;
3. pós-cadastro sugerindo biometria para usuário sem `biometrics:manage`;
4. necessidade de uma fundação de Design System mais consistente;
5. CTA de Registrar Ponto genérico apesar da escolha Entrada/Saída;
6. Saúde operacional precisando declarar fonte e recência por sinal;
7. formulário de funcionário precisando de agrupamento e melhor hierarquia.

## 2. Decisões históricas preservadas

### Navegação operacional reduzida

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

Essa redução continua válida como direção inicial da sidebar, sujeita ao `CollapsibleSidebar` canônico atual.

### Dashboard

- operação da equipe como prioridade;
- saúde técnica separada da operação principal;
- números apenas com fonte real;
- dado ausente não vira `0` ilustrativo;
- IA/PREDIX não ocupa card principal antes de existir capacidade real.

Essas decisões continuam válidas.

### Funcionário → Biometria

```text
Salvar/concluir funcionário
  → usuário possui biometrics:manage?
      → sim: oferecer fluxo biométrico quando permitido pelo onboarding
      → não: não renderizar CTA proibido
```

A regra permanece válida, mas o onboarding atual é um wizard de oito etapas com biometria própria na Etapa 6.

### Registrar Ponto

```text
Entrada → Registrar entrada
Saída   → Registrar saída
```

O shell de `/punch` continua separado do admin.

### Saúde operacional

Cada sinal continua declarando:

```text
componente
estado textual
fonte
ultima atualizacao propria
impacto quando aplicavel
```

Sem sinal suficiente: `TELEMETRY_UNAVAILABLE`.

## 3. Decisões da RC-01 substituídas pelo ciclo 11/08/2026

```text
microtokens rigidamente congelados em px........ SUPERSEDED
sidebar fixed dimensions as global rule......... SUPERSEDED
icon library ainda indefinida................... SUPERSEDED → Lucide
stepper/painel lateral anteriores................ SUPERSEDED
Figma como próximo passo obrigatório imediato... SUPERSEDED pela sequência atual de reconciliação documental/Design Lab
```

A política atual usa `rem`, `fr`, `minmax`, `clamp`, unidades de viewport limitadas e container queries, conforme `05_DESIGN_SYSTEM.md`.

## 4. Continuidade correta

Não continuar o projeto a partir deste arquivo isoladamente.

Antes de qualquer proposta de UX/UI, ler:

```text
DECISOES_CONGELADAS.md
12_NF01_CANONICAL_DECISIONS_2026-08-11.md
05_DESIGN_SYSTEM.md
06_COMPONENT_CATALOG.md
07_WIREFRAMES.md
08_RESPONSIVE_ACCESSIBILITY.md
09_TEST_AND_ACCEPTANCE_STRATEGY.md
```

## 5. Estado

```text
RC01=HISTORICAL_COMPLETE
CURRENT_CANONICAL_RC=12_NF01_CANONICAL_DECISIONS_2026-08-11.md
PRODUCTION_CODE=UNCHANGED
NF02=NOT_STARTED
FINAL_HUMAN_GATE=NOT_READY
```
