## 8. Riscos críticos

| ID | Categoria | Risco | Tratamento proposto |
|---|---|---|---|
| RC-01 | Regulatório | Declarar REP-P, homologação ou conformidade sem arquitetura e evidências. | Bloquear alegação comercial; decisão jurídica e técnica na FASE 12. |
| RC-02 | Dados biométricos | Biometria é sensível e irreversível em caso de comprometimento. | Minimização, segregação, criptografia, rotação, acesso e plano de incidente. |
| RC-03 | Legado técnico | A rota viva persiste `Ponto`, enquanto o domínio imutável está em tabelas novas. | Migrar com adaptador e reconciliação antes de workflows/relatórios. |
| RC-04 | Validação | FASE 10.1.1 passou funcionalmente, mas não estatisticamente. | Executar LEA-95/96 antes de homologar ou ampliar piloto. |
| RC-05 | Offline | Fila offline pode permitir adulteração, duplicidade e relógio falso. | Threat model, assinatura/idempotência, conflito explícito e testes de recuperação. |
| RC-06 | Cálculo trabalhista | Escalas, noturno, tolerâncias e banco podem variar por regra e instrumento coletivo. | Motor parametrizado, versões e validação de DP/jurídico. |
| RC-07 | Anexos sensíveis | Atestados podem conter saúde e malware. | Coleta mínima, storage privado, antivírus, ACL e retenção específica. |
| RC-08 | Multitenancy | Falha de escopo expõe dados e faces de outra empresa/obra. | Testes negativos sistemáticos, constraints e revisão de autorização. |
| RC-09 | Assinatura/chaves | Certificados e chaves expiram ou podem ser perdidos. | Inventário, rotação, HSM/segredo, backup e verificação contínua. |
| RC-10 | Operação local | Servidor/câmera/rede locais são ponto único de falha. | Health, contingência manual, restore e estratégia de disponibilidade. |
| RC-11 | Concorrência | Duplo envio e fechamento paralelo podem gerar inconsistência. | Locks/idempotência transacional e testes de corrida. |
| RC-12 | Escopo comercial | Copiar features de concorrentes antes de validar cliente aumenta custo e atraso. | Gate de demanda e cliente piloto para cada integração/diferencial. |

## 9. Decisões humanas pendentes

1. O produto continuará como controle interno da Potiguar ou será vendido a terceiros?
2. O produto pretende ser REP-P, somente coletor de um REP-P, PTRP, ou solução interna não anunciada como conforme?
3. Qual segmento será o primeiro cliente: obras próprias, pequenas construtoras ou empresas gerais?
4. A batida facial será obrigatória, preferencial ou alternativa a PIN/QR?
5. A primeira aplicação móvel será PWA ou nativa?
6. Geofence apenas sinaliza ou bloqueia? Quem autoriza exceção?
7. Worksite representa local físico; será criado centro de custo separado?
8. Quais escalas e instrumentos coletivos entram no primeiro escopo?
9. Qual sistema de folha/ERP é prioridade real?
10. Qual nível de aprovação: gestor único ou gestor+RH?
11. Guardar a melhor imagem do cadastro é necessário ou somente o template?
12. Comprar serviço de antispoof ou desenvolver internamente?
13. Qual SLA, RPO/RTO e contingência manual são aceitáveis?
14. Quais itens do roadmap são aceitos, adiados ou rejeitados? A proposta não é aprovação.

## 10. Dúvidas jurídicas — EXIGE_VALIDAÇÃO_JURÍDICA

