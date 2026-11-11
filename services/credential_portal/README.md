## Fluxo móvel simplificado — atualização 11/11/2026

A versão atual do portal usa **uma única página**, com dois campos:
(1) código temporário emitido pelo MESTRE e (2) chave API obtida no Google AI Studio.
O usuário clica uma vez em **Salvar chave com segurança**.

O navegador importa a chave pública RSA e cifra a API key antes de enviar
`POST /submit-once`; o servidor valida, no mesmo pedido, o desafio assinado
sem cookies, o código de uso único e a cifra. Não há redirecionamento ou
página intermediária, e a confirmação é exibida sem mudar de página.
A rota antiga `/unlock` devolve 409 para informar que o formulário
anterior ficou desatualizado. Caso o navegador ainda apresente duas telas,
reabra o endereço com uma query de versão para evitar conteúdo antigo em cache.

# Portal temporário de credenciais do Copiloto Potiguar

**Situação:** implementação em branch de proposta, sem merge e sem deploy de produção.

## Objetivo

Permitir que LEANDRO, de outro dispositivo, forneça a chave do Google AI Studio
**sem enviá-la a uma conversa, mensagem, arquivo do GitHub ou shell remoto**.
O processo implementa uma aplicação HTTP protegida, com transporte HTTPS via
Cloudflare Tunnel, criptografia no navegador e persistência local em SQLite cifrado.

O SQLite **não é servidor de rede**: o portal Flask recebe a chave pela rede,
descriptografa apenas em memória e a guarda no SQLite local com Fernet.

## Proteções implementadas

- Código de acesso aleatório, gerado uma vez, apresentado somente na preparação. Não confundir o código de acesso ao portal com a API key Gemini.
- Prazo limitado, 8 tentativas incorretas totais e revogação ao primeiro salvamento.
- **Login sem cookies de sessão:** formulário inicial com desafio assinado com expiração de 10 minutos; após confirmação do código, a própria resposta exibe o formulário de chave com um ticket assinado de 15 minutos em memória, sem redirecionamento nem valores sensíveis na URL.
- CSRF separado no acesso e na submissão, vinculado ao ticket e com validade curta; rejeita Origin e Referer de outros domínios.
- O browser cifra a API key com RSA-OAEP/SHA-256 (public key do servidor).
  O envio POST contém somente ciphertext Base64, não o valor original.
- O servidor decripta em memória e cifra novamente com Fernet, chave-mestra
  em arquivo privado **separado** do arquivo SQLite.
- Diretório 0700, arquivos privados 0600, sem logs com os valores das chaves.
- Banco SQLite e arquivos privados **fora do repositório**, sem subir segredos ao Git.
- Nenhuma leitura ou modificação de jornada, funcionários ou biometria.
- Não ativa a integração `POTIGUAR_COPILOT_ENABLED` automaticamente.
- Uso único e mensagem final sem revelar a chave.

**Atenção:** criptografia em repouso reduz risco em cópias do banco, mas
não substitui proteção do host. Quem controla a conta de serviço e possui
tanto o arquivo do banco quanto a chave-mestra pode recuperar a credencial.
O Cloudflare Tunnel é infraestrutura externa transitória e não possui
garantia de disponibilidade. Para produção, preferir domínio próprio,
controle de acesso do provedor, secret manager, auditoria e rotação de chaves.

## Execução isolada (não é um serviço de produção)

No diretório do checkout desta branch:

```bash
python3 -m venv /caminho/privado/venv
/caminho/privado/venv/bin/pip install -r services/credential_portal/requirements.txt

# O diretório não pode ser rastreado pelo Git.
mkdir -p /caminho/privado/cofre
chmod 700 /caminho/privado/cofre

/caminho/privado/venv/bin/python -m services.credential_portal.bootstrap \
  --private-dir /caminho/privado/cofre --ttl-seconds 7200

# Processo separado, somente localhost:
POTIGUAR_PORTAL_BOOT=1 \
POTIGUAR_COPILOT_VAULT_DIR=/caminho/privado/cofre \
  /caminho/privado/venv/bin/gunicorn \
  --workers 1 --threads 4 --bind 127.0.0.1:18779 \
  --access-logfile /dev/null services.credential_portal.portal:app
```

Para uso remoto, somente após validar autenticação, conectar
um túnel HTTPS temporário ao endereço `127.0.0.1:18779`.
**Nunca** permitir HTTP público ou expor a porta 18779 externamente.

Copiloto Flask (quando a branch de integração for aprovada):

```bash
POTIGUAR_COPILOT_VAULT_DIR=/caminho/privado/cofre
# Ativar por decisão operacional separada, em ambiente de teste:
# POTIGUAR_COPILOT_ENABLED=1
```

Se `GEMINI_API_KEY` estiver configurada no processo Flask, ela possui prioridade
sobre o cofre; remova ou deixe vazia para usar o SQLite.
O cofre fica no computador em que foi provisionado: implantação em outra
máquina exige um processo seguro de migração de credenciais.

## Testes

```bash
/caminho/privado/venv/bin/pip install -r services/credential_portal/requirements-test.txt
/caminho/privado/venv/bin/python -m pytest -q services/credential_portal/tests/
node --check services/credential_portal/static/submit.js
```

Os testes usam chaves **totalmente fictícias**, sem chamada ao Google.

## Validações necessárias após o recebimento

1. Confirmar estado de portal como `closed`, sem imprimir a chave.
2. Validar que o cofre SQLite tem ciphertext e permissões privadas.
3. Executar verificação controlada de conectividade com a API, sem logar a chave.
4. Verificar disponibilidade dos modelos 3.8 Live e Extended Thinking e quotas.
5. Revisar custo, consentimento e necessidade de habilitar a feature flag.
6. **Não mesclar nem fazer deploy** sem autorização explícita de LEANDRO.
