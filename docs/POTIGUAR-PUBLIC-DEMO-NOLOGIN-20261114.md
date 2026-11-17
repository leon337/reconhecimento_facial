# Potiguar — Demonstração pública sem login com Copiloto V2

**Data:** 14/11/2026
**Situação:** implementado e testado em instância pública isolada; NÃO homologação final e NÃO produção.
**Orquestrador:** MESTRE. **Autoridade final:** responsável humano do projeto.

## Decisão arquitetural

Não remover autenticação do Flask ou de qualquer deploy existente. Criar um **entrypoint independente** `demo_entry:app`, que importa o Flask normal e instala `app.public_demo.install_public_demo` somente quando `POTIGUAR_PUBLIC_DEMO=1` e condições de isolamento e HTTPS são verificadas.

O contêiner de demo `potiguar-copilot-public-demo-20261114` e seu Cloudflare Quick Tunnel `potiguar-copilot-public-demo-tunnel-20261114` são independentes de `potiguar-copilot-mobile-hml-20261113`, homologação anterior e produção. Banco SQLite, SECRET_KEY e Fernet são novos, em diretório de estado dedicado, fora do Git. Montagem do cofre Gemini é somente leitura. O bundle Vite e os controladores são um snapshot próprio e não compartilham os inodes do Vite compilado da HML.

### Comportamento de acesso

- `/admin/copilot` responde HTTP 200 imediatamente, com HTTPS e sem HTTP Basic ou formulário de login.
- `/admin/login` redireciona para o Copiloto.
- Cada navegador com novo cookie recebe um usuário e escopo de empresa/obra **exclusivamente sintéticos**. A conta tem papel `manager`, não `admin`, e uma senha aleatória inacessível/não utilizada; não há senha que o usuário precise digitar.
- O cookie de sessão é `Secure`, `HttpOnly` e `SameSite=Lax`. Usuários de navegadores diferentes não veem os rascunhos uns dos outros pela política de escopo.
- No aplicativo convencional, a autenticação permanece exigida; o módulo de demo não é importado por `main:app`.

### Limites e proteção

- Permitidos: visualização do dashboard, histórico de pontos, relatórios, funcionários, rascunhos; criação de rascunhos e formulário V2; consulta de metadados; ferramentas permitidas do Copiloto.
- Bloqueados por padrão: criação definitiva de funcionários, atualizações administrativas, biometria, registro de ponto, login/logout mutável e todos os endpoints não allowlistados.
- Para `/onboarding/<id>/save`, apenas campos sintéticos permitidos são gravados. Nomes pessoais de teste precisam começar com `Teste ` ou terminar com ` de Teste`; CPF, telefone, logradouro, conta bancária, PIX, biometria, acesso e outros campos protegidos são recusados quando preenchidos.
- Arquivos estáticos são permitidos somente por lista explícita; `/static/uploads/*` e scripts de captura biométrica retornam HTTP 403.
- O frontend mostra aviso visível: **DEMONSTRAÇÃO SEM LOGIN — use somente dados fictícios**.
- Cofre de IA permanece no servidor; o navegador recebe somente token efêmero.
- Limitadores: até 60 sessões Gemini Live por dia, tempo mínimo de 15 segundos entre novas emissões por sessão; até 180 identidades de demo na instância; até 30 rascunhos ativos por identidade. Não são limites globais de tráfego/uso do provedor.
- A página não deve ser usada com dados de funcionários reais. Quick Tunnel não tem SLA, pode expirar ou mudar de URL. Deploy definitivo deve usar túnel nomeado e política de acesso adequada.

## Copiloto V2 e suas capacidades reais

O shell persistente `/admin/copilot` sobrevive às mudanças de documento do iframe de mesma origem. A sessão `gemini-3.8-live` e o WebSocket permanecem no pai.

`navigate_potiguar`: abre somente `dashboard`, `attendance`, `reports`, `employees`, `drafts` e `new_employee`, com URLs fornecidas pelo backend e verificadas após a navegação. Não há navegação arbitrária nem ferramentas para editar qualquer módulo genericamente.

No cadastro V2 de **oito etapas**, o Copiloto usa `suggest_onboarding_fields`, `navigate_onboarding` e `operate_onboarding` para propor, preencher e salvar campos seguros, navegar pelas etapas autorizadas, recuperar estado, focar campo e pular opcional. O controlador valida o campo ativo e confirma a persistência no Flask antes do recibo. Valores protegidos devem ser preenchidos fora da IA e na demo são impedidos no servidor. A conclusão do funcionário permanece negada.

A navegação entre módulos não derruba o Live. A entrada no cadastro pode pausar o microfone por segurança sem encerrar a sessão; ele pode ser reativado em campos seguros.

## Evidências executadas

- Flask: 26/26 testes de demo, sessão, segregação, guardrails e regressão aprovados.
- Frontend: 39/39 testes JavaScript aprovados; compilação Vite concluída.
- Chrome móvel emulado 412×896 na URL pública **sem qualquer credencial**: 13 verificações de sessão, ferramenta de navegação real, microfone, conexão contínua e gravação do campo V2 — PASS, 1 WebSocket aberto, 0 fechado, 0 erros JS.
- Chrome móvel emulado na URL pública: 17 verificações de linguagem natural (incluindo pergunta sem gravação, sinônimo intermitente, falha HTTP 503 e recuperação, rascunhos e sessão contínua) — PASS.
- HTTP público: `/admin/copilot` 200; `/admin/login` redireciona; `/static/copilot/pcm-worklet.js` 200; `/static/uploads/any.jpg` 403.
- Regressão adversarial prévia: 40.000 cenários sintéticos, 3.600 chamadas simuladas de ferramenta, confirmação vetorizada usando AMD Radeon RX 580 via ANGLE/Vulkan. Não confundir essas execuções locais com 40.000 conversas reais do Gemini.

### Limites ainda não certificados

Áudio foi testado em navegador móvel **emulado com microfone virtual**, não em um smartphone físico. Não foram certificados execução de ações arbitrárias fora das ferramentas tipadas, operação em segundo plano, persistência após fechamento da aba, uso de dados reais ou implantação de produção.

## Execução e rollback

Build frontend:
`cd frontend/copilot && npm test && npm run build`

Testes em contêiner isolado:
`python -m unittest tests.test_public_demo_no_login_unittest tests.test_copilot_onboarding_runtime_unittest tests.test_onboarding_v2_unittest`

Deploy preparado apenas para a máquina de laboratório:
`python3 scripts/potiguar_deploy_public_no_login_demo.py`

O deploy recusa sobrescrever contêineres/snapshots existentes. Remover a demonstração exige parar e remover **apenas** os contêineres `potiguar-copilot-public-demo-20261114` e `potiguar-copilot-public-demo-tunnel-20261114` e, quando autorizado, limpar seus arquivos sob `/home/leo/.local/state/potiguar-public-demo-20261114`. Produção e HML protegida não são afetadas.

**Nota:** o endereço Cloudflare Quick Tunnel não deve ser usado como URL permanente.
