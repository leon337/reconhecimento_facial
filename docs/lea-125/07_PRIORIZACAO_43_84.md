# Priorização — itens 43 a 84

## 4. LEA-129 — Matriz de priorização

Escala de valor: **0 nenhum, 1 baixo, 2 médio, 3 alto**. Colunas: F=funcionário, G=gestor, RH=RH/DP, C=comercial, O=operacional, VC=vantagem competitiva.

| ID | Funcionalidade | F | G | RH | C | O | VC | Total/18 | Esforço | Risco dominante | Dependências-chave | Prioridade |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| 43 | Espelho/comprovante eletrônico assinado | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Custo, expiração, aplicação jurídica errada | Certificado, HSM/segredo, PAdES/CAdES, política | **P0** |
| 44 | Cadastro de colaborador e conta | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Baixo | Dados incorretos, privilégio | Employee/User, validações, senha | **P0** |
| 45 | Departamentos, cargos e equipes | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Médio | Hierarquia incorreta, acesso transversal | Modelos organizacionais, vínculos temporais | **P1** |
| 46 | Papéis e permissões RBAC | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Escalada de privilégio, permissões insuficientes | Autenticação, decorators, matriz de permissão | **P0** |
| 47 | Importação em massa | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Médio | Planilha malformada, duplicidade, PII | Parser, validação, preview, rollback | **P2** |
| 48 | Desligamento e transferência | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Médio | Perda de acesso/histórico, conflito de tenant | Vigência, escopo, autorização | **P1** |
| 49 | Multiempresa isolada | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Vazamento multitenant | Tenant scope, consultas, constraints | **P0** |
| 50 | Obras/unidades e estação escopada | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Configuração errada, estação fora de escopo | Worksite, código de estação, RBAC | **P0** |
| 51 | Centro de custo/projeto separado de obra | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Mistura local/custo, retroatividade | Modelo próprio, vigência, relatório | **P1** |
| 52 | Dispositivo autorizado | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Alto | Troca de aparelho, fingerprint invasivo | Device binding, chaves, inventário | **P2** |
| 53 | Gestão de estação compartilhada | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Sequestro de estação, indisponibilidade | Inventário, token de estação, observabilidade | **P1** |
| 54 | Fila local de marcações | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Muito alto | Adulteração local, perda, duplicidade | PWA/app, armazenamento cifrado, relógio, idempotência | **P1** |
| 55 | Sincronização, conflito e recuperação | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Muito alto | Corrida, relógio divergente, fechamento já feito | Idempotency key, versionamento, resolução de conflitos | **P1** |
| 56 | Captura de GPS no registro | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Médio | Privacidade, precisão, spoofing | Permissão do dispositivo, schema, minimização | **P1** |
| 57 | Cerca virtual e local autorizado | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Falso bloqueio, privacidade, GPS ruim | Geometria, locais, tolerância, modo offline | **P1** |
| 58 | Detecção de localização falsa | 1 | 1 | 1 | 1 | 1 | 2 | 7 | Muito alto | Evasão, falso positivo, dependência móvel | Sinais do SO, attestation, análise de risco | **P3** |
| 59 | API pública versionada | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Alto | Abuso, quebra de contrato, vazamento | Autenticação, versionamento, rate limit, docs | **P2** |
| 60 | Eventos de integração | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Alto | Duplicidade, destino indisponível, PII | Fila, assinatura HMAC, retry, DLQ | **P2** |
| 61 | Conectores folha/ERP | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Muito alto | Manutenção, versões, suporte | API/exportador, mapeamento por fornecedor | **P2** |
| 62 | AFD, AEJ e formatos oficiais | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Muito alto | Autuação, formato errado, papel incorreto | Arquitetura REP/PTRP, NSR, assinatura, leiautes | **P0** |
| 63 | SSO/Active Directory | 1 | 1 | 1 | 1 | 1 | 2 | 7 | Alto | Lockout, mapeamento de papéis | OIDC/SAML, provisionamento, RBAC | **P3** |
| 64 | E-mail, push e WhatsApp para confirmação e pendências | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Médio | Vazamento, spam, custo | Provedor, preferências, templates, fila | **P1** |
| 65 | Integração com REP/hardware externo | 1 | 1 | 1 | 1 | 1 | 2 | 7 | Muito alto | Vendor lock-in, certificação, suporte físico | SDK/protocolo, AFD, suporte por modelo | **P3** |
| 66 | TLS, sessão, CSRF e hardening HTTP | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Configuração, certificado local | Caddy, cookies, headers, CSRF | **P0** |
| 67 | Segregação e criptografia biométrica | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Perda de chave, legado em texto, rotação | Fernet/chave externa, storage privado | **P0** |
| 68 | Trilha de auditoria e logs estruturados | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Médio | Excesso de dados, ausência de alerta | Modelo append-only, retenção, consulta | **P0** |
| 69 | MFA, rate limiting compartilhado e monitoramento | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Lockout, custo, falso positivo | IdP/MFA, Redis/WAF/SIEM, alertas | **P1** |
| 70 | Backup, restauração e recuperação de desastre | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Backup não restaurável, chave ausente | PostgreSQL, storage, cópia externa, runbook | **P0** |
| 71 | Aviso, finalidade e base legal documentada | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Alto | Base inadequada, consentimento inválido | Inventário de dados, jurídico, UX, registro de versão | **P0** |
| 72 | Retenção, eliminação, anonimização e bloqueio | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Muito alto | Conflito com obrigação trabalhista, irreversibilidade | Política, jobs, legal hold, backup | **P0** |
| 73 | Atendimento a direitos do titular | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Entregar dado a terceiro, prazo, exceções | Canal, identidade, workflow, exportação | **P1** |
| 74 | Definição de arquitetura REP-P/REP-A/REP-C e registro INPI | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Muito alto | Declaração indevida de conformidade | Especialista trabalhista, arquitetura, INPI quando aplicável | **P0** |
| 75 | PTRP, espelho e cadeia de tratamento | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Muito alto | Mistura de REP e PTRP, perda de rastreio | Core de eventos, ajustes, fechamento, leiautes | **P0** |
| 76 | Assinaturas PAdES/CAdES e Atestado Técnico | 3 | 3 | 3 | 2 | 3 | 2 | 16 | Muito alto | Assinar objeto errado, expiração, responsabilidade | Certificado ICP-Brasil quando exigido, gestão de chaves, documentação | **P0** |
| 77 | Portal do colaborador e onboarding guiado | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Exposição de dados, abandono | Autenticação de colaborador, UX, relatórios | **P1** |
| 78 | Painel de equipe e pendências | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Alto | Sobrecarga, vazamento entre equipes | Relatórios, workflow, RBAC | **P1** |
| 79 | Acessibilidade, baixa letramento e baixo consumo de dados | 2 | 3 | 3 | 3 | 3 | 2 | 16 | Médio | Exclusão digital, voz expondo dados | Design system, testes assistivos, compressão | **P1** |
| 80 | Marcação por WhatsApp, voz ou IA | 0 | 1 | 0 | 0 | 0 | 0 | 1 | Muito alto | Impersonação, replay, custo, privacidade | Provedor, identidade forte, GPS, auditoria | **R** |
| 81 | Rastreamento de rota e monitoramento de produtividade | 0 | 1 | 0 | 0 | 0 | 0 | 1 | Muito alto | Vigilância excessiva, LGPD, clima laboral | GPS contínuo, analytics, política | **R** |
| 82 | Wearables, IoT e OBD veicular | 0 | 1 | 0 | 0 | 0 | 0 | 1 | Muito alto | Fragmentação, custo, suporte | Hardware, protocolos, suporte | **R** |
| 83 | Batida automática por aproximação ou modo anônimo | 0 | 1 | 0 | 0 | 0 | 0 | 1 | Muito alto | Registro involuntário, erro, falta de identidade, vigilância | Câmera contínua, política, consentimento/base, confirmação | **R** |
| 84 | Controle de acesso e catracas no núcleo | 0 | 1 | 0 | 0 | 0 | 0 | 1 | Muito alto | Bloqueio físico indevido, alta responsabilidade | Hardware crítico, disponibilidade, normas de segurança | **R** |

### Leitura da matriz

- **P0:** protege o núcleo, fecha dívida operacional ou desbloqueia decisão jurídica.
- **P1:** necessário para V1 comercial e ciclo mensal real.
- **P2:** eficiência, integrações ou diferenciação após o núcleo.
- **P3:** nicho/futuro condicionado a demanda.
- **R:** rejeitado do roadmap central.
