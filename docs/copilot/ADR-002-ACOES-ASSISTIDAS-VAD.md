# ADR-002 — Cadastro assistido e VAD modular do Copiloto Potiguar

**Situação:** implementação incremental em branch isolada; não presume deploy.

## Problema e MVP

O copiloto atual só orienta. O objetivo é permitir **criar um funcionário** a partir de pedido por voz ou texto, mas **nunca** executar uma ação só por ordem do modelo. O áudio ambiente também gera falsos turnos.

MVP: Gemini Live interpreta o pedido e chama exclusivamente `prepare_employee_registration`, função **sem efeitos no banco**. A UI exibe os campos para revisão, permite edição e pede clique humano em **Confirmar e cadastrar**. Um endpoint próprio revalida CSRF/RBAC, normalização, limites, escopo organizacional, duplicidades e auditoria antes de criar `Employee` + `User`. O servidor gera uma senha inicial aleatória, devolvida ao administrador **uma única vez**, sem apresentá-la ao Gemini ou incluí-la na transcrição. O fluxo biométrico continua manual, sem gravação de jornada e sem ferramentas de ponto.

## Requisitos e riscos

- `USERS_CREATE` necessário tanto para oferecer a ferramenta no front quanto para gravar; auditor sem permissão não pode criar.
- Modelo pode inventar campos: tudo fica editável e exige confirmação explícita em UI. Nenhum texto ou ferramenta recebido do Google é tratado como autorização.
- Credenciais, CPF, imagens biométricas, senhas e batidas de ponto não vão ao modelo. Nomes e dados funcionais **podem ser processados pelo Gemini** quando o usuário os fala: exibir consentimento e usar dados fictícios na homologação. Uma revisão de LGPD é necessária antes de dados reais.
- Senha sempre gerada pelo backend; conta nova com papel `operator` por padrão, nunca admin.
- A operação deve ser resistente a duplo clique, violação de scope, payload extra e username repetido.
- Sem botão de confirmação nenhuma escrita deve ocorrer no domínio.
- Feature flag `POTIGUAR_COPILOT_ACTIONS_ENABLED` desligada por padrão; só liberar na HML governada.
- Auditoria separada `copilot.employee.create`.

## VAD

Camada 1: `getUserMedia` com echo cancellation e noise suppression. Camada 2: `vad.js` local e modular, com classificação heurística baseada em RMS relativo, cruzamentos por zero e periodicidade (não é classificador neural); buffer de pré-fala, duração mínima para ativar, histerese e encerramento de silêncio. Não envia o ruído rejeitado à API e **não grava áudio**. Camada 3: VAD da Live API em sensibilidade LOW e limiares conservadores; sinalizar `audioStreamEnd` quando o gate local encerra o turno. Alternativa manual de apertar/parar microfone disponível para ambientes difíceis.

Limite conhecido: VAD por energia/peridiocidade não consegue distinguir toda fala distante ou música de comando legítimo. Para implantação comercial, calibrar no Android real, comparar com modelo neural WebRTC/Silero local (se houver código aprovado do assistente R) e avaliar falsos positivos/negativos, latência e privacidade. **Até localizar o repositório/código do assistente R, não declarar reutilização.**

## Futuro

Múltiplas ações e ferramentas com grants específicos, deduplicação persistente de requisições via tabela de idempotência, normalização de matrícula por empresa, alternativa offline de OCR não sensível, observabilidade de VAD agregada sem áudio, e revisão legal/biométrica.

## Evidência

Documentar testes de servidor Flask/RBAC/CSRF/escopo/duplicidade, testes JS sem microfone de usuários reais, E2E sintético de função Gemini Live, validação visual móvel, integração isolada; GitHub e deploy são gates separados.
