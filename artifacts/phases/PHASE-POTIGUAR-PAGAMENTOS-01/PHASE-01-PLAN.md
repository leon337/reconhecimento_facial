# Plano — PHASE-POTIGUAR-PAGAMENTOS-01

- **Missão:** MCF-POTIGUAR-PAGAMENTOS-20261113
- **Referência canônica:** https://github.com/leon337/multiagent-collaboration-framework/issues/522
- **Coordenador:** MESTRE; autoridade humana LEANDRO; autoridade interna de gate LÉO, quando disponível como agente distinto
- **Classificação:** Classe C (risco trabalhista, financeiro e de proteção de dados).
- **Ponto de partida:** `feat/potiguar-conversational-controller-20261113@5d7d4fdd`.
- **Objetivo:** disponibilizar primeiro recorte navegável e seguro de períodos semanais/jornadas sem apurar ou pagar valores.
- **Resultado esperado:** modelos, migração, telas e endpoints autenticados por empresa/obra, teste de isolamento, relatório e checkpoint.
- **Escopo:** descoberta estrutural de Excel, modelagem não monetária, controles RBAC, validação de horas, auditoria, testes sintéticos.
- **Exclusões:** importação de dados reais, fórmulas financeiras, PIX, aprovação financeira, deploy e merge.
- **Fontes:** cinco arquivos privados da contabilidade; código Potiguar real; AGENTS.md, docs/MCF-CURRENT-STATE.md e protocolo ESEV/PRF do MCF.
- **Premissa relevante:** nenhuma regra de diária/hora/adicionais pode ser inferida apenas da estrutura do Excel.
- **Riscos:** divergência de fórmula (#REF!), quebra de isolamento, fraude de jornada, exposição de dados pessoais e ações financeiras indevidas.
- **Controles:** nenhuma quantia financeira no esquema, empresa obrigatória, validação de funcionário/obra, CSRF, eventos de auditoria, branch isolada.
- **Critérios de aceite:** 1. login e papéis; 2. escopo; 3. rascunhos de 7 dias; 4. validação de tempos; 5. rejeição de duplicidade; 6. ausência de liquidação; 7. migração real em banco temporário; 8. testes; 9. PRF.
- **Gates:** LÉO e LEANDRO somente nos boundaries exigidos; produção/pagamento não autorizados nesta fase.
- **Ciclo:** 1.
