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

LAN_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo "status=online"
echo "computer_url=http://localhost:8000"
if [[ -n "$LAN_IP" ]]; then
  echo "phone_url=http://${LAN_IP}:8000"
fi
