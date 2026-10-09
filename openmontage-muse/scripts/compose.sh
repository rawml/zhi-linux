#!/usr/bin/env bash
# OpenMontage-Muse 合成脚本（ffmpeg）：
#   按分镜顺序拼接视频片段 -> 混入旁白音轨 -> 可选叠加 srt 字幕 -> 输出终版 mp4。
#
# 用法：
#   compose.sh <assets_dir> <输出mp4> [字幕.srt]
#
# assets_dir 约定：
#   clip-01.mp4, clip-02.mp4, ...   视频片段（按文件名排序拼接）
#   narration.mp3                   旁白音轨（可选；没有就只拼画面）
#
# 行为：
#   - 片段统一转码为 1920x1080/30fps/H.264 再拼接，保证衔接无缝
#   - 有旁白时用 -shortest 对齐（画面总长向旁白看齐，按 skill 管线第 5 步）
#   - 有 srt 时用 libass 烧录字幕
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "用法: compose.sh <assets_dir> <输出mp4> [字幕.srt]"
  exit 2
fi

ASSETS="$1"; OUT="$2"; SRT="${3:-}"
NARR="$ASSETS/narration.mp3"

mapfile -t CLIPS < <(ls "$ASSETS"/clip-*.mp4 2>/dev/null | sort)
if [[ ${#CLIPS[@]} -eq 0 ]]; then
  echo "ERROR: $ASSETS 下没有 clip-*.mp4" >&2
  exit 2
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# 1) 片段逐个标准化（1080p/30fps/H.264/AAC），写 concat 列表
: > "$TMP/list.txt"
i=0
for c in "${CLIPS[@]}"; do
  i=$((i+1))
  n="$TMP/seg-$(printf '%02d' $i).mp4"
  ffmpeg -hide_banner -loglevel error -y -i "$c" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30" \
    -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 128k "$n"
  echo "file '$n'" >> "$TMP/list.txt"
done

# 2) 拼接
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$TMP/list.txt" \
  -c copy "$TMP/joined.mp4"

# 3) 混入旁白（有旁白时 -shortest 对齐）
if [[ -f "$NARR" ]]; then
  ffmpeg -hide_banner -loglevel error -y -i "$TMP/joined.mp4" -i "$NARR" \
    -c:v copy -c:a aac -b:a 160k -shortest "$TMP/mixed.mp4"
  SRC="$TMP/mixed.mp4"
else
  echo "WARN: 没有 $NARR，只拼画面" >&2
  SRC="$TMP/joined.mp4"
fi

# 4) 可选烧录字幕（libass）
if [[ -n "$SRT" ]]; then
  if [[ ! -f "$SRT" ]]; then echo "ERROR: 字幕文件不存在: $SRT" >&2; exit 2; fi
  ffmpeg -hide_banner -loglevel error -y -i "$SRC" \
    -vf "subtitles='$SRT'" -c:a copy "$OUT"
else
  cp "$SRC" "$OUT"
fi

DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")"
echo "OK: $OUT (${DUR}s)"
