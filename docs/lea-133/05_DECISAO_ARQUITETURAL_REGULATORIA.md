# LEA-133 — Decisão arquitetural sobre papel do produto e fronteira regulatória

## 1. Decisão de produto

A direção estratégica aprovada prepara o Controle de Ponto Potiguar para evolução comercial e operação multiempresa/multiobra.

```text
CURRENT_OPERATION=LOCAL_CONTROLLED_PILOT
TARGET_PRODUCT=COMMERCIAL_MULTI_COMPANY_TIME_ATTENDANCE_PLATFORM
EXTERNAL_CLIENT_PREPARATION=YES
```

Isso é decisão de produto/arquitetura. Não é classificação jurídica.

## 2. Decisão regulatória segura nesta fase

O projeto não possui base suficiente para declarar, apenas por engenharia, que é REP-P, REP-C, REP-A, PTRP, coletor de REP ou combinação formal dessas categorias.

Consequentemente, a decisão arquitetural vigente é:

```text
CURRENT_REGULATORY_CLAIM=NONE
CURRENT_PUBLIC_CLAIM=NOT_ADVERTISED_AS_LEGALLY_CONFORMANT_REP
REP_P_CLASSIFICATION=VALIDACAO_ESPECIALIZADA_NECESSARIA
PTRP_CLASSIFICATION=VALIDACAO_ESPECIALIZADA_NECESSARIA
COLLECTOR_ROLE=VALIDACAO_ESPECIALIZADA_NECESSARIA
SREP_ARTIFACT_REQUIREMENTS=VALIDACAO_ESPECIALIZADA_NECESSARIA
```

## 3. Arquitetura enquanto a validação não ocorre

O núcleo deve permanecer agnóstico o bastante para suportar a decisão futura sem reescrever o registro essencial de jornada.

Princípios:

1. evento original append-only;
2. timestamp e origem preservados;
3. correções como eventos/ajustes separados;
4. isolamento por empresa/obra;
5. trilha de auditoria;
6. comprovante e artefatos regulatórios como camadas derivadas, não como alteração do evento original;
7. regras trabalhistas configuráveis, não hardcoded por hipótese jurídica;
8. biometria tratada como dado sensível com minimização e controle de acesso.

## 4. Itens que exigem especialista

### Trabalhista/regulatório

- enquadramento SREP;
- papel do software na cadeia REP/PTRP;
- requisitos de comprovante, NSR, hash e assinatura;
- AFD, AEJ, espelho e atestado técnico;
- regras coletivas e exceções de jornada;
- requisitos aplicáveis para comercialização no cenário escolhido.

### Privacidade/proteção de dados

- base legal específica para biometria no contexto laboral;
- transparência e informação ao titular;
- retenção e descarte por categoria de dado;
- compartilhamento/suboperadores;
- avaliação de risco/DPIA quando aplicável;
- direitos do titular e processo de atendimento.

## 5. Decisões proibidas por inferência

```text
ENGINEERING_CAN_DECLARE_PORTARIA_671_COMPLIANT=NO
ENGINEERING_CAN_DECLARE_LGPD_COMPLIANT=NO
AI_CAN_DECLARE_FRAUD=NO
AI_CAN_DECLARE_LEGAL_CONFORMITY=NO
MARKETING_CAN_USE_REP_P_LABEL_WITHOUT_VALIDATION=NO
```

## 6. Gate para futura classificação

Antes de adotar qualquer rótulo regulatório:

```text
arquitetura alvo definida
  -> requisitos legais aplicáveis mapeados
  -> especialista trabalhista revisa
  -> especialista privacidade revisa biometria
  -> gaps técnicos viram tarefas rastreáveis
  -> testes/evidências executados
  -> revisão independente
  -> gate humano
  -> somente então comunicação comercial
```

## 7. Resultado desta ressalva

```text
COMMERCIAL_DIRECTION=DECIDED
CURRENT_REGULATORY_ROLE=NO_CLAIM
REGULATORY_ITEMS_SEPARATED_FROM_ENGINEERING=YES
LEGAL_VALIDATION=REQUIRED
LEGAL_CONFORMITY_DECLARED=NO
```

A ressalva é resolvida no nível correto: não por inventar conformidade, mas por fixar a fronteira de autoridade e impedir que uma hipótese regulatória contamine a arquitetura ou a comunicação do produto.