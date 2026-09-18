# Mission Runtime — Front-end do Controle de Ponto

Este diretório materializa o estado governado da missão **CPP-NF-01-PRODUTO-DESIGN-SYSTEM**.

## Fontes

- `.mcf/project-capsule.yaml` — cápsula do projeto.
- `mission.yaml` — contrato da missão, papéis e autoridade.
- `current.yaml` — estado materializado e próximo passo.
- contrato N1 — define critérios de validação da Fase N.
- `docs/nf-01/evidence/phase-n/` — evidências.

## Regra de continuidade

Um agente que assumir esta missão deve seguir:

```text
ler capsule
→ ler mission.yaml
→ ler current.yaml
→ verificar HEAD/PR/checks ao vivo
→ verificar evidências referenciadas
→ executar próximo passo permitido
→ testar
→ registrar evidência
→ sincronizar current.yaml
→ continuar até Human Gate real
```

## Paralelismo

As frentes A–D podem trabalhar em paralelo somente dentro das autoridades declaradas em `mission.yaml`. Nenhuma frente pode converter evidência automatizada/assistida em aceitação humana, fazer merge, iniciar Fase O ou NF-02 por conta própria.

## VoiceHub

Durante trabalhos longos, o coordenador deve reportar avanços significativos pelo VoiceHub usando a identificação:

```text
Mestre — missão Controle de Ponto
```

Cada atualização deve informar:

1. o que foi concluído;
2. estado atual;
3. próximo passo;
4. se ação humana é necessária.

## Testes

Mudanças no runtime são documentação/estado governado. Elas não substituem testes unitários, integração ou validações existentes do produto. Antes de avançar gate, verificar os workflows do PR #32 e as evidências específicas da fase.

## Human Gate atual

```text
H1_MANUAL_BROWSER_ZOOM_200=WAITING_HUMAN
N3_MANUAL_SCREEN_READER_CRITICAL_JOURNEY=PASS
PHASE_O_START_ALLOWED=NO
NF02_START_ALLOWED=NO
PR_MERGE_AUTHORIZED=NO
```