1. Qual é a base legal apropriada para cada tratamento biométrico e finalidade no contexto de emprego? Consentimento não deve ser presumido como única opção.
2. É necessário Relatório de Impacto à Proteção de Dados Pessoais para o piloto e para a versão comercial?
3. Qual papel regulatório o CPP exercerá na arquitetura SREP e quais responsabilidades cabem ao desenvolvedor e ao empregador?
4. Há necessidade de registro do programa no INPI para a arquitetura escolhida?
5. Quais campos, NSR, hash, acesso e assinatura devem constar no comprovante por marcação?
6. Quais artefatos o CPP deverá gerar: AFD, AEJ, Espelho, ou apenas consumir/produzir parte deles?
7. Quem assina AFD, AEJ e comprovante PDF, com qual certificado e padrão?
8. Quando o Atestado Técnico e Termo de Responsabilidade é exigido e qual escopo deve cobrir?
9. Quais períodos de retenção se aplicam a eventos, espelhos, logs, templates, imagens, anexos e backups?
10. Como atender eliminação/bloqueio sem descumprir obrigações de conservação e defesa de direitos?
11. Como tratar atestados e outros dados de saúde anexados às justificativas?
12. Quais regras de adicional noturno, intervalos, banco de horas e escalas devem ser parametrizadas para a categoria e instrumentos coletivos?
13. Quais cláusulas são necessárias com fornecedores de nuvem, mensageria, biometria e assinatura?

### Correções normativas mínimas aplicadas nesta análise

- Biometria é dado pessoal sensível; o art. 11 da LGPD contém mais de uma hipótese de tratamento, portanto consentimento não é automaticamente a única base.
- O canal coletor não define sozinho se o sistema é REP-C, REP-A ou REP-P.
- REP-P é software executado em servidor dedicado/nuvem e possui requisitos próprios, incluindo registro de programa no INPI.
- Todos os tipos de SREP devem gerar AFD; REP-A/REP-P o geram prontamente quando solicitado.
- O PTRP trata o AFD e gera Espelho e AEJ.
- Para comprovante PDF emitido por REP-P, o MTE indica PAdES; AFD/AEJ usam CAdES nos casos definidos.
- O PTRP não deve ser chamado de “homologado” sem base; a Q&A oficial esclarece que não necessita homologação em órgão.
- Retenção e eliminação exigem matriz por categoria de dado; o prazo genérico do PDF não foi aceito como fato.

## 11. Funcionalidades que não devem ser implementadas

1. Rastreamento contínuo de rota ou produtividade dentro do produto de ponto.
2. Marcação automática apenas pela aproximação do rosto.
3. Modo anônimo para registro oficial de jornada.
4. WhatsApp/voz/IA como canal primário sem autenticação forte e sem núcleo regulatório concluído.
5. Wearables, IoT e OBD antes de demanda contratada.
6. Controle físico de acesso/catracas no núcleo.
7. Edição ou exclusão de marcação original.
8. Geofence como única prova e bloqueio absoluto sem contingência.
9. Regras trabalhistas hardcoded como universais.
10. Declarações de REP-P, homologação, LGPD ou Portaria 671 antes dos respectivos gates.

## 12. Tabela das 15 funcionalidades mais importantes

| Ordem | ID | Funcionalidade | Estado | Horizonte | Por que é importante |
|---:|---:|---|---|---|---|
| 1 | 34 | Original imutável e correção append-only | PARCIAL | MVP OPERACIONAL | elimina a divisão entre evento real e modelo imutável |
| 2 | 2 | Múltiplos intervalos | PARCIAL | MVP OPERACIONAL | completa a jornada, hoje limitada a entrada/saída |
| 3 | 4 | Sequência e integridade temporal | PARCIAL | MVP OPERACIONAL | protege ordem, relógio e repetição |
| 4 | 42 | Comprovante após cada marcação | NÃO IMPLEMENTADO | MVP OPERACIONAL | dá evidência imediata ao trabalhador |
| 5 | 30 | Solicitação de correção | PARCIAL | MVP OPERACIONAL | substitui edição informal por pedido rastreável |
| 6 | 32 | Aprovação ou recusa pelo gestor | NÃO IMPLEMENTADO | MVP OPERACIONAL | fecha o workflow de correção |
| 7 | 18 | Jornada fixa | PARCIAL | MVP OPERACIONAL | torna cálculo baseado em regra vigente |
| 8 | 23 | Regra intrajornada | PARCIAL | MVP OPERACIONAL | permite calcular pausas e pendências |
| 9 | 25 | Tolerâncias de atraso e saldo | PARCIAL | MVP OPERACIONAL | preserva bruto e aplica política |
| 10 | 26 | Cálculo de horas extras | PARCIAL | MVP OPERACIONAL | é base de RH/folha |
| 11 | 40 | Fechamento mensal | PARCIAL | MVP OPERACIONAL | cria marco mensal controlado |
| 12 | 37 | Espelho e folha de ponto | NÃO IMPLEMENTADO | MVP OPERACIONAL | permite conferência e operação do DP |
| 13 | 71 | Aviso, finalidade e base legal documentada | EXIGE_VALIDAÇÃO_JURÍDICA | MVP OPERACIONAL | governa o tratamento biométrico |
| 14 | 70 | Backup, restauração e recuperação de desastre | PARCIAL | MVP OPERACIONAL | protege continuidade operacional |
| 15 | 54 | Fila local de marcações | NÃO IMPLEMENTADO | V1 COMERCIAL | atende o cenário de obras com rede instável |

