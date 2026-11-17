# Entrada Vercel — Demonstração sintética Potiguar

Escopo: somente demonstração pública sem login, isolada do banco de produção.

Esta pasta publica um gateway HTTP na Vercel para o backend sintético existente, com a allowlist do módulo app/public_demo.py. Não migra o Flask, o SQLite, o cofre Gemini, a biometria ou o ambiente privado à Vercel. Não equivale à implantação integral da aplicação. As regras de acesso permanecem no backend e devem ser validadas pelo exterior: X-Potiguar-Demo: synthetic-no-login, uploads 403, cadastro definitivo negado.

A regra rewrites do vercel.json aponta para um Cloudflare Quick Tunnel temporário, que pode expirar ou ficar indisponível. Se a origem mudar, será necessário atualizar a URL neste arquivo, testar a allowlist e redeployar. Para uma publicação durável, substituir a origem por um endpoint HTTPS estável do backend sintético, com autorização humana e configuração segura. Um endereço .vercel.app estável, por si só, não transforma o backend temporário em persistente.

O objetivo é viabilizar testes externos com Gemini/ChatGPT usando dados fictícios, nunca disponibilizar cadastros reais. A conta do operador, CPF, salário, dados bancários, biometria e documentos reais não devem entrar nesta demonstração.

## Deploy e verificação

Criar projeto isolado potiguar-v2-demo na equipe autorizada e publicar esta pasta como raiz do projeto. Validar /admin/copilot (HTTP 200 com cabeçalho sintético), /admin/login (redireciona), /static/uploads/any.jpg (403), rascunhos fictícios, cabeçalhos e navegação V2. Se a origem retornar 5xx, suspender divulgação do novo link.

A promoção de desenvolvimento para produção real permanece separada, com HUMAN_GATE.
