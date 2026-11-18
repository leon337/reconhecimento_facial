# Checkpoint de continuidade — Potiguar / descoberta operacional (2026-11-04)

> **Natureza:** memória de contexto e handoff de conversa, **não** nova NF, alteração de decisão congelada, evidência de homologação, autorização para uso de biometria ou declaração de conformidade jurídica.
> **Repositório:** `leon337/reconhecimento_facial`
> **Fonte técnica:** `main` consultada em 2026-11-04; baseline do branch deste checkpoint: `2a388fdc40817dca8f7bd96232e723c0e520702b`.
> **Fontes normativas preservadas:** `DECISOES_CONGELADAS.md`, `PROJECT_STATE.md`, `CHECKPOINT.md`; `main` é a fonte do código e a NF-01 em andamento tem seu próprio [PR #32](https://github.com/leon337/reconhecimento_facial/pull/32).

## 1. Contexto de oportunidade (hipóteses, não decisões aprovadas)

- A Potiguar trabalha com projetos de decoração/ornamentação natalina, incluindo Recife e Rio Grande do Norte, e parte da organização histórica de pessoal, compras e materiais ocorre por papel e conversas.
- Há uma conversa exploratória sobre possíveis melhorias operacionais, com responsabilidades e autoridade na empresa ainda indefinidas. **Nenhuma adoção empresarial do ponto facial foi autorizada ou comprovada.**
- O entendimento inicial é **não apresentar nem implantar o reconhecimento facial por padrão**. Primeiro deve-se mapear os problemas reais da empresa e o retorno potencial de cada solução.
- O produto `PredixAI Operations` / Almoxarifado Inteligente é candidato a diagnóstico inicial, **não uma prioridade de roadmap aprovada**. Ver [`leon337/predixai-operations`](https://github.com/leon337/predixai-operations).
- O controle anterior de almoxarifado foi descrito como **parcial**; faltam detalhes do processo real. Não concluir inexistência de controles, perdas, mau desempenho ou irregularidade de qualquer pessoa.

## 2. Estado do projeto facial — separar main e PR ativo

- A `main` documenta a **FASE 12 encerrada**; piloto local avançado, não homologado para produção. Evidência histórica da Fase 12: **143 testes de regressão aprovados**.
- Foram relatadas **20 marcações de ponto confirmadas por operador** (10 notebook e 10 telefone), mas não foi recuperada a série completa dos tempos individuais. **Não** afirmar validação estatística rigorosa ou prontidão em larga escala.
- A **NF-01 (Produto + Design System)** está em andamento no [PR #32](https://github.com/leon337/reconhecimento_facial/pull/32), aberto e não mesclado quando consultado em 2026-11-04. O PR informa trabalho automatizado de UI/UX, com Fase N pendente de evidências manuais.
- Duas validações manuais permanecem bloqueadas no PR #32: **zoom real do navegador em 200%** e **jornada crítica com leitor de tela**. Não converter automação equivalente em `PASS` manual.
- O início da NF-02, merge, homologação de produção, migração `Ponto → AttendanceEvent`, IA operacional e deploy **não estão autorizados neste checkpoint**.
- Biometria, controle trabalhista e LGPD exigem avaliação especializada antes de operação real. Este documento não substitui validação jurídica/regulatória.

## 3. Critério de retomada

1. Confirmar com a empresa os objetivos e a autorização formal para qualquer investigação envolvendo funcionários, jornada, câmeras ou dados pessoais.
2. Fazer diagnóstico operacional antes de escolher solução: custos de administração, critérios de registro de jornada, conectividade em campo, risco de divergências, desempenho no ambiente real e processos existentes.
3. Se o produto facial demonstrar relevância, avaliar requisitos de registro de ponto, privacidade, contingência, segurança e piloto controlado, **sem substituir o ponto oficial** até autorização e conformidade comprovadas.
4. **Continuar a NF-01 no seu próprio fluxo e PR #32**: evidências manuais de acessibilidade e gates vigentes. Não criar NF paralela por causa deste checkpoint.
5. Revalidar GitHub e provedores ao retomar; datas e SHAs acima são snapshots auditáveis, não afirmações permanentes.

## 4. Limites e handoff

```text
CHECKPOINT_ONLY=YES
DECISION_FREEZE=UNCHANGED
NF01_PR32=OPEN_AT_CHECK_2026_11_04
PHASE_N_MANUAL_ZOOM_200=PENDING
PHASE_N_MANUAL_SCREEN_READER=PENDING
NF02_START=NO
PRODUCTION_HOMOLOGATION=NO
COMPANY_PILOT_AUTHORIZATION=NOT_CONFIRMED
LEGAL_COMPLIANCE_DECLARED=NO
BIOMETRIC_DATA_COLLECTION=NO
CODE_CHANGE=NO
DEPLOY=NO
MERGE_AUTHORIZED=NO
NEXT_ACTION=RESUME_NF01_VALIDATION_OR_REASSESS_BUSINESS_NEED_AFTER_DISCOVERY
```

Este arquivo é uma anotação de continuidade em PR documental e não altera as fontes estratégicas, os artefatos da NF-01 nem a classificação do projeto.
