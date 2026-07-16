# Instalação — Controle de Ponto Potiguar

## 1. Objetivo

Orientar a instalação do projeto em ambiente local e por Docker, usando Linux Mint como referência.

## 2. Pré-requisitos

### Instalação local

- Linux Mint ou distribuição compatível;
- Git;
- Python 3.10 ou versão compatível com as dependências;
- `venv` e `pip`;
- compilador C/C++;
- CMake;
- bibliotecas BLAS e LAPACK.

No Linux Mint/Ubuntu:

```bash
sudo apt update
sudo apt install -y \
  git python3 python3-venv python3-pip \
  build-essential cmake \
  libopenblas-dev liblapack-dev
```

### Instalação por Docker

- Docker Engine;
- permissão para executar `docker`.

## 3. Clonar o repositório

```bash
git clone https://github.com/leon337/reconhecimento_facial.git
cd reconhecimento_facial
```

Para desenvolvimento de uma fase, troque para a branch correspondente. Não altere a `main` diretamente.

## 4. Criar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

## 5. Instalar dependências

```bash
python -m pip install -r requirements.txt
```

A instalação de `dlib` pode demorar porque envolve componentes nativos. Uma falha nessa etapa normalmente indica ausência de compilador, CMake ou bibliotecas matemáticas do sistema.

## 6. Configurar o ambiente

Crie um arquivo `.env` local ou exporte as variáveis no terminal:

```bash
export APP_ENV=development
export SECRET_KEY='somente-desenvolvimento'
export DATABASE_URL='sqlite:///instance/ponto.db'
export PORT=5000
export FLASK_DEBUG=1
```

Não versione `.env`, chaves, bancos locais, fotos ou dados biométricos.

## 7. Executar localmente

```bash
python main.py
```

A aplicação escuta por padrão em:

```text
http://127.0.0.1:5000
```

Como `main.py` usa `host=0.0.0.0`, outros dispositivos da mesma rede poderão acessar pelo IP do computador quando o firewall permitir.

## 8. Executar com Gunicorn

```bash
gunicorn \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers ${WEB_CONCURRENCY:-1} \
  --timeout 120 \
  main:app
```

## 9. Executar com Docker

Construir a imagem:

```bash
docker build -t controle-ponto-potiguar .
```

Executar em desenvolvimento:

```bash
docker run --rm \
  -p 8000:8000 \
  -e APP_ENV=development \
  -e SECRET_KEY='somente-desenvolvimento' \
  controle-ponto-potiguar
```

Teste no navegador:

```text
http://127.0.0.1:8000
```

## 10. Executar testes

Com o ambiente virtual ativo:

```bash
python -m pytest -q
```

Validação de sintaxe:

```bash
python -m compileall -q app main.py tests
```

Validação do Docker:

```bash
docker build -t controle-ponto-potiguar:test .
```

Os testes unitários verificam regras isoladas; os testes de integração verificam o encaixe entre rotas, autenticação, banco e respostas HTTP. É o equivalente a testar cada estação e depois a linha de montagem completa.

## 11. Problemas comuns

### Erro ao instalar `dlib`

Confirme `build-essential`, `cmake`, `libopenblas-dev` e `liblapack-dev`.

### Banco não criado

Confirme permissão de escrita no diretório `instance/` e a URI em `DATABASE_URL`.

### `SECRET_KEY é obrigatória em produção`

Defina uma chave longa e aleatória antes de usar `APP_ENV=production`.

### Câmera indisponível

Verifique permissões do navegador, acesso ao dispositivo e uso exclusivo da câmera por outra aplicação.

## 12. Restrições de segurança

- use somente pessoas fictícias e imagens sintéticas em desenvolvimento;
- não copie banco de produção para o computador de desenvolvimento;
- não publique portas diretamente na internet sem HTTPS e reverse proxy;
- não trate a instalação local como autorização para produção.