## 13. Ordem recomendada de implementação

1. **Backup, restauração e recuperação de desastre** — MVP OPERACIONAL / P0.
2. **Identificação facial na batida** — MVP OPERACIONAL / P0.
3. **Liveness passivo multiquadro** — MVP OPERACIONAL / P0.
4. **Original imutável e correção append-only** — MVP OPERACIONAL / P0.
5. **Múltiplos intervalos** — MVP OPERACIONAL / P0.
6. **Sequência e integridade temporal** — MVP OPERACIONAL / P0.
7. **Comprovante após cada marcação** — MVP OPERACIONAL / P0.
8. **Aviso, finalidade e base legal documentada** — MVP OPERACIONAL / P0.
9. **Definição de arquitetura REP-P/REP-A/REP-C e registro INPI** — MVP OPERACIONAL / P0.
10. **Solicitação de correção** — MVP OPERACIONAL / P0.
11. **Justificativa e anexos** — MVP OPERACIONAL / P0.
12. **Aprovação ou recusa pelo gestor** — MVP OPERACIONAL / P0.
13. **Jornada fixa** — MVP OPERACIONAL / P0.
14. **Regra intrajornada** — MVP OPERACIONAL / P0.
15. **Tolerâncias de atraso e saldo** — MVP OPERACIONAL / P0.
16. **Cálculo de horas extras** — MVP OPERACIONAL / P0.
17. **Detecção de marcação incompleta ou inconsistente** — MVP OPERACIONAL / P0.
18. **Fechamento mensal** — MVP OPERACIONAL / P0.
19. **Espelho e folha de ponto** — MVP OPERACIONAL / P0.
20. **Espelho/comprovante eletrônico assinado** — MVP OPERACIONAL / P0.
21. **Retenção, eliminação, anonimização e bloqueio** — V1 COMERCIAL / P0.
22. **Atendimento a direitos do titular** — V1 COMERCIAL / P1.
23. **Fila local de marcações** — V1 COMERCIAL / P1.
24. **Sincronização, conflito e recuperação** — V1 COMERCIAL / P1.
25. **Captura de GPS no registro** — V1 COMERCIAL / P1.
26. **Cerca virtual e local autorizado** — V1 COMERCIAL / P1.
27. **Centro de custo/projeto separado de obra** — V1 COMERCIAL / P1.
28. **Portal do colaborador e onboarding guiado** — V1 COMERCIAL / P1.
29. **Painel de equipe e pendências** — V1 COMERCIAL / P1.
30. **API pública versionada** — V2 / P2.
31. **Eventos de integração** — V2 / P2.
32. **Conectores folha/ERP** — V2 / P2.
33. **Antispoof avançado contra foto, vídeo e deepfake** — V2 / P2.

A ordem é sequencial por dependência, não por desejo de mercado. Itens já entregues aparecem quando precisam ser validados, migrados ou endurecidos antes de depender deles.
