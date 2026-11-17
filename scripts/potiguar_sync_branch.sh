#!/usr/bin/env bash
# Potiguar: sincronização segura e verificável de branch de trabalho.
# Usa somente fast-forward; jamais força push, faz merge ou altera produção.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mode="${1:---check}"
if [[ "$mode" != "--check" && "$mode" != "--push" ]]; then
  echo "Uso: $0 --check|--push" >&2;exit 2
fi
branch=$(git symbolic-ref --quiet --short HEAD) || { echo "HEAD destacado" >&2;exit 2; }
if [[ "$branch" == main && "$mode" == "--push" ]]; then
  echo "main é produção; promoção apenas via PR e aprovação humana" >&2;exit 2
fi
git fetch --prune origin
if [[ -n "$(git status --porcelain)" ]]; then
  echo "WORKTREE_DIRTY: faça commit ou preserve as alterações antes de sincronizar" >&2
  git status --short;exit 3
fi
head=$(git rev-parse HEAD)
if git show-ref --verify --quiet "refs/remotes/origin/$branch";then
  upstream="origin/$branch"
  read -r behind ahead < <(git rev-list --left-right --count "$upstream...HEAD")
  if (( behind > 0 )); then
    echo "BRANCH_BEHIND: $behind commits do GitHub; reconciliar sem force-push" >&2
    exit 4
  fi
else
  ahead="unpublished"
fi
if [[ "$mode" == "--push" ]];then
  git push --set-upstream origin "HEAD:refs/heads/$branch"
fi
remote=$(git ls-remote --heads origin "$branch" | awk '{print $1}')
printf 'branch=%s\nlocal=%s\nremote=%s\nmode=%s\n' "$branch" "$head" "${remote:-missing}" "$mode"
if [[ -z "$remote" || "$remote" != "$head" ]];then
  echo "NOT_SYNCED: commit local diferente do remoto" >&2
  exit 5
fi
echo 'SYNC_VERIFIED'
