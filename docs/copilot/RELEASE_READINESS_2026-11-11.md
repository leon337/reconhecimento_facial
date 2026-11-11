# Copiloto Potiguar — prontidão para publicação (11/11/2026)

**Autorização humana:** LEANDRO autorizou testes, merge e deploy com tudo funcionando. Autorização recebida, mas não equivale a dispensar os requisitos regulatórios da aplicação de ponto.

## Verificações realizadas

- PR #36 (interface Vue e serviço Live) incorporado à `main` em `4a2abd8`, com a flag de IA desligada por padrão.
- PR #37 contém o portal de credenciais cifradas, compatibilidade dos tokens efêmeros Google e leitura **somente leitura** do cofre SQLite.
- Google Gemini 3.8 Live e Live Extended Thinking: API autenticada, áudio sintético bidirecional, transcrição de entrada e saída e resposta falada testadas.
- Regressão Python completa: **163 testes aprovados em contêiner isolado**, sem dados trabalhistas reais.
- Portal: **12 testes de segurança aprovados**, incluindo uso único e SQLite cifrado; workflow isolado também executado.
- Frontend: compilação Vue reproduzida, três verificações de conversão PCM aprovadas.
- Homologação local: imagem de aplicação iniciada com SQLite sintético, administrador de teste, cofre privado somente leitura, `/health` HTTP 200, interface autenticada e emissor efêmero Live HTTP 200.
- Ambiente de homologação expõe apenas o `localhost` do host. Acesso externo de testes requer gateway autenticado e HTTPS.
- Imagem de homologação pode ser construída por sobreposição de fontes na imagem local já instalada, mas isso não substitui um build integral reproduzível da imagem oficial.

## Pendências para operação real de ponto (P0)

1. **Destino de produção** com domínio próprio, DNS, TLS, servidor/conta de implantação definida e serviços duráveis. Nenhum destino final foi identificado nas verificações de 11/11/2026.
2. **PostgreSQL de produção** com volume persistente, migrações Alembic revisadas e ensaio de rollback.
3. **Backup e restauração** reais em ambiente isolado, com política de retenção e controle de acesso.
4. **Revisão jurídica, trabalhista e LGPD** do sistema de registro e tratamento biométrico; não declarar conformidade por evidência apenas técnica.
5. **Segurança operacional**: segredos externos, administração protegida, limites de requisição, HTTPS, auditoria, monitoramento e resposta a incidentes.
6. **CI completo no HEAD de release**: os runners do GitHub tiveram falhas externas de DNS durante `apt-get update`; a suíte local não deve substituir automaticamente todos os checks formais.
7. **Homologação humana em dispositivos reais** (navegação, acessibilidade, voz, microfone e latência) e critérios de aceitação.

## Política de deploy

- Pode-se **implantar e divulgar um ambiente de homologação com dados sintéticos**, deixando explícito que não é serviço oficial de ponto.
- Nunca publicar a chave Gemini nem o cofre no Git ou em contêiner sem volume privado de leitura restrita.
- O portal de coleta de chave já cumpriu seu objetivo; **não reabrir o recebimento público de segredo** durante a demonstração.
- O piloto local deve manter a feature flag do copiloto ligada apenas no ambiente de ensaio, com limites de custo do provedor.
- Para produção real, respeitar o gate `docs/09_DEPLOY.md`: CI, security review, LGPD, backups, HTTPS, smoke tests, observabilidade e autorização.
- Não usar túnel temporário Cloudflare como endpoint definitivo de produção: URLs mudam, não há SLA e o túnel depende da máquina ligada.

## Rollback

Se a homologação apresentar falha, interromper acesso externo, parar o contêiner do release, manter volume de dados sintéticos e restaurar a imagem anterior, validando `GET /health`. Não afetar a `main`, o cofre original nem bases reais.

## Referências

- PR #36: https://github.com/leon337/reconhecimento_facial/pull/36
- PR #37: https://github.com/leon337/reconhecimento_facial/pull/37
- Evidências de voz: `docs/copilot/2026-11-11_LIVE_PROVIDER_SMOKE.md`
- Critérios operacionais: `docs/09_DEPLOY.md` e `DECISOES_CONGELADAS.md`
