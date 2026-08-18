# PHASE-NF01 — PLAN

```yaml
mission: CPP-NF-01-PRODUTO-DESIGN-SYSTEM
nf: NF-01
mode: MCF_CANONICO
protocol: 1.1
risk_class: C
base_main_sha: 2a388fdc40817dca8f7bd96232e723c0e520702b
branch: docs/nf-01-produto-design-system
authority_human_final: LEANDRO
production_code: prohibited
nf02: prohibited
```

## Objetivo

Converter as decisões congeladas em especificação implementável de produto e Design System sem alterar código de produção.

## Fontes obrigatórias

- `DECISOES_CONGELADAS.md`;
- `ROADMAP_CURRENT.md`;
- `PROJECT_STATE.md`;
- `CHECKPOINT.md`;
- `docs/mcf/PRF_CPP_COMMERCIAL_REDESIGN_AI_OBS_001.md`;
- entregáveis `docs/lea-133/`;
- entregáveis `docs/lea-125/`;
- código/templates/JS atuais;
- MCF oficial `main`.

## Agentes selecionados com entrega concreta

| Agente | Entrega |
|---|---|
| Mestre | contrato, coordenação e gate |
| Miriam | reconciliação de fontes e estado real |
| Leonardo | definição de produto |
| Evelyn | estratégia de experiência |
| Laura | arquitetura da informação e fluxos |
| Isabela | Design System e componentes |
| Marina | acessibilidade |
| Sofia | coerência arquitetural e invariantes |
| Renato | critérios/testes futuros |
| Carmem | documentação final |
| Augusto | ESEV/rastreabilidade Classe C |
| Emily | auditoria independente |
| Júlia | limites de privacidade/IA/decisão sensível |
| Gabriel | rastreabilidade branch/commit/PR |
| Léo | gate delegado apenas quando compatível com autoridade humana final |

Convocação não significa atividade autônoma. As contribuições acima correspondem a seções e verificações realmente materializadas nos artefatos.

## Entregáveis

1. `docs/nf-01/01_PRODUCT_DEFINITION.md`
2. `docs/nf-01/02_UI_INVENTORY.md`
3. `docs/nf-01/03_INFORMATION_ARCHITECTURE.md`
4. `docs/nf-01/04_ROLES_PERMISSIONS_AND_STATES.md`
5. `docs/nf-01/05_DESIGN_SYSTEM.md`
6. `docs/nf-01/06_COMPONENT_CATALOG.md`
7. `docs/nf-01/07_WIREFRAMES.md`
8. `docs/nf-01/08_RESPONSIVE_ACCESSIBILITY.md`
9. `docs/nf-01/09_TEST_AND_ACCEPTANCE_STRATEGY.md`
10. `docs/nf-01/10_NF01_CLOSEOUT.md`

## Gates

```text
G0_SOURCE_RECOVERY
G1_SPEC_COMPLETENESS
G2_INDEPENDENT_REVIEW
G3_CI_AND_DIFF
G4_HUMAN_CLOSEOUT_LEANDRO
```

G4 não pode ser presumido.

## Restrições

```text
PRODUCTION_CODE_CHANGED=NO
DECISOES_CONGELADAS_CHANGED=NO
PONTO_MIGRATION=NO
AI_IMPLEMENTED=NO
OBS_BACKEND_IMPLEMENTED=NO
DEPLOY=NO
PRODUCTION_HOMOLOGATION=NO
NF02_STARTED=NO
```
