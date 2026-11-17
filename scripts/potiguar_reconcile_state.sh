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
if command -v curl >/dev/null;then
 curl -sSk --max-time 10 -o /dev/null -w 'Vercel HTTP %{http_code}\n' https://potiguar-v2-demo.vercel.app/admin/copilot || echo 'Vercel not reachable'
fi
echo 'DISK';df -h . |tail -1
echo 'CHECK_RESULT'
if test "$branch" != develop || test "$local_head" != "$dev_head" || test -n "$(git status --porcelain)";then
 echo 'BLOCKED: use clean synchronized develop';exit 3
fi
echo 'PASS: clean develop synchronized to GitHub'
