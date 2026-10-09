#!/usr/bin/env bash
# Fish Audio 配音一行调用（自动走免费档 s2.1-pro-free）。
# 认证经 authd surrogate 交换自动注入，无需手动传 key。
#
# 用法：
#   speak.sh "旁白文案" 温柔动听女声 narration.mp3
#   speak.sh --speed 1.1 "旁白文案" AD学姐 narration.mp3
#
# 音色映射（voice id 在下方 VOICE_IDS 里填）。
# 选音色流程（skill 要求）：先用 muse.create_options 让用户选 5 个之一，
# 不要自己默认选定。

set -euo pipefail

SPEED="1.0"
if [[ "${1:-}" == "--speed" ]]; then
  SPEED="$2"; shift 2
fi

if [[ $# -ne 3 ]]; then
  echo "用法: speak.sh [--speed 0.5-2.0] \"旁白文案\" <音色名> <输出mp3>"
  echo "可用音色：AD学姐 / 贾小军 / 温柔动听女声 / 宣传片大气浑厚 / 女大学生"
  exit 2
fi

TEXT="$1"; VOICE_NAME="$2"; OUT="$3"

# ---- 音色名 -> Fish Audio voice id 映射（2026-10-08 按名查公用库，取首个同名结果）----
declare -A VOICE_IDS=(
  ["AD学姐"]="7f92f8afb8ec43bf81429cc1c9199cb1"
  ["贾小军"]="80cf680e668c44fc8d5795f80d903f7a"
  ["温柔动听女声"]="faccba1a8ac54016bcfc02761285e67f"
  ["宣传片大气浑厚"]="aa585dc793fe4dd5bcfd891e3cbd2416"
  ["女大学生"]="5c353fdb312f4888836a9a5680099ef0"
)

VOICE_ID="${VOICE_IDS[$VOICE_NAME]:-}"
if [[ -z "$VOICE_ID" ]]; then
  if [[ -z "${VOICE_IDS[$VOICE_NAME]+x}" ]]; then
    echo "ERROR: 未知音色 '$VOICE_NAME'。可用：${!VOICE_IDS[*]}" >&2
  else
    echo "ERROR: 音色 '$VOICE_NAME' 的 voice id 还没填（用 GET https://api.fish.audio/model 按名字查 id 填入本文件）。" >&2
  fi
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/../../fish-audio/bin/tts.py" \
  --text "$TEXT" \
  --reference-id "$VOICE_ID" \
  --output "$OUT" \
  --speed "$SPEED"
