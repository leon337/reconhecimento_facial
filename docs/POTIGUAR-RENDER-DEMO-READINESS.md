# Potiguar — backend sintético no Render (plano gratuito)

**Referência:** 17/11/2026. **Situação:** configuração versionada, implantação **BLOQUEADA pela capacidade do workspace**, não publicada.

## Conta e inventário

Workspace autorizado: Render **Leandro's workspace** (ID `tea-d2u2msje5dus73eb6ehg`). A listagem ao vivo encontrou **25 serviços** e nenhum serviço correspondente a `leon337/reconhecimento_facial`. A tentativa de criar `potiguar-v2-demo-backend` com `plan=free` retornou exatamente: `Hobby Tier is limited to 25 services`.

**Não remover ou reaproveitar serviços de outros repositórios automaticamente.** A aplicação `potiguar-intermitente-app` identificada no workspace pertence a outro repositório e foi preservada. Para liberar uma vaga, a autoridade humana deve aprovar qual serviço está comprovadamente obsoleto; não contratar plano pago por inferência.

## Infraestrutura pronta no repositório

- `render.yaml` — Blueprint isolado de **um** serviço web Docker `free` em `virginia`, repo `leon337/reconhecimento_facial`, branch **`develop`**, `autoDeployTrigger: off`, sem previews.
- `scripts/potiguar_render_demo_entry.py` — inicia exclusivamente o entrypoint já existente da **demonstração sintética**; **nunca `main:app`**.
- `scripts/potiguar_render_demo_environment.py` — falha antes de importar o Flask se ambiente, banco, segurança, flags, worker ou segredo divergem. Rejeita qualquer Gemini API key, cofre remoto ou chave biométrica. Usa um `SECRET_KEY` aleatório gerado no Render (não no Git) para derivar a chave Fernet da demonstração.
- `tests/test_render_demo_environment_unittest.py` — contrato de negação em caso de variáveis ausentes, banco privado, production mode ou segredos indevidos.
- `scripts/potiguar_render_demo_smoke.py` — diagnóstico externo somente leitura e limitado à URL exata da demo Render, incluindo cabeçalho sintético e bloqueio de uploads.

As variáveis de ambiente e limites estão no Blueprint, sem chaves comprometidas. O modo público mantém `app.public_demo.install_public_demo` e sua allowlist; são bloqueados CPF, telefone, dados financeiros/biométricos e a conclusão do funcionário. Sem `GEMINI_API_KEY` ou cofre externo, **Gemini Live não ficará conectado** no Render; isso é intencional até uma aprovação e controle de quota durável.

## Limitações obrigatórias do Free

- O Render pode hibernar após 15 minutos ociosos; a primeira abertura pode demorar a iniciar.
- **SQLite no Render gratuito é efêmero**: os rascunhos fictícios podem desaparecer após hibernação, reinício ou redeploy. Esse serviço entrega **nome HTTPS estável**, não armazenamento durável. Não prometer recuperação de rascunhos entre sessões longas.
- A quota gratuita de 750 horas por workspace é compartilhada com outros serviços e o provedor pode suspender serviços ao consumir a franquia.
- Render Free Postgres também expira após 30 dias, portanto não resolve a exigência de persistência permanente sem outra decisão de dados. Nenhuma base de dados nova foi criada.
- O Dockerfile original instala bibliotecas pesadas de reconhecimento facial apesar da rota pública bloqueá-las; **viabilidade da compilação e memória do plano Free não foi comprovada**, portanto validar antes de promover a origem.

## Sequência controlada de liberação (somente depois de resolver o limite)

1. Liberar **uma vaga** por decisão humana específica sobre serviço obsoleto, ou outra solução sem contratação paga. Confirmar novamente a contagem de serviços e o plano.
2. Validar o Blueprint `render.yaml` e criar/aplicar exclusivamente `potiguar-v2-demo-backend`, garantindo `plan: free`, `autoDeployTrigger: off` e `develop`. Registrar Service ID e deployment SHA.
3. Aguardar o estado `live` e executar `python scripts/potiguar_render_demo_smoke.py`; conferir em navegador que são dados sintéticos, rascunhos fictícios, isolamento por cookie e negativa de criação real.
4. **Só após PASS** alterar a reescrita de `deploy/vercel-demo/vercel.json` para `https://potiguar-v2-demo-backend.onrender.com` por PR dedicado em `develop`, testar HTTPS da Vercel/Render, e preparar rollback à configuração anterior. Não alterar a produção real.
5. Para persistência longa e Gemini Live real, abrir missão separada de banco e gestão de segredos. **Não anexar credenciais reais à instância Free efêmera**.

## Ambientes preservados

- Produção privada, main e homologação: intactos.
- Demo pública atual: https://potiguar-v2-demo.vercel.app/admin/copilot — continua com backend atual via Cloudflare Quick Tunnel até a migração validada.
- Branches/PRs de pagamentos e NF-01: fora deste escopo e preservados.

Critério de saída desta missão de **preparação**: PR e CI verdes, Blueprint válido/versionado, Render ainda sem serviço devido ao limite de 25, nenhuma origem Vercel alterada e nenhuma cobrança. Não confundir com uma implantação finalizada.
