# Copiloto Potiguar — teste com Google Gemini Live real (11/11/2026)

**Escopo:** notebook de desenvolvimento autorizado; chave Gemini existente no cofre cifrado SQLite, sem exibir seu conteúdo em logs, Git ou chat.

## Evidência da API do Google

| Verificação | Resultado |
|---|---|
| Credencial principal / catálogo | HTTP 200 |
| Modelo gemini-3.8-live | Listado com bidiGenerateContent |
| Modelo gemini-3.8-live-extended-thinking | Listado com bidiGenerateContent |
| auth_tokens com liveConnectConstraints | HTTP 400 INVALID_ARGUMENT; o serviço rejeita o nome do campo |
| auth_tokens sem liveConnectConstraints, uses=1 e expiracões curtas | HTTP 200; token efêmero emitido |
| Conexão Live 3.8 + entrada textual sintética | Conectada, 15 blocos de áudio PCM, transcrição recebida, turno concluído |
| Conexão Live Extended + thinkingLevel=low e entrada textual sintética | Conectada, 22 blocos de áudio PCM, transcrição recebida, turno concluído |

A conexão foi exercitada por SDK JavaScript @google/genai 3.1.0, somente com frase sintética, sem dados pessoais nem ferramentas de escrita de ponto.

## Limitação de segurança observada

O provedor **não aceitou model-bound ephemeral tokens no endpoint usado por esta credencial**. O backend do Potiguar valida a seleção contra lista explícita de dois modelos Live, mas o token emitido pelo Google **não é vinculado pelo provedor ao modelo selecionado**. A tokenização permanece de uso único, com cerca de um minuto para iniciar e 15 minutos de validade; um cliente malicioso detentor do token poderia tentar utilizá-lo com outro modelo da Live API. Não descrever a proteção como restrição criptográfica do modelo.

Para publicação comercial: revisar a implementação de escopo do Google, controlar custos e sessões, telemetria sem PII, auditoria e consentimento com revisão LGPD. O uso de token efêmero não equivale a homologação de segurança.

## O que não foi comprovado aqui

- Microfone real de celular ou leitor de tela de usuário final.
- Reconhecimento de voz em ambiente ruidoso, latência p95, custo ou quotas em carga.
- Troca de dados reais de ponto e biometria (explicitamente proibida neste MVP).
- Deploy em produção com domínio, TLS, banco de jornada persistente e requisitos legais.

**Política de integração:** somente após checks completos; a aplicação preserva a flag de IA desligada por padrão. A autorização geral de merge/deploy dada por LEANDRO não torna a conformidade legal ou a infraestrutura de produção automaticamente aprovadas.

## Rodadas adicionais de voz bidirecional e homologação isolada

- Áudio **sintético** criado a partir da resposta falada do Gemini Live, convertido de PCM mono 24 kHz para PCM mono 16 kHz sem dados de usuário.
- O mesmo áudio foi enviado pela Live API como entrada real PCM 16 kHz.
- **Gemini 3.8 Live:** áudio de entrada recebido e transcrito; 9 blocos de áudio de resposta, transcrição de saída, conclusão normal da interação.
- **Gemini 3.8 Live Extended Thinking:** configuração explícita de thinkingLevel=low; áudio de entrada recebido e transcrito; 13 blocos de áudio de resposta, transcrição de saída, conclusão normal.
- **163/163 testes Python passaram** em execução independente de contêiner usando o código atual da proposta, sem acesso a banco de produção.
- **12/12 testes do portal criptografado passaram**, incluindo leitura de SQLite sem qualquer escrita no arquivo do cofre.
- **3/3 testes JavaScript PCM passaram**; a compilação Vite reproduziu os arquivos estáticos versionados.
- A homologação técnica isolada no notebook atende apenas localhost (127.0.0.1:18951) e emprega banco SQLite sintético, conta fictícia e cofre da API montado somente para leitura.
- Smoke HTTP do contêiner: /health HTTP 200, acesso de visitante ao copiloto redirecionado ao login, workspace e metadados de gestor fictício HTTP 200, feature habilitada e cofre configurado; POST /admin/copilot/session-token com sessão e CSRF de teste retornou HTTP 200 e cabeçalhos no-store.
- **Limite desta homologação:** utiliza runtime de imagem de base anterior com módulos da proposta montados para validação. Não é um artefato imutável final, não contém banco trabalhista real, não está exposto publicamente e **não** autoriza produção.

## Infraestrutura de CI externa

Nos runs de PR #37 em 11/11/2026, jobs do GitHub que instalam bibliotecas do sistema estão sujeitos a falhas na resolução DNS de espelhos Ubuntu (ex.: azure.archive.ubuntu.com e security.ubuntu.com). O workflow independente de testes do portal passou. A suíte de 163 testes foi executada fora desses runners e não equivale a declarar verde o conjunto de checks ainda pendentes.
