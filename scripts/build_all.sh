#!/usr/bin/env bash
# ============================================================
# build_all.sh —— 批量编译 handwritten/ 下的所有步骤
#
# 用法（仓库根目录）：
#   bash scripts/build_all.sh                # 三条线、全部已有步骤
#   bash scripts/build_all.sh vins           # 只编 vins
#   bash scripts/build_all.sh vins 4         # 只编 vins 的 step4
#
# 有 CMakeLists.txt 走 cmake；否则用 g++ + pkg-config opencv4 直编。
# ============================================================

set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRACK_FILTER="${1:-}"
STEP_FILTER="${2:-}"

cd "$REPO_DIR" || exit 1

if ! pkg-config --exists opencv4 2>/dev/null; then
    echo "[警告] pkg-config 找不到 opencv4，g++ 直编的分支会失败。"
    echo "       确认已安装: sudo apt install -y libopencv-dev"
    echo
fi

fail=0
built=0

for track_dir in handwritten/*/; do
    track="$(basename "$track_dir")"
    [ "$track" = "results" ] && continue
    [ -n "$TRACK_FILTER" ] && [ "$TRACK_FILTER" != "$track" ] && continue

    for step_dir in "$track_dir"step*/; do
        [ -d "$step_dir" ] || continue
        step="$(basename "$step_dir")"
        [ -n "$STEP_FILTER" ] && [ "$STEP_FILTER" != "${step#step}" ] && continue

        echo "==================== $track/$step ===================="

        if [ -f "$step_dir/CMakeLists.txt" ]; then
            mkdir -p "$step_dir/build"
            if ( cd "$step_dir/build" && cmake .. >/dev/null && make ); then
                built=$((built + 1))
            else
                echo "[失败] $track/$step"
                fail=$((fail + 1))
            fi
        else
            cpp="$(find "$step_dir" -maxdepth 1 -name '*.cpp' | head -1)"
            if [ -z "$cpp" ]; then
                echo "[跳过] $track/$step 无源码"
                continue
            fi
            mkdir -p "$step_dir/build"
            out="$step_dir/build/$(basename "${cpp%.cpp}")"
            if g++ -std=c++11 -O2 "$cpp" -o "$out" $(pkg-config --cflags --libs opencv4); then
                built=$((built + 1))
            else
                echo "[失败] $track/$step"
                fail=$((fail + 1))
            fi
        fi
    done
done

echo
echo "编译成功 $built 个步骤，失败 $fail 个。"
if [ "$fail" -gt 0 ]; then
    echo "注意：make 失败时 build/ 里可能还留着旧二进制，运行前务必确认输出里有 Built target。"
fi
