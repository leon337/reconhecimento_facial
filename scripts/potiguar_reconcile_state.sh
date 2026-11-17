#!/usr/bin/env bash
# Reconciliação sem alterações de aplicação ou deploy.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
git fetch --prune origin >/dev/null
local_head="$(git rev-parse HEAD)"
dev_head="$(git rev-parse origin/develop)"
prod_head="$(git rev-parse origin/main)"
branch="$(git branch --show-current)"
printf 'branch=%s\nlocal_sha=%s\ndevelop_sha=%s\nmain_sha=%s\n' "$branch" "$local_head" "$dev_head" "$prod_head"
printf 'ahead_behind_develop=';git rev-list --left-right --count HEAD...origin/develop
printf 'worktree_dirty_count=';git status --porcelain |wc -l
echo 'GIT_WORKTREES';git worktree list
echo 'OPEN_GITHUB_PRS'
if command -v gh >/dev/null;then
 gh pr list -R leon337/reconhecimento_facial --state open --limit 100 --json number,headRefName,baseRefName,isDraft --jq '.[]|[.number,.headRefName,.baseRefName,.isDraft]|@tsv'
else echo 'gh CLI unavailable: PRs not checked';fi
echo 'PUBLIC_SYNTHETIC_DEMO'
command -v curl >/dev/null || { echo 'BLOCKED: curl unavailable';exit 4; }
headers="$(mktemp)"
trap 'rm -f "$headers"' EXIT
http="$(curl -sSL --max-time 12 -D "$headers" -o /dev/null -w '%{http_code}' https://potiguar-v2-demo.vercel.app/admin/copilot)" || { echo 'BLOCKED: Vercel unreachable';exit 4; }
printf 'Vercel HTTP %s\n' "$http"
if test "$http" != 200 || ! grep -qi '^x-potiguar-demo: synthetic-no-login' "$headers";then
 echo 'BLOCKED: Vercel synthetic-demo gate invalid';exit 4
fi
echo 'DISK';df -h . |tail -1
free_kib="$(df -Pk . |awk 'NR==2 {print $4}')"
if test "$free_kib" -lt 3145728;then
 echo 'BLOCKED: less than 3 GiB free for builds';exit 5
fi
echo 'CHECK_RESULT'
if test "$branch" != develop || test "$local_head" != "$dev_head" || test "$(git rev-parse main)" != "$prod_head" || test -n "$(git status --porcelain)";then
 echo 'BLOCKED: local branches or worktree diverged from GitHub';exit 3
fi
echo 'PASS: clean develop/main, synthetic Vercel and disk preflight'
