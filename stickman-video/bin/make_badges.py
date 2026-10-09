#!/usr/bin/env python3
"""Generate keyword badge PNGs (transparent bg) in two styles.

Usage: make_badges.py <output_dir> <badges.json>
  badges.json: [["text", style], ...]  style 1 = explosion starburst
  (harsh/impact words), style 2 = cloud (warm/healing words).
  Output files: badge01.png, badge02.png, ...

Proven in production (2026-10-01). Font: Noto Sans CJK SC Bold via fc-match.
"""
import json
import math
import os
import random
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def font_path():
    r = subprocess.run(["fc-match", "-f", "%{file}\n", "Noto Sans CJK SC:bold"],
                       capture_output=True, text=True)
    p = r.stdout.strip()
    if p and os.path.exists(p):
        return p
    raise RuntimeError("CJK bold font not found")


FONT_FILE = font_path()


def get_font(size):
    return ImageFont.truetype(FONT_FILE, size)


def starburst_points(cx, cy, rx, ry, spikes=16, jitter_seed=7):
    pts = []
    rnd = random.Random(jitter_seed)  # deterministic, organic manga look
    jr = [rnd.uniform(0.92, 1.04) for _ in range(spikes)]
    for i in range(spikes * 2):
        ang = math.pi * i / spikes - math.pi / 2
        if i % 2 == 0:
            px, py = rx * jr[i // 2], ry * jr[i // 2]
        else:
            px, py = rx * 0.68, ry * 0.68
        pts.append((cx + px * math.cos(ang), cy + py * math.sin(ang)))
    return pts


def cloud_ellipses(W, H):
    cx, cy = W / 2, H / 2
    e = []
    n = 7
    for i in range(n):
        t = i / (n - 1)
        x = W * 0.18 + t * W * 0.64
        r = H * (0.30 + 0.10 * math.sin(t * math.pi))
        e.append((x - r * 1.25, cy - r, x + r * 1.25, cy + r))
    e.append((W * 0.32, H * 0.08, W * 0.52, H * 0.52))
    e.append((W * 0.50, H * 0.06, W * 0.70, H * 0.50))
    return e


def make_badge(text, style, out_path, fs=64, outline=7):
    font = get_font(fs)
    l, t, r, b = font.getbbox(text)
    tw, th = r - l, b - t

    if style == 1:
        rx_in, ry_in = tw / 2 + 36, th / 2 + 30
        rx_out, ry_out = rx_in / 0.66, ry_in / 0.66
        W = int(rx_out * 2 + outline * 2 + 10)
        H = int(ry_out * 2 + outline * 2 + 10)
    else:
        pad_x, pad_y = 96, 72
        W, H = int(tw + pad_x * 2), int(th + pad_y * 2)

    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    if style == 1:
        md.polygon(starburst_points(W / 2, H / 2, rx_out, ry_out), fill=255)
    else:
        for e in cloud_ellipses(W, H):
            md.ellipse(e, fill=255)

    k = outline * 2 + 1
    dil = mask.filter(ImageFilter.MaxFilter(k))

    badge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    white = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    badge.paste(black, (0, 0), dil)
    badge.paste(white, (0, 0), mask)

    d2 = ImageDraw.Draw(badge)
    d2.text((W / 2, H / 2), text, font=font, fill=(0, 0, 0, 255), anchor="mm")
    badge.save(out_path)
    print("saved", out_path, badge.size)


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    out_dir, json_path = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    with open(json_path) as f:
        badges = json.load(f)
    for i, (text, style) in enumerate(badges, start=1):
        make_badge(text, style, os.path.join(out_dir, f"badge{i:02d}.png"))


if __name__ == "__main__":
    main()
