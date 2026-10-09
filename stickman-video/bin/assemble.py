#!/usr/bin/env python3
"""Generic assembly for stickman emotional-copy videos.

Usage: assemble.py <project_dir> <final_name>

Expected layout:
  <project_dir>/anim/animNN.mp4     (N = 1..scenes, ~10s each)
  <project_dir>/audio/narrNN.mp3    (per-scene narration)
  <project_dir>/badges/badgeNN.png   (transparent keyword badges)

Output: <project_dir>/output/final_<final_name>.mp4
  1920x1080, 30fps, H.264 + AAC. Each scene = narration + 0.5s;
  narration padded with 0.5s silence to prevent cumulative A/V drift.

Proven in production (2026-10-01, 《不要用善良，去惯着得寸进尺的人》).
"""
import json
import os
import subprocess
import sys


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd[:12]))
        print(r.stderr[-2000:])
        sys.exit(1)
    return r


def probe_dur(path):
    r = run(["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "csv=p=0", path])
    return float(r.stdout.strip())


def count_scenes(audio_dir):
    n = 0
    while os.path.exists(os.path.join(audio_dir, f"narr{n + 1:02d}.mp3")):
        n += 1
    return n


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    D, name = sys.argv[1], sys.argv[2]
    ANIM = os.path.join(D, "anim")
    AUDIO = os.path.join(D, "audio")
    BADGES = os.path.join(D, "badges")
    ASEG = os.path.join(D, "anim_segments")
    OUT = os.path.join(D, "output")
    os.makedirs(ASEG, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    scenes = count_scenes(AUDIO)
    if scenes == 0:
        print("no narrNN.mp3 found in", AUDIO)
        sys.exit(1)

    vseg, aseg = [], []
    for i in range(1, scenes + 1):
        need = round(probe_dur(os.path.join(AUDIO, f"narr{i:02d}.mp3")) + 0.5, 2)
        src = os.path.join(ANIM, f"anim{i:02d}.mp4")
        badge = os.path.join(BADGES, f"badge{i:02d}.png")
        assert os.path.exists(src), f"missing anim clip {i}"
        assert os.path.exists(badge), f"missing badge {i}"
        vout = os.path.join(ASEG, f"cseg{i:02d}.mp4")
        aout = os.path.join(ASEG, f"cseg{i:02d}.m4a")
        fc = ("[0:v]scale=1920:1080:force_original_aspect_ratio=increase,"
              "crop=1920:1080,fps=30[base];"
              "[base][1:v]overlay=x=(W-w)/2:y=54:format=auto[v]")
        run(["ffmpeg", "-y", "-i", src, "-i", badge, "-filter_complex", fc,
             "-map", "[v]", "-t", f"{need:.3f}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", "-r", "30", "-an", vout])
        vseg.append(vout)
        run(["ffmpeg", "-y", "-i", os.path.join(AUDIO, f"narr{i:02d}.mp3"),
             "-af", "apad=pad_dur=0.5", "-t", f"{need:.3f}",
             "-c:a", "aac", "-b:a", "160k", aout])
        aseg.append(aout)
        print(f"scene {i:02d} done ({need:.2f}s)")

    vlst = os.path.join(ASEG, "vlist.txt")
    with open(vlst, "w") as f:
        for s in vseg:
            f.write(f"file '{s}'\n")
    silent = os.path.join(OUT, "silent_video.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", vlst, "-c", "copy", silent])

    alst = os.path.join(ASEG, "alist.txt")
    with open(alst, "w") as f:
        for s in aseg:
            f.write(f"file '{s}'\n")
    narr = os.path.join(OUT, "narration_full.m4a")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", alst, "-c", "copy", narr])

    final = os.path.join(OUT, f"final_{name}.mp4")
    run(["ffmpeg", "-y", "-i", silent, "-i", narr,
         "-c:v", "copy", "-c:a", "copy",
         "-shortest", "-movflags", "+faststart", final])
    print("FINAL:", final)
    print("video dur:", probe_dur(final))


if __name__ == "__main__":
    main()
