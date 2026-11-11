# Copiloto Potiguar — evidências do cadastro assistido e VAD

**Data:** 2026-11-11. **Escopo:** MVP isolado, sem dados de funcionários reais.

## Cenário de negócio

Usuário com `USERS_CREATE` pede ao Gemini 3.8 Live: "Cadastre Maria de Teste, usuário maria.teste, matrícula TEST-101". O modelo chama a ferramenta `prepare_employee_registration` e devolve **somente um rascunho**. A UI oferece campos editáveis. Após o clique humano de confirmação, `POST /admin/copilot/employee-create` revalida credenciais de sessão, CSRF, RBAC, escopo empresa/obra, unicidade, limites de tamanho e auditoria, e cria somente `Employee` + `User`, com papel operador. A senha é gerada aleatoriamente no servidor, devolvida uma vez ao administrador e nunca compartilhada com o Gemini.

## Evidência técnica

- Teste Google real, modelo `gemini-3.8-live`, usando chave privada já provisionada no cofre, token efêmero de uso único e apenas dados sintéticos: **conexão OK, functionCall `prepare_employee_registration` OK, rascunho estruturado OK, sem chamada de gravação**.
- `gemini-3.8-live-extended-thinking`: conectou, mas **não emitiu a chamada de função** no cenário sintético e atingiu timeout. Por isso a criação assistida por conversa foi restrita ao modelo Live padrão; Extended pode continuar orientando.
- Testes Node do VAD (RMS relativo, periodicidade, cruzamento por zero, pré-fala, duração mínima, histerese) rejeitaram ruído branco baixo/alto, silêncio e pulsos muito curtos; reconheceram fala senoidal sintética.
- Processamento de gravação **sintética de voz** já gerada pelo Gemini: 34 blocos PCM, 1 início e 1 fim de fala, 32 blocos transmitidos. Nenhum dado pessoal foi usado.
- Camada Google Live configurada com sensibilidade de início/fim LOW, prefixo 220 ms e silêncio 750 ms; áudio em silêncio sem fala local não é transmitido.
- Alternativa de microfone manual visível na UI.
- Testes backend: usuário auditor sem `USERS_CREATE` bloqueado, feature off nega gravação, duplicidade bloqueada, auditoria criada, usuário recebe papel operador, senha aleatória não enviada ao Gemini, campos extra/role/company_id rejeitados, escopo organizacional do gestor preservado e dados reais proibidos na HML.
- Fluxo completo Python executado em contêiner com banco e credenciais sintéticas. **O microfone real em celular e ruídos locais ainda precisam de validação humana; não afirmar que o ruído está 100% eliminado.**

## Limites e governança

- `POTIGUAR_COPILOT_ACTIONS_ENABLED=0` por padrão. Habilitar **somente** em homologação com conta fictícia, quota de uso e mecanismo de rollback.
- Homologação pública aceita apenas nomes de teste, usernames terminados em `.teste` ou iniciados em `teste.`, e matrícula `TEST-`. No máximo 5 cadastros fictícios por dia, atrelado ao mecanismo de cota SQLite.
- Não cria biometria, ponto, escala, folha de pagamento nem credenciais administrativas.
- O VAD é heurístico local, não equivalente à identificação de voz humana. Pode falhar com música, fala distante, microfone ruim ou ruído tonal. A solução anterior do assistente **R** não foi identificada em repositório ou módulo verificável desta sessão e **não está sendo descrita como reutilizada**.
- A chave Gemini não entra no repositório, build ou logs. A confirmação depende do login e de um clique humano na UI.
- Para uso oficial de ponto, ainda são necessárias as etapas de homologação legal/LGPD, backup/restore PostgreSQL, infraestrutura durável e validação presencial de acessibilidade.
