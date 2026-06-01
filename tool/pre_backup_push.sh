#!/bin/bash
# 备份前检查点提交 + 推送
# 优先使用 Windows 侧 Git 凭据链路
set -e

MESSAGE="${1:-chore: pre-backup checkpoint}"

echo "=== 备份前检查点推送 ==="
echo "提交信息: $MESSAGE"

# Stage all changes
git add -A

# Only commit if there are staged changes
if git diff --cached --quiet; then
  echo "没有需要提交的更改"
else
  git commit -m "$MESSAGE"
  echo "已提交"
fi

# Push using Windows Git (cmd.exe) to use Windows credential manager
if command -v cmd.exe &>/dev/null; then
  echo "使用 Windows Git 推送..."
  cmd.exe /c "git push origin main 2>&1"
else
  git push origin main
fi

echo "=== 推送完成 ==="
