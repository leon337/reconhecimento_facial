# Potiguar — correção de interface móvel e Gemini na homologação

**Data:** 11/11/2026
**Ambiente:** homologação isolada no notebook autorizado, com túnel HTTPS temporário e autenticação dupla. Não é produção oficial de ponto.

## Problemas constatados

1. O formulário de novo funcionário não possuía `<meta name="viewport">`, fazendo a interface inteira ser miniaturizada pelo Chrome Android.
2. As duas telas administrativas dependiam de Tailwind por CDN e não tinham padronização responsiva própria.
3. A homologação tinha `POTIGUAR_COPILOT_ENABLED=0` e cofre Gemini não montado: não era possível conversar com a IA, apesar de o Google Live ter passado em testes de laboratório.
4. A página do copiloto respondia `Referrer-Policy: no-referrer`. Em HTTPS com Flask-WTF `WTF_CSRF_SSL_STRICT`, isso pode fazer os POSTs de sessão Live serem rejeitados com HTTP 400 porque o navegador não envia Referer válido.

## Correções

- `templates/admin/users_new.html`, `templates/admin/users_list.html` e `static/admin-mobile.css`: viewport, CSS local mobile-first, campos de pelo menos 48 px, rótulos acessíveis, navegação para o Copiloto e cartões em largura de 412 px.
- `app/copilot/routes.py`: na **resposta HTML do workspace**, `Referrer-Policy: same-origin`, mantendo o Referer apenas para requisições do próprio Potiguar e atendendo CSRF estrito; os endpoints de token continuam com cabeçalhos `no-store` e `no-referrer`.
- `main.py`: flag de homologação HTTPS para cookie Secure, sem relaxar o modo production.
- `app/copilot/demo_quota.py`: cota global, atômica e persistida em SQLite local **somente para demonstração quando habilitada**. Definida na homologação como `POTIGUAR_COPILOT_DEMO_DAILY_LIMIT=12` sessões por dia UTC. Não garante custo zero e não se aplica ao sistema real quando ausente.
- Cofre criptografado Gemini montado **somente leitura** em `/run/potiguar-vault`, com a flag Live ativa apenas no contêiner de homologação. A chave original não foi copiada para o repositório nem adicionada ao Render.
- Gateway Caddy com HTTP Basic Auth + login Flask separados, HTTPS público via túnel Cloudflare temporário.

## Evidências

- **167 testes Python aprovados**, sem falhas, em contêiner isolado com banco e usuários de teste.
- Renderização HTML via Flask, viewport, CSS local e navegação: PASS.
- Teste concorrente do limite de sessões (16 solicitações simultâneas / 4 vagas): 4 permitidas, 12 rejeitadas.
- Inspeção visual via Brave headless no tamanho **412 × 915 px**. Capturas com usuários sintéticos nas pastas de evidência.
- Teste por HTTPS público: dupla autenticação, login, lista, formulário novo, workspace e metadados do copiloto **HTTP 200**, `enabled=true`, `configured=true`.
- Backend da homologação emitiu tokens temporários Live HTTP 200 com CSRF válido; a conversa sintética com **gemini-3.8-live** e **gemini-3.8-live-extended-thinking** retornou áudio e transcrição, turno concluído. Nenhuma credencial nem conteúdo de fala real foi registrado nas evidências.
- Tela HTML do workspace retorna `Referrer-Policy: same-origin`, para compatibilidade com HTTPS + CSRF estrito.

## Limites

- O Copiloto atual é **assistente por voz/texto para orientação**, não executa cadastros automaticamente, não altera biometria, folha ou batidas de ponto.
- O teste comprova o canal Live e sua infraestrutura; o microfone de um celular real ainda requer homologação presencial.
- O link `trycloudflare.com` depende do notebook e da sessão do túnel. Não é um endereço permanente.
- O banco de demonstração é SQLite sintético, não PostgreSQL de produção. Sem conformidade trabalhista/LGPD homologada para operação oficial.
- A cota de 12 tokens **não garante custo zero**: o uso da API do Google pode gerar cobrança conforme o plano associado à chave.
- A flag de IA permanece desligada por padrão em `main` e em produção; os segredos do ensaio ficam somente no host autorizado.
