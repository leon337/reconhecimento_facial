# NF-01 — Revisão individual B4 Tabs

**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**Branch:** `docs/nf-01-produto-design-system`  
**PR:** #32  
**Componente:** `B4 — Tabs`  
**Gate humano:** LEANDRO  
**Data:** 2026-08-17  

## Resultado

```text
B4_TABS=FROZEN_INDIVIDUALLY
HUMAN_GATE=APPROVED_BY_LEANDRO
PHASE_B_COMPONENT_REVIEW=COMPLETE
NEXT_OFFICIAL_ITEM=C1_STATUS_BADGE_COMPONENT_REVIEW
IMPLEMENTATION=NO
PRODUCTION_CHANGE=NO
NF02=NOT_STARTED
```

## Contrato congelado

```text
B4_TABS

mesmo contexto / visões irmãs........ ✅
usar como wizard...................... ❌
usar como navegação principal......... ❌

texto visível nas tabs................ ✅ padrão
ícone + texto.......................... ✅
ícone sozinho.......................... ❌ normalmente

active multissinal..................... ✅
depender só de cor..................... ❌

Tab entra no grupo..................... ✅
Arrow navega........................... ✅
Home / End............................. ✅
Tab segue para painel.................. ✅

ativação automática................... ✅ conteúdo imediato
ativação manual........................ ✅ conteúdo pesado/remoto

estado restaurável/navegável........... ✅ quando relevante
URL exata.............................. ⏳ implementação

loading pertence ao painel............. ✅
erro pertence ao painel................ ✅

RBAC remove opção proibida............. ✅
tab proibida apenas disabled........... ❌

poucas tabs em mobile.................. ✅ horizontal
overflow controlado.................... ✅ quando necessário
esmagar tipografia..................... ❌
dropdown automático no mobile.......... ❌

contadores/badges...................... ✅ quando úteis
badge sem nome acessível................ ❌
```

## Decisões detalhadas

- Tabs representam visões irmãs do mesmo contexto.
- Tabs não substituem `HorizontalStepper`, wizard ou navegação principal.
- O rótulo textual é padrão; ícone sozinho não é padrão.
- O estado ativo deve combinar mais de um sinal visual e `aria-selected`.
- Teclado: `Tab` entra/sai do conjunto; setas navegam; `Home` e `End` são suportados.
- Ativação automática é aceitável quando o conteúdo é local/imediato; manual é preferível quando a troca dispara conteúdo remoto/pesado.
- Estado da aba deve ser restaurável/navegável quando relevante; a estratégia exata de URL pertence à implementação futura.
- Loading e erro pertencem ao `TabPanel`, não à tab.
- RBAC deve ocultar opções proibidas em vez de simplesmente exibi-las desabilitadas.
- Em mobile, poucas tabs permanecem horizontais; overflow horizontal controlado pode ser usado quando necessário.
- Não transformar automaticamente tabs em dropdown em mobile.
- Badges/contadores podem existir quando úteis, com nome acessível.

## Testes futuros obrigatórios

```text
UNITARIOS
- tab ativa
- mudança de seleção
- disabled quando aplicável
- Home / End
- Arrow Left / Right
- associação tab ↔ painel

INTEGRACAO
- Tabs + URL/estado
- Tabs + RBAC
- Tabs + painel assíncrono
- Tabs + ErrorState
- Tabs + contador

RESPONSIVO
- 360
- 768
- 1024
- 1440+
- overflow horizontal quando autorizado

ACESSIBILIDADE
- teclado
- screen reader
- focus-visible
- aria-selected
- aria-controls
- ordem de foco
- zoom 200%
```

## Guardrails preservados

```text
DO_NOT_START_NF02
DO_NOT_CHANGE_PRODUCTION_CODE
DO_NOT_CHANGE_BACKEND
DO_NOT_MERGE_WITHOUT_EXPLICIT_LEANDRO_APPROVAL
```

Com esta aprovação, a Fase B — Ações, navegação local e ajuda — está conceitualmente encerrada. O próximo item oficial é `C1 — StatusBadge`.
