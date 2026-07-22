# Priorização — itens 1 a 42

## 4. LEA-129 — Matriz de priorização

Escala de valor: **0 nenhum, 1 baixo, 2 médio, 3 alto**. Colunas: F=funcionário, G=gestor, RH=RH/DP, C=comercial, O=operacional, VC=vantagem competitiva.

| ID | Funcionalidade | F | G | RH | C | O | VC | Total/18 | Esforço | Risco dominante | Dependências-chave | Prioridade |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| 1 | Entrada e saída | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Baixo | Concorrência, relógio, duplicidade | Backend, banco, interface, relógio confiável | **P0** |
| 2 | Múltiplos intervalos | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Erros de sequência, regras coletivas | Modelo de eventos, regras de sequência, UI | **P0** |
| 3 | Bloqueio temporal de duplicidade | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Baixo | Corrida entre requisições, falsos bloqueios | Consulta transacional, índice, regra temporal | **P0** |
| 4 | Sequência e integridade temporal | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Fuso horário, concorrência, relógio do cliente | Domínio de jornada, transações, chave idempotente | **P0** |
| 5 | Identificação facial na batida | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Falso positivo/negativo, viés, iluminação | Câmera, modelo facial, templates, thresholds | **P0** |
| 6 | Cadastro biométrico multiquadro | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Cadastro indevido, baixa qualidade, privacidade | Câmera, análise de qualidade, criptografia, armazenamento privado | **P0** |
| 7 | Detecção de biometria duplicada ou ambígua | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Falso bloqueio, colisão, manutenção do limiar | Busca vetorial, thresholds, escopo por empresa | **P0** |
| 8 | Liveness passivo multiquadro | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Replay em vídeo, iluminação, acessibilidade | Câmera ao vivo, análise de quadros, desafio | **P0** |
| 9 | Antispoof avançado contra foto, vídeo e deepfake | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Muito alto | Custo, latência, viés, fornecedor, falso bloqueio | SDK/serviço externo ou hardware, dataset de ataques | **P2** |
| 10 | Desafio de uso único e proteção contra replay de requisição | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Baixo | Corrida, expiração, indisponibilidade | Banco, hashing, expiração, consumo atômico | **P0** |
| 11 | PIN numérico | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Médio | Compartilhamento de PIN, fraude | Gestão segura de segredo, bloqueio de tentativas, política de contingência | **P2** |
| 12 | QR Code dinâmico | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Médio | Captura de tela, repasse, replay | Emissor, assinatura, expiração, câmera/leitor | **P2** |
| 13 | NFC/RFID | 1 | 1 | 1 | 1 | 1 | 2 | 7 | Alto | Empréstimo de crachá, custo físico | Leitor, driver, gestão de cartões | **P3** |
| 14 | Biometria digital | 1 | 1 | 1 | 1 | 1 | 2 | 7 | Alto | Higiene, falhas em trabalho manual, fornecedor | Hardware, SDK, templates específicos | **P3** |
| 15 | Aplicação web responsiva | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Baixo | Compatibilidade, permissões de câmera | HTTPS, navegador, câmera, UI responsiva | **P0** |
| 16 | Aplicativo móvel nativo ou PWA offline | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Muito alto | Custo de duas plataformas, dados locais, atualizações | Mobile/PWA, sync, segurança do dispositivo | **P2** |
| 17 | Totem ou quiosque compartilhado | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Médio | Fila, sessão residual, disponibilidade física | Modo quiosque, escopo de estação, recuperação de câmera | **P1** |
| 18 | Jornada fixa | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Configuração errada, regras coletivas | Modelo de escala, vínculo com empregado, calendário | **P0** |
| 19 | Jornada flexível e escalas personalizadas/rotativas | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Complexidade, convenções, regressões | Motor de calendário, versionamento de regras | **P1** |
| 20 | Modelos 5x2, 6x1 e 12x36 | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Hardcode legal, convenção coletiva | Motor de escalas, feriados, vigência | **P1** |
| 21 | Feriados, folgas, férias e ausências | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Calendário incorreto, integração RH | Calendário, localidades, tipos de ausência, anexos | **P1** |
| 22 | Troca de turno | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Alto | Conflito de jornada, descanso, abuso | Escalas, workflow, notificações | **P2** |
| 23 | Regra intrajornada | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Interpretação legal, marcações incompletas | Eventos de intervalo, regra por jornada | **P0** |
| 24 | Descanso interjornada | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Médio | Regra legal/coletiva, falsos alertas | Histórico entre dias, regras parametrizadas | **P1** |
| 25 | Tolerâncias de atraso e saldo | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Hardcode, divergência sindical | Motor de cálculo, configuração versionada | **P0** |
| 26 | Cálculo de horas extras | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Erros financeiros, convenções | Jornada, eventos completos, tolerâncias | **P0** |
| 27 | Cálculo noturno parametrizado | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Hardcode jurídico, virada de dia | Timezone, motor temporal, regra coletiva | **P1** |
| 28 | Saldo, compensação e expiração | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Passivo trabalhista, expiração errada | Cálculo diário, razão imutável, políticas, fechamento | **P1** |
| 29 | Detecção de marcação incompleta ou inconsistente | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Falso positivo, volume de pendências | Motor de sequência, agenda, painel | **P0** |
| 30 | Solicitação de correção | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Fraude, edição retroativa, privacidade | Modelo de solicitação, status, UI, autorização | **P0** |
| 31 | Justificativa e anexos | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Dados de saúde, malware, excesso de coleta | Armazenamento privado, antivírus, retenção, ACL | **P0** |
| 32 | Aprovação ou recusa pelo gestor | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Conflito de interesse, atraso, acesso indevido | Workflow, RBAC, notificações, auditoria | **P0** |
| 33 | Múltiplos níveis e aprovação em lote | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Alto | Aprovação indevida em massa | Workflow configurável, segregação de funções | **P2** |
| 34 | Original imutável e correção append-only | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Uso do modelo legado mutável, migração | Modelo append-only, autorização, consulta composta | **P0** |
| 35 | Bloqueio pós-fechamento e reabertura controlada | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Médio | Reabertura abusiva, inconsistência com folha | Closure, RBAC, workflow de reabertura | **P1** |
| 36 | Relatório diário de presença e pendências | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Exposição entre equipes, desempenho | Consultas, autorização, paginação | **P0** |
| 37 | Espelho e folha de ponto | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Erro de cálculo, interpretação legal | PTRP/cálculos, PDF/HTML, acesso do colaborador | **P0** |
| 38 | Relatórios analíticos de horas, atrasos, faltas e localização | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Métrica enganosa, privacidade | Core de cálculo, filtros, exportação | **P1** |
| 39 | Dashboards e relatórios agendados | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Alto | Vazamento por envio, dados desatualizados | Jobs, filas, e-mail, cache | **P2** |
| 40 | Fechamento mensal | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Fechar com pendências, reversão | Eventos completos, cálculo, workflow | **P0** |
| 41 | Exportação para folha de pagamento | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Erro financeiro, layouts variáveis | Fechamento, mapeamento, layouts | **P1** |
| 42 | Comprovante após cada marcação | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Exigência regulatória, acesso, integridade | NSR/identificador, hash, armazenamento, portal | **P0** |
