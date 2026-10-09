# Style Catalog: Visual Styles & Prompt Formulas

This catalog defines the supported visual styles for `directing-stickman-videos`, including character DNA locks, environment specifications, motion pacing, and negative constraints.

---

## 1. Style Matrix Overview

| Style Key | Style Name | Visual Theme | Best For | Character Design |
|---|---|---|---|---|
| **Style 1** | Classic Minimalist (Light / Dark) | Pure white or black canvas, monochrome lines, up to 3 saturated accent colors | High-density explainers, pure logic, mental models, fast-paced cognitive concepts | Faceless, clothes-free, hollow circle head, uniform line weight |
| **Style 2A** | Modern Beanie - Studio Tech (极简科技风) | Pure white high-key studio, subtle light-gray perspective grid, glowing cyan/blue glass UI | Tech tutorials, AI tool breakdowns, career insights, methodology breakthroughs | Red beanie (no pom-pom), yellow t-shirt, black stick limbs, smooth 2D animation |
| **Style 2B** | Modern Beanie - Cinematic Story (彩色故事风) | Full-color narrative environments, cinematic lighting & depth (warm room, dusk, desert, summit) | Emotional storytelling, personal growth, motivational journeys, narrative hooks | Same red beanie & yellow t-shirt figure staged inside rich environmental lighting |

---

## 2. Style 1: Classic Minimalist

### Polarity & Background
- **Light Theme**: Flat, uniform, digitally pure-white canvas. Strictly forbid gray tint, paper texture, gradients, shadows, lighting, bloom, fog, or 3D depth.
- **Dark Theme**: Flat, uniform, pitch-black canvas. Pure white line art with high-contrast accent colors.

### Character DNA
```text
A minimalist 2D stick figure with a hollow circular head, no facial features, no hair, no clothing, no filled body, uniform medium line weight.
```

### Palette Contract
- Maximum of three saturated accent colors named with ordinary words (e.g., vivid red, electric blue, warm gold).
- No technical color notations (hex, RGB, Pantone).

---

## 3. Style 2: Modern Beanie Zeke

### Character DNA Anchors (Anti-Deformation Lock)

To prevent character drift, bug-eye deformations, or clothing loss across clips, use these exact character anchors:

**Clip 1 Character Anchor:**
```text
A minimalist 2D animated stick figure wearing a bright red beanie (smooth rounded knit, no pom-pom) and a yellow t-shirt, with simple black stick limbs and shorts. Simple black lines, vibrant colors, smooth 2D animation style.
```

**Subsequent Clips Character Anchor (Clips 2–6):**
```text
The same minimalist 2D animated stick figure in a bright red beanie and yellow shirt... Simple black lines, vibrant colors, smooth 2D animation style.
```

**Deformation Prevention Rules:**
- **No Realistic Facial Features**: Hollow circular head or minimal dot eyes only. Never request detailed pupils, irises, or photorealistic facial contours (which trigger alien bug-eyes).
- **No Pom-Poms**: Specify smooth rounded beanie top to prevent erratic pom-poms or winter tassels.
- **Always Include Both Beanie and T-shirt**: Omitting the shirt results in naked stick bodies; omitting the beanie results in standard Style 1 characters.

---

### Sub-Style 2A: Modern Studio Tech (极简科技风)

**In Plain Language**: Apple 发布会式极简科技风。纯白亮面高光空间 + 极淡浅灰透视地砖网格 + 悬浮青蓝半透明玻璃 UI/微光质感。

#### Environment Specification
```text
in a modern bright white studio space with subtle light-gray perspective grid lines on the floor plane. High-key studio lighting, clean white negative space, sleek glowing cyan and electric blue glass holographic UI elements.
```

#### Mandatory Negative Constraints (Anti-Clutter)
Without explicit negative constraints, diffusion models tend to generate motherboard circuitry, spaceship corridors, and cracked concrete. **Always append this negative clause in 2A prompts:**
```text
Negative constraints: strictly minimalist studio aesthetic, no circuit board textures, no sci-fi wall panels, no spaceship corridors, no cracked concrete, no grunge textures, no photorealistic human skin, no speech bubbles, no dialogue text boxes.
```

#### Motion Dynamics (Anti-Stutter & Anti-Lag)
- **Do not use abstract liquid/morphing transformations** (e.g., stairs melting into a clock), which trigger latent flicker and stuttering.
- **Use physical, character-driven interactions**:
  - Leaping and bumping an invisible glass ceiling with a comedic bounce.
  - Tapping a sneaker onto the floor grid to emit an expanding cyan ripple wave.
  - Pulling out a glowing light-pen to draw a crisp luminous line bridge across an abyss.
  - Touching a sleek floating glass panel to reveal an icon-only illuminated lock.
  - Pushing open a heavy minimalist vault door to step forward into bright horizon light.
- **Pacing**: Every 10-second clip must feature distinct actions across `[0–3s]`, `[3–7s]`, and `[7–10s]`. Never let the character stand idle or stare at the camera for multiple seconds.

---

### Sub-Style 2B: Cinematic Story (彩色故事风)

**In Plain Language**: Pixar 故事短片风。全彩沉浸式场景（暖光台灯卧室、黄昏窗前、荒野公路、云端山顶）+ 电影叙事光影。

#### Environment Specification
```text
in a rich full-color cinematic environment [describe setting: e.g., a dimly lit cozy bedroom with warm lamplight / a vast open desert highway under a glowing dusk sky / a dramatic mountain ridge above rolling golden clouds]. Cinematic volumetric lighting, soft depth of field, atmospheric narrative mood.
```

#### Character & Style Consistency
- The character remains the same minimalist 2D stick figure in red beanie and yellow shirt.
- Maintain smooth 2D vector animation aesthetics for the character even within a textured, atmospheric background.

#### Negative Constraints
```text
Negative constraints: no photorealistic human skin or faces, no 3D humanoid CGI uncanny valley models, no chaotic line glitches, no speech bubbles, no dialogue text boxes.
```

---

## 4. Universal Audio Continuity Contract

Independent text-to-video clips will generate random voices and disjointed music unless explicitly locked. Every prompt in a package must follow this dual-lock formula:

### Narrator Voice Lock
```text
Identical narrator: confident, articulate, warm young adult American male voice, natural conversational storytelling tone, voice-first mix, audio voiceover only, strictly no speech bubbles or dialogue boxes.
```
*(Can be adapted for female or older narrator, but must remain identical verbatim across all clips in the package).*

### BGM Continuity Lock
- **Clip 1**:
  ```text
  Audio: Voiceover clearly audible over quiet, thoughtful piano and subtle soft ambient synth, building gentle optimistic momentum.
  ```
- **Clips 2–6**:
  ```text
  Audio: Voiceover seamlessly continues the identical quiet, thoughtful piano and subtle soft ambient synth from clip 1, maintaining identical tempo, instrumentation, and optimistic narrative momentum. Synchronized crisp SFX on physical actions.
  ```

---

## 5. Visual Beat Pacing Template (10-Second Clip)

Every prompt must divide its 10 seconds into three active narrative beats:

```text
Timed Synchronized Visual Beats:
- [0–3s] (VO: "..."): [Setup / premise action — character enters, acts, or inherits momentum from previous clip]
- [3–7s] (VO: "..."): [Escalation / discovery — character interacts with environment or solves visual obstacle]
- [7–10s] (VO: "..."): [Climax & outgoing transition — character delivers payoff and initiates outgoing motion for next clip]
```
