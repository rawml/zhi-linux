---
name: "openmontage-muse"
description: "OpenMontage 适配版：用 Muse 原生能力跑 agentic 视频生产管线——media 生成视频片段、Fish Audio 配音、ffmpeg 合成，全程零 API key、零费用。用户要做视频（短片、混剪、解说、口播、预告片），或给参考视频要\"做个类似的\"时使用。"
---

# OpenMontage-Muse

把 OpenMontage 的 agentic 视频生产思想，跑在 Muse 原生工具链上。
原版的上游仓库（只读参考）放在 `upstream/`，生产流程不依赖它。

## 能力映射（替代原版 provider 层）

| 原版环节 | 原版 provider（需 key/付费） | Muse 版替代 | 说明 |
|---|---|---|---|
| 视频片段生成 | Veo / Kling / MiniMax（fal.ai 等） | `media.generate_video` | 文本生视频或图生视频；**每条用户消息最多 6 个成功视频**（含转交给 subagent 生成的），分镜时按 ≤6 个场景规划 |
| 关键帧/静态素材 | FLUX / GPT Image / Imagen | `media.generate_image` | 每条消息最多 4 张；图生视频更可控，先出关键帧再转视频 |
| 配音/旁白 | ElevenLabs / Google TTS / Chirp | Fish Audio `bin/tts.py` | 免费模型 s2.1-pro-free（$0，免费至 2026-11-30）；5 个实测中文音色见下；长文案分段合成再用 ffmpeg 拼接 |
| 剪辑合成 | Remotion / Python composer | `ffmpeg` | 拼接、混音、字幕、转码，本机已验证可用 |
| 免费素材路线 | Pexels / Pixabay | 可选（需 key）；默认直接用 media 生成 | 二选一 |

中文音色（2026-10-08 实测可用，直接按名字调用）：
- AD学姐（年轻女声）、贾小军、温柔动听女声、宣传片大气浑厚、女大学生

配音调用（一行搞定，自动走免费档）：
```sh
~/workspace/skills/openmontage-muse/scripts/speak.sh "旁白文案" 温柔动听女声 narration.mp3
```
底层是 `~/workspace/skills/fish-audio/bin/tts.py`（`--reference-id` 指定音色 id，见 speak.sh 内映射）。

**选音色流程（用户要求）**：需要旁白时，**先问用户选哪个声音**——用 `muse.create_options` 给出 5 个选项，不要自己默认选定：
- AD学姐：年轻女声，女友感
- 贾小军：男声
- 温柔动听女声：舒缓女声
- 宣传片大气浑厚：浑厚男声，适合宣传片/解说
- 女大学生：青春女声
用户选定后再调用 speak.sh。

## Fish Audio 免费档配置（key 相关）

- 免费模型 `s2.1-pro-free`：$0/百万字节，限时免费至 2026-11-30，无 SLA、受公平使用约束。
- **Key 已由用户经 Secure Vault 接入**（凭证名 `custom.fish-audio`），调用时通过 surrogate 机制自动注入 Authorization 头；**永远不要让用户在聊天里贴 key**，也不要把 key 写进任何文件、日志、记忆。
- 如果合成返回 401/403：先确认请求真的走了 helper（没走 helper 就是没带凭证）；确认带上仍被拒绝，再用 `credentials.request_api_access`（带 `reconnect`）让用户重连。
- 真人克隆类音色（AD学姐等）商用有肖像权风险，公开分发前必须提醒用户。

## 生产管线

1. **idea**：明确主题、时长、横/竖屏、有无旁白。输出一句话 brief（讲什么、给谁看、什么风格）。
2. **script**：写分镜脚本：场景列表 = 每个场景的画面描述 prompt + 时长 + 旁白文案。场景数 ≤6（视频配额硬限制）；要更多场景就分多条消息生产。
3. **reference（可选）**：用户给了参考视频（YouTube/TikTok/Reel 链接或本地文件）→ 先拆解它的文案、节奏、场景、风格，再出 2-3 个差异化创意，不直接抄。
4. **asset**：按场景逐个生成，全部落到 `~/workspace/openmontage-muse/runs/<日期>-<主题>/assets/`：
   - `media.generate_video`：prompt 写具体画面描述（主体、动作、场景、镜头、氛围）；视频子代理会自动扩写，**不要自己加电影感修辞**；`output_dir` 指到 assets 目录；
   - 旁白：`scripts/speak.sh "文案" <音色名> out.mp3`（长文案先分段，合成后用 ffmpeg 拼成一条音轨）；
5. **compose**：`scripts/compose.sh`（ffmpeg）：按分镜顺序拼接片段 → 混入旁白（`-shortest` 对齐）→ 可选叠加字幕（srt，需 libass）→ 输出终版 mp4。
6. **review**：看一遍成片（ffprobe 查时长 / 抽帧看画面），检查字幕、节奏、音画对齐；有问题回第 4 步重生成对应场景。

## 硬约束

- 每条用户消息视频配额 6 个：生产前先算好场景数，超了就拆多次对话。转交 subagent 做视频也要在指令里写明它能用几个。
- Fish Audio 免费档无 SLA、受公平使用约束；真人克隆类音色（AD学姐等）商用有肖像权风险，公开分发前必须提醒用户。
- 重要决策（换音色、改分镜、大改创意）先跟用户确认再执行；决策记在 run 目录的 `DECISIONS.md`（append-only）。

## 已验证

2026-10-08 冒烟测试：1 个视频片段 + Fish Audio 旁白 + ffmpeg 合成，全链路跑通，产物在 `~/workspace/openmontage-muse/runs/_smoke/final.mp4`。
