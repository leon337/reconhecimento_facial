# PRF — NF-01 Produto + Design System

Pacote de rastreabilidade Classe C da NF-01.

## Artefatos

- `PHASE-NF01-PLAN.md` — contrato e plano;
- `PHASE-NF01-REPORT.md` — resultado e limites;
- `PHASE-NF01-VALIDATION.txt` — validação resumida;
- `PHASE-NF01-VALIDATION-FULL.txt` — matriz detalhada;
- `PHASE-NF01-SMOKE.txt` — justificativa de não aplicabilidade de smoke do novo design;
- `PHASE-NF01-CHECKPOINT.yaml` — estado da fase;
- `PHASE-NF01-DECISIONS.md` — decisões locais;
- `PHASE-NF01-INDEPENDENT-REVIEW.md` — auditoria independente do conteúdo substantivo;
- `ARTIFACT-MANIFEST.sha256` — manifesto presente com checksums explicitamente pendentes até HEAD congelado.

## Especificação de produto

Ver `docs/nf-01/`.

## Estado

```text
PR=32
INDEPENDENT_REVIEW=COMPLETE_APPROVE_WITH_CONDITIONS
FINAL_CI_HEAD=PENDING
HUMAN_GATE=PENDING_LEANDRO
NF02_STARTED=NO
```

## Regra de fechamento

A existência deste pacote não autoriza NF-02. O fechamento formal depende dos checks do HEAD final e do gate de LEANDRO.
