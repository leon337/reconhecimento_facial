# Potiguar — duas linhas oficiais de implantação

**Decisão de arquitetura:** 2026-11-17. **Escopo:** leon337/reconhecimento_facial.
**Autoridade final:** responsável humano. **Operação:** MESTRE.
**Status:** política versionada; nenhuma alteração automática na produção.

## Regra operacional

**Um único código-fonte Git; dois ambientes oficiais independentes.**

| Aspecto | Desenvolvimento | Produção |
| --- | --- | --- |
| Branch permanente | `develop` | `main` |
| Compose | `docker-compose.local.yml` | `docker-compose.production.yml` |
| APP_ENV / POTIGUAR_DEPLOYMENT_ROLE | development / development | production / production |
| Dados | testes sintéticos por padrão; dados reais somente com autorização, privacidade e retenção definida | funcionários reais |
| Rede | acesso restrito e autenticado; não usar Quick Tunnel sem login para pessoas reais | HTTPS de domínio gerenciado, autenticação e RBAC |
| Persistência | banco e cofre próprios; proibida conexão ao banco de produção | banco, backup e cofre próprios |
| IA | ferramentas tipadas, recibos verificáveis, dados protegidos inseridos somente no formulário | mesmas restrições, com aprovação humana |
| Operação final | operador deve confirmar cada criação real no formulário | operador confirma e servidor audita a criação |
| Publicação | merge no `develop` após CI | PR `develop` → `main` + gate humano + backup/rollback |

**Branches de recurso e PRs não são cópias de ambiente**, mas têm prazo curto e devem ser resolvidos por merge, fechamento justificado ou vinculação a uma tarefa ativa. Nunca fazer push forçado na `main` ou deploy implícito de produção.

## Cadastro assistido de funcionário real

O cadastro V2 possui oito etapas. O Gemini Live pode navegar nos módulos, orientar cada etapa e enviar propostas **somente para campos explicitamente permitidos** (sem dados fiscais, bancários, médicos, biometria ou senhas). Depois de cada proposta, a interface aguarda sucesso do backend para confirmar o salvamento. No final:

1. O agente usa `operate_onboarding({action:"request_completion"})` **somente na etapa 8**; o recibo diz `awaiting_human_confirmation`, nunca `created:true`.
2. A tela exibe a revisão e destaca `Concluir cadastro`.
3. O operador confere todos os dados e clica no botão. É exibida confirmação explícita com o nome cadastrado.
4. O servidor valida todos os dados, a versão do rascunho, a autorização RBAC e o escopo de empresa/obra. A criação é transacional; apenas sucesso com ID real gera confirmação no front.
5. Nenhum acesso administrativo é concedido automaticamente. Biometria usa o fluxo separado com transparência e autorização.

**Não cadastrar pessoas reais na demonstração anônima.** O serviço `app.public_demo` bloqueia `/complete` e campos protegidos por design. Para validar a gravação real, usar somente a instalação privada de desenvolvimento, com autorização dos titulares e política de retenção de dados, antes de testar produção. O teste automático usa somente identidades fictícias.

## Estado de implantação: reconciliação obrigatória

Em 2026-11-17 havia três instalações Flask de testes ativas no notebook (public demo e duas HML), além de túnel e gateway auxiliares e vários contêineres de backup **parados**. Isso é legado de testes e não representa três versões oficiais. **Produção externa não foi confirmada na consulta ao host**, logo não alegar dois deploys ativos. A migração deve:
- Identificar o banco real e backups antes de parar ou excluir qualquer contêiner/volume;
- Preservar evidências e dados, desligar os túneis e demos antigos somente depois de validar o novo desenvolvimento restrito;
- Não apagar volumes, registros ou credenciais sem autorização específica;
- Tratar o ambiente de produção como não promovido até haver domínio, acesso, backup, CI e gate comprovados.

## Protocolo para não deixar trabalho sem reconciliação

Após **cada** alteração de código:
- Revisar `git status`, `git diff --check` e testes aplicáveis;
- `git fetch --prune origin`, conferir upstream e divergência;
- Fazer commit identificado, push sem `--force` e verificar SHA remoto igual ao local;
- Manter PR do recurso vinculado ao `develop`, com checklist e verificações de CI;
- Encerrar o PR com merge ou justificativa documentada, ou registrar bloqueio verificável com responsável e próximo passo. Não afirmar conclusão com CI pendente;
- Promover `develop` para `main` **somente** com critérios de liberação, rollback testado e aprovação humana. Não misturar o trabalho de pagamentos e NF-01 com mudanças de cadastro.

## Gatilhos de aprovação e tarefas objetivas

- [x] Fonte única e ambientes definidos; guardas de APP_ENV para desenvolvimento/produção.
- [x] Contrato `request_completion` com recibo sem criação; confirmação humana no V2.
- [x] Contrato de metadados atualizado para manter modo `guidance_only` com recurso desabilitado.
- [ ] CI do PR de desenvolvimento inteiramente verde após alterações atuais (bloqueia merge).
- [ ] Teste ponta a ponta em desenvolvimento protegido até a criação sintética transacional, verificando lista e auditoria.
- [ ] Reconciliar e aposentar instâncias legadas depois de backups e validação; não excluir arquivos de pessoas.
- [ ] Identificar ambiente real de produção e homologar backups, credenciais, domínio e plano de rollback.
- [ ] Obter dados de funcionário e consentimentos correspondentes, quando houver registro real autorizado. Nenhum dado pessoal foi fornecido nesta missão.
- [ ] Gate humano de publicação na produção.

**Limitação conhecida:** algumas respostas do formulário são protegidas e necessitam preenchimento humano local; o Copiloto não possui ferramentas para preencher documentos, pagamento, credenciais, biometria ou acionar a criação sem a confirmação do operador.
