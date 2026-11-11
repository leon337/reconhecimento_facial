# Copiloto Potiguar — MVP independente (11/11/2026)

**Status:** EXPERIMENTAL / IMPLEMENTADO EM BRANCH DE PROPOSTA. NÃO INTEGRADO À MAIN E NÃO IMPLANTADO.

**Motivação:** interface conversacional por voz e texto para tornar o Controle de Ponto Potiguar mais acessível e reduzir a necessidade de conhecer menus. Decisão executiva: LEANDRO autorizou MESTRE a decidir a arquitetura e **implementar em branch separada**. Permanecem **sem autorização** merge e deploy de produção.

## Decisão de engenharia (ADR 001)

- **Manter Flask + SQLAlchemy** como fonte de verdade e executor de domínio (registro de ponto, RBAC, biometria, banco); **não reescrever o backend**.
- **Vue 3 + Vite** para novo módulo frontend responsivo isolado em `frontend/copilot`. Build versionado em `static/copilot`; não necessita Node.js no processo Flask.
- **Gemini Live 3.8** é o modo rápido. **Gemini 3.8 Live Extended Thinking** é modo de raciocínio aumentado selecionado antes da sessão, com `thinkingLevel=medium`.
- **Não existe o termo Xend como serviço separado**: refere-se ao modo Extended Thinking da mesma família.
- **Protocolo Live** com conexão navegador → Google por WebSocket. O Flask, autenticado, fornece **token efêmero de uso único**, restrito ao modelo, com 60 s para iniciar e 15 min para conexão. A chave permanente **nunca** é enviada ao cliente.
- **Acesso:** apenas sessões administrativas com permissão `users:view`; o backend valida toda solicitação com RBAC e POST com CSRF. Auditor pode consultar o guia; operador de ponto não possui essa permissão.
- **Segurança do escopo:** sem tools de escrita, sem consulta a dados pessoais, sem listas de usuários expostas à IA, sem alterações de cadastros, ponto, folha, jornada ou biometria.
- **Privacidade:** o envio de mensagens ou áudio depende de consentimento explícito; nada é guardado em `localStorage`, e não há gravação ou armazenamento de áudio no servidor Potiguar.
- **Acessibilidade:** áudio, entrada de texto, legendas/transcrições, labels, foco visível, redução de movimento e layouts responsivos; o assistente não substitui teclado nem leitor de tela.
- **Disponibilidade:** funcionalidade `OFF` por padrão. Mesmo desligada, a página oferece uma **prévia com respostas locais de orientação** ao clicar nas sugestões, sem chamadas Gemini.

## Rotas

- `GET /admin/copilot`: interface, autenticada; prévia disponível sem chave.
- `GET /admin/copilot/meta`: estado/links de navegação, sem dados de funcionários.
- `POST /admin/copilot/session-token`: somente com a feature habilitada, API key configurada, modelo permitido, CSRF e janela mínima de 15 s por sessão. Resposta sem cache.

Nenhum endpoint do copiloto executa operações de escrita do ponto.

## Como executar localmente (somente ambiente de teste)

1. Reutilize um ambiente Python da aplicação que já tenha as dependências em `requirements.txt`.
2. No diretório `frontend/copilot`, rode `npm ci && npm run build` (a compilação foi testada; o build está versionado).
3. Inicie Flask como habitualmente; acesse `/admin/users`, autentique-se com conta de gestor e clique **Copiloto Potiguar (prévia)**.
4. Sem habilitação, verifique a prévia de forma segura.
5. Para conexão real em ambiente de teste, disponibilize `POTIGUAR_COPILOT_ENABLED=1` e `GEMINI_API_KEY` como segredo **no servidor**, nunca no repositório nem no frontend. Use HTTPS ou localhost para o microfone.
6. Autorize microfone somente quando desejar; conclua/encerre a sessão para interromper a captura.

**Configuração de credenciais:** a chave real não está provisionada nesta branch. Os testes usam exclusivamente valores simulados; uma sessão com o provedor real requer ambiente autorizado e chave fornecida pelo administrador.

## O que o MVP entrega

- Um workspace Vue de gestão com interface própria.
- Login herdado do Flask, permissões e controle de acesso.
- Chat por texto, microfone com áudio PCM 16kHz, reprodução de resposta PCM 24kHz, transcrições na tela.
- Seleção de modelo normal e Extended antes da sessão.
- Contexto de orientação restrito; atalhos oficiais para Funcionários e Novo Funcionário.
- Consentimento antes do envio externo e não retenção local de histórico.
- Feature flag desligada por padrão e erros tratados.

## Ainda NÃO entrega

- Preenchimento ou gravação de cadastro por IA.
- Registro de ponto por voz ou IA (isso deve passar pelo fluxo de identidade/liveness e regras de domínio, nunca pela fala isolada).
- Consulta autônoma a dados pessoais, permissões ampliadas, biometria, folha de pagamento, correção de jornada ou ações administrativas.
- Homologação jurídica/regulatória, testes E2E contra o serviço Google com chave real, testes de usuários com deficiência.
- Migração do restante do frontend para Vue e deploy.

## Critérios de aceite / regressão

1. CI Python existente e testes novos do copiloto passam.
2. Vite compila sem erros, sem chave permanente no bundle.
3. Contas sem `users:view` não recebem interface nem tokens.
4. Sem configuração, API retorna 503 e o layout permanece em prévia.
5. Token de sessão possui model allowlist, expiração curta, 1 uso e resposta sem cache; erros não expõem segredos.
6. Nenhum domínio de dados reais é exposto ao fornecedor automaticamente.
7. Nenhum merge/deploy/implantação sem nova autorização de LEANDRO.

## Evolução posterior (depende de gate explícito)

- Formulários guiados de cadastro com **pré-visualização**, validação de campos, confirmação final e execução pelas mesmas rotas RBAC/CSRF do sistema; nunca escrever no banco diretamente por proposta do modelo.
- Ferramentas de leitura com listas explicitamente limitadas à empresa/obra do usuário, minimização de dados e política LGPD.
- Testes de acessibilidade com usuários reais, latência, custo por sessão, fallback offline, telemetry sem PII e renovação/resume de sessão Live.
- Migração gradual de outras telas para Vue somente após evidência de ganho.

### Referências técnicas oficiais
- https://aistudio.google.com/docs/live-api
- https://aistudio.google.com/docs/live-api/ephemeral-tokens
- https://aistudio.google.com/docs/live-api/capabilities
