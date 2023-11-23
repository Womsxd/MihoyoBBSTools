#!/usr/bin/bash

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 切换目录
AA_DIR0="$SCRIPT_DIR/mhylogin"
cd "$AA_DIR0" || exit 1

echo "Current directory: $(pwd)"
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit."
else
    git add .
    git commit -m "Update by bash"
    git push origin main
    echo "Done."
fi

##########
# 等待 30 秒
sleep 30s
# 切换目录2
AA_DIR1="$SCRIPT_DIR"
cd "$AA_DIR1" || exit 1
echo "Current directory: $(pwd)"

if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit."
else
    git add .
    git commit -m "Update by bash"
    git push origin master
    echo "Done."
fi
