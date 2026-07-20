# FASE 10 — Piloto local no Linux Mint

## Objetivo

Disponibilizar o Controle de Ponto Potiguar em uma máquina Linux Mint, usando Docker Compose, PostgreSQL persistente e armazenamento biométrico privado.

## Arquitetura

```text
Navegador do computador/celular
        ↓ porta 8000
Aplicação Flask + Gunicorn
        ↓ rede Docker interna
PostgreSQL 16

Volumes persistentes:
- postgres_local
- biometric_local
```

## Pré-requisitos

- Linux Mint atualizado;
- Git;
- Docker Engine;
- plugin Docker Compose;
- computador e celular na mesma rede Wi‑Fi para o teste móvel.

## Primeira inicialização

```bash
git clone https://github.com/leon337/reconhecimento_facial.git
cd reconhecimento_facial
git checkout fase-10-implantacao-piloto
chmod +x scripts/start_local_pilot.sh
./scripts/start_local_pilot.sh
```

Na primeira execução, o script cria `.env.local`, gera segredos aleatórios e exibe a senha do administrador uma única vez.

## Endereços

No computador:

```text
http://localhost:8000
```

No celular conectado à mesma rede:

```text
http://IP_DA_MAQUINA:8000
```

O script mostra o endereço do celular ao finalizar.

## Comandos operacionais

Ver estado:

```bash
docker compose --env-file .env.local -f docker-compose.local.yml ps
```

Ver logs:

```bash
docker compose --env-file .env.local -f docker-compose.local.yml logs -f app
```

Parar:

```bash
docker compose --env-file .env.local -f docker-compose.local.yml down
```

Iniciar novamente:

```bash
docker compose --env-file .env.local -f docker-compose.local.yml up -d
```

## Dados persistentes

O comando `down` não apaga o banco nem as biometrias. Não use `down -v` durante o piloto, pois `-v` remove os volumes.

## Segurança do piloto

- `.env.local` não deve ser enviado ao GitHub;
- a porta do PostgreSQL não é publicada na rede local;
- a biometria fica em volume privado;
- o piloto usa HTTP apenas na rede local;
- dados biométricos reais somente devem ser cadastrados após o teste da câmera, backup e acesso administrativo;
- acesso pela internet permanece bloqueado.

## Checklist de aceite

- [ ] aplicação responde em `/health`;
- [ ] login administrativo funciona;
- [ ] empresa Potiguar e Obra Piloto existem;
- [ ] celular acessa a tela pela mesma rede;
- [ ] câmera é autorizada pelo navegador;
- [ ] uma batida sintética é registrada;
- [ ] reinício dos containers preserva os dados;
- [ ] backup local é executado e verificado;
- [ ] senha administrativa foi guardada em local seguro.
