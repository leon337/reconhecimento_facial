# ADR — Integração real do Novo Funcionário V2 (homologação)

**Estado:** implementação de homologação, branch isolada; não representa conformidade trabalhista/LGPD certificada nem autorização de produção comercial.

## Fonte funcional
- Protótipo canônico `docs/nf-01/prototype/screens/03.04-novo-funcionario-v2.html` (NF-01, Fase L).
- Os arquivos do Design Lab permanecem intactos; o `new-employee-v2.js` do laboratório é uma simulação e **não** foi exposto como fluxo de cadastro real.
- A rota existente `GET /admin/users/new` agora redireciona para o assistente real de oito etapas; `POST /admin/users` legado permanece para compatibilidade até descontinuação formal.

## Regras de arquitetura
- Manter Flask + SQLAlchemy + SQLite existente em homologação, sem novos serviços públicos.
- Adicionar duas tabelas: `onboarding_drafts` (rascunho por administrador/empresa/obra, número de versão e estado) e `employee_onboarding` (detalhes adicionais criptografados por empregado).
- O cadastro principal permanece em `employees`, ligado a `users` pela identidade técnica. O usuário técnico criado não tem permissão administrativa nem senha conhecida; solicitar acesso no fluxo V2 **não** o ativa. Isso evita privilégios implícitos.
- Os campos declarativos replicam as oito etapas canônicas, inclusive pessoais, endereço, vínculo, pagamento, acesso e biometria.
- O cofre `instance/onboarding-fernet.key` é distinto do banco e da chave de biometria, com permissão 0600; nenhum dado sensível é registrado em logs ou em armazenamento local do navegador.
- O servidor impõe lista de campos, tipos, comprimento e seleções válidas. Cargos nunca são mapeados para `User.role='admin'`.
- Salvamentos de rascunho são transacionais com versão otimista; concorrência antiga retorna 409 em vez de sobrescrever.
- Conclusão sob a mesma transação cria `Employee`, `User` técnico, `EmployeeOnboarding` criptografado e trilha de auditoria. O mesmo envio é idempotente.
- RBAC `users:create` e escopo por empresa/obra são verificados em todas as rotas, inclusive na listagem de rascunhos.
- Dados opcionais especialmente sensíveis exigem confirmação de transparência; a checkbox não substitui definição de base legal, política de retenção ou avaliação da necessidade pelo controlador.
- A captura facial usa a tela operacional preexistente, depois da conclusão. Nenhum mock ou dado biométrico é transmitido pelo novo formulário.
- O banco antigo, relatórios, registros de ponto e perfis faciais existentes são preservados. Migração Alembic adiciona somente tabelas; rollback do aplicativo anterior continua possível sem eliminar tabelas novas.

## Limitações explícitas antes de produção
- O fluxo registra informações adicionais criptografadas, mas não entrega ainda processamento de folha, importação e-social, edição pós-cadastro ou ativação automatizada de convites.
- Validação humana e jurídica é necessária para dados bancários, raça/cor, PCD, dependentes, bases legais, consentimentos específicos quando aplicáveis, prazos de retenção e direitos dos titulares.
- Usuários de homologação devem usar dados fictícios. A integração comercial exige testes de acessibilidade manual e aprovação de liberação.
- Espaço em disco abaixo de 3 GiB no computador precisa ser tratado antes de ampliar armazenamento ou implantar cargas adicionais.

## Reversão
- Manter a imagem e o contêiner de relatórios anteriores parados, criar cópia consistente do SQLite e preservar a chave de criptografia da versão nova.
- Caso o health check falhe, restaurar o contêiner anterior; nunca apagar o banco sem aprovação explícita.
