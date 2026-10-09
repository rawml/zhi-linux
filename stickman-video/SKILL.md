---
name: "stickman-video"
description: "Produce a complete 16:9 stickman emotional-copy short video from a theme line: viral copy rewrite, fixed-voice narration, storyboard stills, image-to-video animation, keyword badges, assembly, QC, and a publishing kit. Trigger when the user asks to make/produce a stickman video (e.g. 开始制作, 再做一个, 做一条火柴人视频)."
---

# Stickman Video

## Purpose
Turn one theme line into a finished, QC'd stickman emotional-copy short film
(~30–45s, 16:9, 1920×1080, 30fps, H.264+AAC) with a publishing kit, at the
quality bar of the established series.

## Division of labor (user preference — do not override)
- **Default:** deliver only director-style storyboard prompts + publishing kit.
  The user generates frames with their own tools and assembles themselves.
- **Full production:** only when the user explicitly asks (e.g. 开始制作 /
  再做一个 in a production context). Then run all 8 steps below.

## Workflow
1. **文案改写** — see `references/copywriting.md`. Rewrite the theme into
   ~130–150 chars of viral copy, split into 8 scenes. Never copy the source
   phrasing verbatim.
2. **旁白 TTS** — one mp3 per scene via the `tts` skill:
   `--voice avocado_v2:MAI_01 --language zh`, Warm Chinese female voice.
   Fixed for series consistency. Save as `audio/narrNN.mp3`.
3. **分镜静帧** — `media.generate_image`, 2048×1152 PNG, using the user's
   male/female character reference images as input. See
   `references/production.md` for style rules and the negative prompt.
4. **图生视频** — `media.generate_video` per still, ~10s each. Verify REAL
   motion (compare t=1s vs t=6s frames); no pure push/zoom/pan. See
   `references/production.md` for the known pitfalls and fixes.
5. **关键词徽章** — `bin/make_badges.py`: style 1 (explosion bubble) for
   harsh/impact words, style 2 (cloud) for warm/healing words.
6. **组装** — `bin/assemble.py <project_dir> <name>`: trims each clip to
   narration+0.5s, overlays badge, concats, muxes narration (each padded with
   0.5s silence to prevent A/V drift). See `references/assembly.md`.
7. **质检** — `references/assembly.md` checklist: resolution, fps, codecs,
   duration, no subtitle burn-in, badges legible and not covering characters,
   characters consistent, no drift.
8. **交付** — copy final mp4 to `~/workspace/your_files/` with a descriptive
   name; write the publishing kit (3 viral titles, tags, BGM pick, 3
   comment-bait lines) — template in `references/publishing.md`.

## Operating Rules
1. **风格铁律**：简约线条火柴人 (round head, dot eyes, thin limbs, flat
   color blocks, black outlines). 严禁写实化/真人化/动漫化/3D化. Every
   image/video prompt carries the negative:
   `photorealistic, real person, photograph, realistic anatomy, detailed hands, 3d render, cinematic realism`.
2. **人物一致**：always use the user's designated male/female reference
   images as generation input. Girl: red knit pom-pom hat + loose yellow
   T-shirt. Boy: red "H" beanie + yellow top + gray work pants + red-black
   shoes.
3. **开头3秒强钩子**：scene 1 must grab attention (conflict, contrast,
   close-up); never a bland establishing shot.
4. **画面饱满是铁律**：每张静帧提示词必须写满[环境+道具+光影色调+机位]
   （模板和反例见 `references/production.md` 第3节），只写人物动作会导致
   白背景——这是最常见的翻车点，目检时把"背景非空白"作为硬性项。
5. **不压旁白全文字幕**：user adds subtitles in CapCut themselves.
6. **徽章混合使用**：否定/打压/冲击 → 1号爆炸气泡；温暖/治愈/收尾 → 2号云朵。
7. **每镜时长 = 旁白时长 + 0.5秒**，旁白尾部补 0.5s 静音 — this is what
   prevents cumulative A/V drift. Never skip it.
8. **诚实质检**：report what was blocked, what was retried, and what the fix
   was. Deliver the film only after the checklist passes.
9. When the user questions the method and says stop: stop everything,
   explain the approach, then continue only after they confirm.
