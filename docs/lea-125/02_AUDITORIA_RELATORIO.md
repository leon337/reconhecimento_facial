## 2. LEA-126 — Auditoria de qualidade do relatório

### Veredito de qualidade

| Dimensão | Avaliação |
|---|---|
| Cobertura de concorrentes | Boa para descoberta inicial |
| Rastreabilidade das fontes | Fraca a média; referências numéricas não formam bibliografia auditável no PDF |
| Separação entre marketing e fato | Fraca |
| Consistência das matrizes | Fraca; há `SIM?`, inferências e duplicidades |
| Fotografia do CPP | Desatualizada e contraditória |
| Matriz legal | Baixa confiabilidade; contém generalizações e confusões conceituais |
| Backlog/roadmap | Útil como brainstorming, não como plano aprovado |

### Correções, dúvidas e classificações explícitas

| ID | Classificação | Local | Achado | Correção/ação |
|---|---|---|---|---|
| A-01 | CONTRADITÓRIO | p.1, 22–23 | O relatório diz que faltam autenticação, criptografia, liveness e controles de acesso avançados. | O repositório comprova sessão administrativa, RBAC, TLS, template cifrado e liveness passivo multiquadro. Corrigir a fotografia do CPP. |
| A-02 | POSSÍVEL ERRO | p.12 | “App móvel = SIM” para o CPP. | Existe acesso pelo navegador do telefone, não aplicativo nativo/PWA offline. Classificação correta: PARCIAL. |
| A-03 | CONTRADITÓRIO | p.12 | “Múltiplos intervalos = PARCIAL”. | O endpoint vivo aceita somente ENTRADA/SAIDA. Há modelo de eventos, mas não fluxo operacional. Manter PARCIAL apenas com essa ressalva. |
| A-04 | NÃO VERIFICADO | p.12, 22, 27 | “Offline = PARCIAL” para o CPP. | Não foi localizado service worker, IndexedDB ou fila local. Tratar como NÃO IMPLEMENTADO até evidência contrária. |
| A-05 | CONTRADITÓRIO | p.13 | “5x2/6x1/12x36 = SIM básico”. | `WorkSchedule` contém minutos e intervalo; não há motor completo desses ciclos. Classificação: PARCIAL. |
| A-06 | POSSÍVEL ERRO | p.13–15 | Obras e centros de custo são tratados como o mesmo recurso. | Worksite está entregue; centro de custo/projeto é entidade diferente e não foi localizada. |
| A-07 | CONTRADITÓRIO | p.14 | “Ponto esquecido/editor”, “solicitação” e “aprovação gestor” aparecem como existentes/futuros misturados. | Há modelo append-only de ajuste, mas não há workflow operacional nem aprovação. Separar modelo, interface e decisão. |
| A-08 | POSSÍVEL ERRO | p.15 | “Importação em massa = SIM” para CPP. | Não foi localizado importador; rota administrativa cria um colaborador por vez. |
| A-09 | POSSÍVEL ERRO | p.15 | “PDF/Excel/CSV = SIM” para CPP. | Não foi localizado gerador/exportador de relatórios. |
| A-10 | CONTRADITÓRIO | p.16–17 | “Rate limiting = NÃO”, enquanto segurança do CPP é tratada como ausente. | Existe rate limiting de login em memória; não existe rate limiting distribuído/API. Classificar PARCIAL e delimitar o escopo. |
| A-11 | CONTRADITÓRIO | p.17, 21–23 | “Exclusão/eliminação = SIM” e “retenção = SIM” para CPP. | Há operações técnicas pontuais e backup, mas não processo LGPD completo nem política validada. Classificação jurídica/operacional: PARCIAL ou EXIGE_VALIDAÇÃO_JURÍDICA. |
| A-12 | ALEGAÇÃO COMERCIAL | p.2–11 | Certificações, “100% aderente”, economia, rapidez, número de clientes e preços. | Registrar como claim do fornecedor até obter documento oficial, escopo do plano e data. |
| A-13 | AVALIAÇÃO DE USUÁRIO | p.2–11 | Notas, reclamações e opiniões de Capterra/App Store/Kickidler. | Amostra, data, plano e contexto não estão documentados; não usar como fato funcional. |
| A-14 | INFERÊNCIA | p.2–11 | Termos como “provavelmente”, “presume-se”, “possivelmente”, “workflow padrão”. | Reclassificar explicitamente como inferência; não preencher matriz com SIM. |
| A-15 | NÃO VERIFICADO | p.2–11 | SSO/AD, API, webhooks, offline, liveness e aprovação multinível em vários concorrentes. | As referências internas não formam bibliografia auditável no PDF. Exigir URL/documento e data por claim. |
| A-16 | CONTRADITÓRIO | p.4–5 | Seção Ahgora usa documentação atribuída à Senior; seção Factorial referencia informação da Genyo para conformidade. | Há contaminação de fonte entre concorrentes. Revalidar cada ficha isoladamente. |
| A-17 | POSSÍVEL ERRO | p.17, 21 | “Todos os concorrentes estão homologados REP-A/P”. | Generalização sem evidência e terminologia inadequada. REP-P requer requisitos próprios e registro de software no INPI; não equivale à homologação de REP-C. |
| A-18 | POSSÍVEL ERRO | p.25 | “Usuários de app = REP-P; totens = REP-C”. | O canal coletor não define sozinho o tipo de REP. Um totem pode ser coletor de um REP-P; REP-C é equipamento convencional específico. |
| A-19 | POSSÍVEL ERRO | p.25 | AFD é tratado como requisito apenas de relógio físico. | A Portaria determina AFD para todos os tipos de SREP, com formas de entrega diferentes. |
| A-20 | POSSÍVEL ERRO | p.21 | AFD/AFD-Web é descrito como exportação para SEFIP/eSocial. | AFD é arquivo fonte do REP; AEJ é produzido pelo programa de tratamento. Não são sinônimos de integração eSocial. |
| A-21 | POSSÍVEL ERRO | p.21, 25–30 | PAdES é alternadamente “obrigatório”, “desejável” e requisito genérico de qualquer espelho. | PAdES é explicitamente indicado ao comprovante PDF do REP-P. Outros documentos/arquivos exigem análise do papel e do padrão aplicável. |
| A-22 | POSSÍVEL ERRO | p.22, 26 | Consentimento é apresentado como única base para biometria. | A LGPD art. 11 prevê consentimento e hipóteses sem consentimento. A base correta depende de finalidade e contexto. |
| A-23 | POSSÍVEL ERRO | p.22, 26 | Eliminação é descrita como direito absoluto após demissão. | Há hipóteses, exceções e obrigações de conservação. O processo precisa decisão jurídica por categoria de dado. |
| A-24 | NÃO VERIFICADO | p.22, 26 | Prazo de cinco anos é atribuído ao art. 15 da Portaria 671. | A referência apresentada não sustenta de forma rastreável a conclusão. Não fixar prazo sem matriz legal atualizada. |
| A-25 | POSSÍVEL ERRO | p.26 | Transparência é classificada como “desejável/tendência”. | Transparência e informação são deveres de governança; o conteúdo e momento exigem validação jurídica. |
| A-26 | POSSÍVEL ERRO | p.19 | Adicional noturno é reduzido a regra fixa 20%/22h–5h e descanso é associado genericamente à NR-1. | Não codificar regra jurídica única; parametrizar e validar CLT, categoria e instrumento coletivo. |
| A-27 | INFERÊNCIA | p.18 | QR “único por usuário por dia” é tratado como padrão. | É decisão de design não sustentada; QR seguro deve considerar expiração curta, assinatura e uso único. |
| A-28 | CONTRADITÓRIO | p.18 e matriz p.12–17 | Liveness é descrito como recurso raro/diferencial, mas várias células são SIM/PARCIAL. | Definir critérios de liveness e separar mera foto, desafio ativo e PAD avançado. |
| A-29 | POSSÍVEL ERRO | p.29 | Marcação automática ao aproximar o rosto é recomendada como diferenciação. | Pode gerar registro involuntário e vigilância contínua; deve ser rejeitada no escopo atual. |
| A-30 | INFERÊNCIA | p.29–30 | Roadmap inicia por PAdES/REP-P e depois trata o núcleo. | O projeto ainda possui dívida da FASE 10.1.1 e não decidiu seu papel regulatório. Primeiro gate deve fechar baseline e decisão jurídica. |

### Regra para as fichas dos concorrentes

- **FATO SUSTENTADO POR FONTE:** somente quando a funcionalidade estiver em documentação oficial identificável, com produto/plano/data.
- **ALEGAÇÃO COMERCIAL:** conformidade total, economia, velocidade, número de clientes, segurança “completa”, preço e diferenciais divulgados pelo fornecedor.
- **AVALIAÇÃO DE USUÁRIO:** reviews e opiniões; registrar amostra, data, plano e contexto.
- **INFERÊNCIA:** qualquer “provavelmente”, “presume-se”, “possivelmente” ou extrapolação de recurso.
- **NÃO VERIFICADO:** a referência não permite rastrear o documento ou confirmar o plano.
- **CONTRADITÓRIO/POSSÍVEL ERRO:** divergência interna, fonte trocada ou conclusão legal sem suporte.
