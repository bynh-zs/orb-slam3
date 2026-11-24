#!/usr/bin/env bash
# ============================================================
# collect.sh —— 把工作机上的手写代码与产物同步进本仓库
#
# 用法（在工作机 Ubuntu 上执行，仓库目录内）：
#   bash scripts/collect.sh                       # 用默认路径与自动探测
#   bash scripts/collect.sh --vins ~/vins/1steps --mono ~/slam/1steps
#
# 三条线：vins / mono / stereo
#   - 源码（*.cpp *.h *.hpp CMakeLists.txt *.sh）→ handwritten/<线>/stepN/
#   - 产物（*.png *.jpg *.txt *.csv，排除 CMakeLists.txt）
#                                               → handwritten/<线>/results/stepN/
#   - 完成后 git add + git commit（不 push，push 由你自己执行）
# ============================================================

set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

VINS_SRC="${VINS_SRC:-}"
MONO_SRC="${MONO_SRC:-}"
STEREO_SRC="${STEREO_SRC:-}"

while [ $# -gt 0 ]; do
    case "$1" in
        --vins)   VINS_SRC="${2:-}";   shift 2 ;;
        --mono)   MONO_SRC="${2:-}";   shift 2 ;;
        --stereo) STEREO_SRC="${2:-}"; shift 2 ;;
        --help|-h)
            echo "用法: bash scripts/collect.sh [--vins PATH] [--mono PATH] [--stereo PATH]"
            exit 0 ;;
        *) echo "[警告] 未知参数: $1（已忽略）"; shift ;;
    esac
done

# ---------- 默认路径与自动探测 ----------
[ -z "$VINS_SRC" ] && [ -d "$HOME/vins/1steps" ] && VINS_SRC="$HOME/vins/1steps"

if [ -z "$MONO_SRC" ] || [ -z "$STEREO_SRC" ]; then
    while IFS= read -r d; do
        case "$d" in
            */vins/*|*/vins) continue ;;
        esac
        base="$(echo "$d" | tr '[:upper:]' '[:lower:]')"
        if [ -z "$MONO_SRC" ]; then
            case "$base" in
                *mono*|*单目*) MONO_SRC="$d"; continue ;;
            esac
        fi
        if [ -z "$STEREO_SRC" ]; then
            case "$base" in
                *stereo*|*双目*|*binoc*) STEREO_SRC="$d" ;;
            esac
        fi
    done < <(find "$HOME" -maxdepth 4 -type d -name '1steps' 2>/dev/null)
fi

echo "仓库目录 : $REPO_DIR"
echo "vins     : ${VINS_SRC:-（未找到，跳过）}"
echo "mono     : ${MONO_SRC:-（未找到，跳过）}"
echo "stereo   : ${STEREO_SRC:-（未找到，跳过）}"
echo

copy_track() {
    local track="$1" src_root="$2"
    [ -n "$src_root" ] || return 0
    if [ ! -d "$src_root" ]; then
        echo "[跳过] $track：目录不存在 $src_root"
        return 0
    fi

    local found=() n d
    for n in $(seq 1 12); do
        d="$src_root/step$n"
        [ -d "$d" ] || continue
        found+=("step$n")

        mkdir -p "$REPO_DIR/handwritten/$track/step$n" \
                 "$REPO_DIR/handwritten/$track/results/step$n"

        # 源码：只取该步目录顶层，不进入 build/
        while IFS= read -r -d '' f; do
            cp -f "$f" "$REPO_DIR/handwritten/$track/step$n/"
        done < <(find "$d" -maxdepth 1 -type f \
                 \( -name '*.cpp' -o -name '*.h' -o -name '*.hpp' \
                    -o -name 'CMakeLists.txt' -o -name '*.sh' \) -print0)

        # 产物：图 + 数值结果
        while IFS= read -r -d '' f; do
            cp -f "$f" "$REPO_DIR/handwritten/$track/results/step$n/"
        done < <(find "$d" -maxdepth 1 -type f \
                 \( -name '*.png' -o -name '*.jpg' -o -name '*.txt' -o -name '*.csv' \) \
                 ! -name 'CMakeLists.txt' -print0)
    done

    if [ ${#found[@]} -eq 0 ]; then
        echo "[跳过] $track：$src_root 下没有 stepN 目录"
    else
        echo "[完成] $track：${found[*]}"
    fi
}

copy_track vins   "$VINS_SRC"
copy_track mono   "$MONO_SRC"
copy_track stereo "$STEREO_SRC"

# ---------- git ----------
if ! command -v git >/dev/null 2>&1; then
    echo
    echo "[提示] 未安装 git。先执行: sudo apt install -y git"
    exit 0
fi

cd "$REPO_DIR" || exit 1

if ! git config user.email >/dev/null 2>&1; then
    git config user.name  "slam-lab"
    git config user.email "slam@localhost"
    echo
    echo "[提示] 未检测到 git 身份，已为本仓库设置临时身份。"
    echo "       用自己的身份: git config user.name '你的名字'; git config user.email '你的邮箱'"
fi

git add -A

if git diff --cached --quiet; then
    echo
    echo "没有变化，跳过提交。"
else
    git commit -q -m "sync: $(date '+%Y-%m-%d %H:%M') 同步手写代码与产物"
    echo
    echo "已提交: $(git log -1 --oneline)"
fi

echo
echo "下一步（推送由你自己执行）:  git push"
