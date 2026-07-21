#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "erro=Docker não encontrado. Instale Docker Engine e o plugin Compose."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "erro=Plugin docker compose não encontrado."
  exit 1
fi

if [[ ! -f .env.local ]]; then
  python3 scripts/configure_local.py
  echo "A senha administrativa foi exibida acima. Guarde-a antes de continuar."
fi

LAN_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
if [[ -z "$LAN_IP" ]]; then
  LAN_IP="127.0.0.1"
fi
export LAN_IP
export WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
mkdir -p instance/certs

docker compose --env-file .env.local -f docker-compose.local.yml up --build -d

echo "Aguardando a aplicação responder..."
for _ in $(seq 1 30); do
  if curl --fail --silent http://127.0.0.1:8000/health >/dev/null; then
    break
  fi
  sleep 2
done

if ! curl --fail --silent http://127.0.0.1:8000/health >/dev/null; then
  echo "erro=Aplicação não respondeu. Consulte: docker compose --env-file .env.local -f docker-compose.local.yml logs"
  exit 1
fi

for _ in $(seq 1 20); do
  if docker compose --env-file .env.local -f docker-compose.local.yml exec -T https-proxy \
    sh -c 'cat /data/caddy/pki/authorities/local/root.crt' \
    > instance/certs/potiguar-local-ca.crt 2>/dev/null; then
    if [[ -s instance/certs/potiguar-local-ca.crt ]]; then
      break
    fi
  fi
  sleep 1
done

if [[ ! -s instance/certs/potiguar-local-ca.crt ]]; then
  echo "erro=Não foi possível exportar o certificado HTTPS local. Consulte os logs do serviço https-proxy."
  exit 1
fi

chmod 644 instance/certs/potiguar-local-ca.crt 2>/dev/null || true

echo "status=online"
echo "computer_url=http://localhost:8000"
echo "phone_url=https://${LAN_IP}:8443"
echo "certificate_url=http://${LAN_IP}:8080/local-ca.crt"
echo "phone_certificate=$ROOT_DIR/instance/certs/potiguar-local-ca.crt"
echo "phone_setup=Antes do primeiro login, baixe e instale o certificado CA; depois use somente o phone_url HTTPS."
