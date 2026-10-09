# Omni Flash Production Prompt Contract

Use this contract only after explicit approval of the current Phase A. Refer to `references/style-catalog.md` for full style specifications and prompt blueprints.

## Production package order

Deliver these sections in order:

1. Global continuity block
2. N standalone English prompts (where N = target duration / 10; default 6 clips for 60s)
3. Stitching guide
4. Voice and music continuity note

## Global continuity block

State the chosen aspect ratio (`16:9` or `9:16`), target duration, selected visual style (Style 1 Classic, Style 2A Studio Tech, or Style 2B Cinematic Story), character anchor design, palette or environment definition, narrator identity, audio arc, and continuity strategy. Treat this block as a review summary; each prompt still repeats all critical locks.

## Standalone prompt order

Write every prompt in this order:

1. Output specification: approximately ten seconds, chosen aspect ratio (`16:9` or `9:16`), 720p target, 24 FPS, synchronized audio
2. Environment and background definition:
   - For Style 1 Light: flat, uniform, digitally pure-white canvas with no shading or 3D depth
   - For Style 1 Dark: flat, uniform, pitch-black canvas with pure white line art
   - For Style 2A (Studio Tech): modern bright white studio space with subtle light-gray perspective grid lines on the floor plane, high-key lighting, clean white negative space, sleek glowing cyan/blue glass elements
   - For Style 2B (Cinematic Story): rich full-color cinematic environment with volumetric lighting and depth of field
3. Character lock:
   - For Style 1: hollow circular head, no facial features, no hair, no clothing, no filled body, stable proportions, uniform medium line weight
   - For Style 2 (Modern Beanie Zeke):
     - First clip: `A minimalist 2D animated stick figure wearing a bright red beanie (smooth knit, no pom-pom) and a yellow t-shirt, with simple black stick limbs and shorts. Simple black lines, vibrant colors, smooth 2D animation style.`
     - Subsequent clips: `The same minimalist 2D animated stick figure in a bright red beanie and yellow shirt... Simple black lines, vibrant colors, smooth 2D animation style.`
4. Palette and accent roles (expressed only with ordinary color names, no hex or technical codes)
5. Composition strategy for the chosen ratio (`16:9` or `9:16`)
6. First-frame state inherited from the previous clip
7. `[0–3s]`, `[3–7s]`, and `[7–10s]` visual beats tied to spoken ideas
8. Exact audio-only English dialogue in quotation marks (strictly no speech bubbles or dialogue boxes)
9. Identical narrator description, emotion, and delivery across all clips
10. BGM, synchronized SFX, and voice-first mixing (subsequent clips mandate seamless BGM continuity from clip 1)
11. Final-frame transition state inherited by the next clip
12. Negative constraints (including style-specific clutter/deformation bans)

Make each prompt self-contained and usable without any external context.

## Style language

Use this wording to request density without character drift:

> rapid scene changes, kinetic motion-graphic transformations, and frequent visual events, while preserving an identical stick-figure design, constant line weight, and strict temporal consistency

Avoid `rapid style changes`, which can invite model changes to drawing style, line weight, or character design.

## Timed visual sequence & motion dynamics

Translate the approved storyboard row into three connected physical events:

- `[0–3s]`: establish or inherit the visual premise.
- `[3–7s]`: transform, escalate, or explain the metaphor through character action.
- `[7–10s]`: deliver a climax and create the next transition.

### Anti-Stutter & Anti-Lag Guidelines:
- Do not use abstract liquid or object shape morphing (e.g., stairs melting into a clock), as these cause diffusion latent jitter and frame drops.
- Drive motion with concrete character actions (leaping, touching glass, drawing luminous lines, opening heavy doors).
- Ensure continuous character engagement; never leave the character standing idle or staring at the camera for multiple seconds.

## Dialogue and visual text

Quote the approved English VO exactly once as audio-only dialogue:
```text
Audio voiceover only, strictly no speech bubbles, no dialogue boxes.
```
Instruct the model not to add, omit, paraphrase, repeat, reorder, caption, subtitle, or visually transcribe words.

Default every generated clip to no visible words, letters, numbers, captions, subtitles, interface copy, palette labels, production annotations, logos, or watermarks. Require icon-only message bubbles, content cards, clocks, meters, and notifications. Put optional approved phrases in a separate post-production overlay list outside the prompts.

## Palette notation

Use ordinary descriptive color names such as vivid red, electric blue, or warm gold. Never put hexadecimal, RGB, HSL, Pantone, or other technical color notation in a generation prompt. Models may reproduce prominent notation literally as unwanted interface text.

## Audio continuity contract

Independent text-to-video clips will generate random voices and disjointed music unless explicitly locked. Every prompt in a package must follow this dual-lock formula:

1. **Narrator Lock**: Repeat the identical narrator specification verbatim across all N prompts (e.g., `Identical narrator: confident, articulate, warm young adult American male voice, natural conversational storytelling tone, voice-first mix`).
2. **BGM Lock**:
   - Clip 1 establishes the musical theme.
   - Clips 2–N explicitly instruct the model: `Audio: Voiceover seamlessly continues the identical quiet, thoughtful piano and subtle soft ambient synth from clip 1, maintaining identical tempo, instrumentation, and optimistic narrative momentum. Synchronized crisp SFX on physical actions.`

## Negative contract

Forbid:

- photorealism and unwanted 3D humanoid rendering
- facial features (pupils, realistic eyes, lips) or hair unless approved
- extra limbs, malformed anatomy, disconnected lines, or changed proportions
- broken or changing line weight
- inverted theme polarity or unexplained colors
- unintended characters or irrelevant spectacle
- visible words, letters, numbers, technical color notation, palette labels, interface copy, captions, subtitles, logos, or watermarks
- altered, omitted, repeated, reordered, or added dialogue
- speech bubbles, comic dialog balloons, or visual text boxes
- **For Style 2A specifically**: `strictly minimalist studio aesthetic, no circuit board textures, no sci-fi wall panels, no spaceship corridors, no cracked concrete, no grunge textures`
- **For Style 2B specifically**: `no photorealistic human skin, no 3D humanoid CGI models, no chaotic line glitches`

## Stitching guide

List all N clips in order. For every cut, repeat the exact ending state and matching opening state. Include any trim, short audio crossfade, or match-cut note needed for assembly.

## Audio continuity note

Independent text-only generations may vary in voice and music. Recommend, in order:

1. Reuse the same voice or audio reference when the interface supports it.
2. Repeat the identical narrator description in every prompt.
3. For maximum consistency, generate synchronized SFX and add one continuous external English voiceover and BGM track during assembly.

## Phase B checks

- The user approved the current Phase A.
- Exactly N standalone prompts are present (matching approved Phase A duration).
- Each prompt repeats ratio (`16:9` or `9:16`), style/theme, character, palette, voice, audio, transition, and negative locks.
- Each prompt has all three timed beats and at least four relevant visual devices.
- Every ending matches the next opening.
- Dialogue exactly matches the approved narration.
- Dialogue is explicitly audio-only and is never displayed visually.
- Standalone prompts contain no hexadecimal, RGB, HSL, Pantone, or other technical color notation.
- Style 2 prompts feature the verified character anchor, BGM continuity lock, and anti-clutter negative constraints.
- Generated scenes contain no visible writing; optional overlay phrases are listed separately for post-production.
