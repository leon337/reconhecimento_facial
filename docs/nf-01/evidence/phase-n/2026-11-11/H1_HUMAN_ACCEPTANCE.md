# NF-01 — Fase N / H1: aceite humano de evidência técnica

**Data:** 11/11/2026  
**Missão:** `CPP-NF-01-PRODUTO-DESIGN-SYSTEM`  
**PR:** #32; branch `docs/nf-01-produto-design-system`  
**SHA testado:** `f14c4c55e966227fb53799cbf95c4ce5894589ef`  
**Executor:** MESTRE, via acesso remoto autorizado ao notebook `leo-N43SM`.  
**Autoridade do gate:** LEANDRO.

## Decisão explícita

Após receber o relatório de execução, LEANDRO declarou em 11/11/2026:

> MESTRE, aprovo o aceite da evidência técnica do zoom em 200% (H1) e autorizo a reconciliação e revisão final da Fase N da NF-01. Não autorizo merge nem deploy neste momento.

**Precisão de autoria:** LEANDRO **aceitou a evidência técnica**, mas **não afirmou ter operado o navegador nem inspecionado presencialmente** as telas. Não classificar a operação como teste pessoal de LEANDRO. A execução do teste foi do MESTRE, com aceite humano explícito da evidência.

```text
H1_REAL_BROWSER_200_AGENT_EXECUTION=PASS
H1_SCREENSHOT_REVIEW_BY_MESTRE=PASS_IN_INSPECTED_SURFACES
H1_HUMAN_EVIDENCE_ACCEPTANCE=APPROVED_BY_LEANDRO_2026_11_11
H1_PERSONALLY_EXECUTED_BY_LEANDRO=NO
H1_GATE=ACCEPTED_WITH_EXECUTOR_DISTINCTION
N3_REAL_ORCA_HUMAN_DIRECTED=PASS_PREVIOUS_EVIDENCE
PR32_MERGE=NOT_AUTHORIZED
DEPLOY=NOT_AUTHORIZED
NF02_START=NOT_AUTHORIZED
```

## Teste verificável

A branch foi preparada em worktree temporária isolada em `/tmp/mcf-nf01-validation-20261111`. O Design Lab foi servido somente em localhost, no Brave com janela gráfica Xvfb/XFWM4. O zoom foi alterado por teclas nativas `Ctrl++` e medido até `window.devicePixelRatio=2.0`.

A primeira tentativa só atingiu 150% e não foi aceita. Repetições calibradas em 200% concluíram com `H1_AGENT_TECHNICAL_CHECK=PASS`, exit code 0.

| Superfície | DPR | clientWidth | scrollWidth | Overflow horizontal |
|---|---:|---:|---:|---|
| AppShell | 2.0 | 692 | 692 | Não |
| Dashboard | 2.0 | 692 | 692 | Não |
| Funcionários | 2.0 | 692 | 692 | Não |
| Novo Funcionário | 2.0 | 692 | 692 | Não |

Interações: lista das oito etapas abriu; ContextDrawer abriu sem extravasar viewport, fechou e devolveu o foco; ErrorSummary apareceu, permaneceu legível e focado; ações inferiores ficaram alcançáveis. As capturas foram inspecionadas visualmente, sem recortes funcionais nos estados observados.

**Escopo:** protótipo com dados demonstrativos, não produção. Não houve dados pessoais reais, biometria real, alteração de backend ou deploy.

## Artefatos e integridade

Diretório: `docs/nf-01/evidence/phase-n/2026-11-11/`.

- `result.json`: medições e interações; SHA256 `2eb6070749e6586de832b9a6b0025f9fc8c3e2f6e4b14bff64edc3bfe21cb70e`.
- Oito capturas `*.jpg`, com integridade verificada em `SHA256SUMS.txt`.
- `new_employee_error.jpg`: SHA256 `cfd7149573418dd3c0abbd4a52ea046ddd47779b8ca306770eb1eaf0d0dd40ea`.

Comentário original: [PR #32 — evidência](https://github.com/leon337/reconhecimento_facial/pull/32#issuecomment-6795060267).

A evidência N3 já se encontra em `../2026-09-18_N3_REAL_ORCA_HUMAN_DIRECTED_EVIDENCE.md`, uma sessão real do Orca. Não foi repetida agora e não é atribuída ao MESTRE.

**Limite:** aceitar H1 não aprova merge, deploy, fechamento integral da NF-01, NF-02, homologação de produção ou alegação de conformidade jurídica.
