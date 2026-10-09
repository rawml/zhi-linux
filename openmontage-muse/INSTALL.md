# 安裝注記（2026-10-08，老爸上傳 SKILL.md 後由三蛋安裝；同日 Fish Audio key 接通後補完）

## 裝了什麼
- `~/workspace/skills/openmontage-muse/SKILL.md`：用戶上傳的原文，一字未動。
- `~/workspace/skills/openmontage-muse/scripts/speak.sh`：配音一行調用（音色名→voice id 映射，見文件內 `VOICE_IDS`；選音色前先用 `muse.create_options` 問用戶）。
- `~/workspace/skills/openmontage-muse/scripts/compose.sh`：ffmpeg 合成（片段標準化→拼接→混旁白→可選燒錄 srt），已驗證 ffmpeg 8.1 + libass 可用。
- `~/workspace/skills/fish-audio/bin/tts.py`：Fish Audio TTS（`POST https://api.fish.audio/v1/tts`，默認免費模型 `s2.1-pro-free`）。**認證走 authd surrogate 交換**：腳本只經手 `hsurr:*` surrogate 值，經 `dynamic_credentials.add_surrogate_to_request()` 注入 Bearer 頭，真 key 永不可讀、永不寫進文件/日誌/記憶。舊的 `FISH_API_KEY` 環境變量方案已廢棄（不符合 skill-creator 的校驗規則）。

## 已驗證（2026-10-08 key 接通後實測）
- `GET /model?self=true`：用戶 workspace 下自有音色為 0，5 個音色取自公用庫（按名搜、取首個同名結果）：
  - AD學姐 `7f92f8afb8ec43bf81429cc1c9199cb1`
  - 賈小軍 `80cf680e668c44fc8d5795f80d903f7a`
  - 溫柔動聽女聲 `faccba1a8ac54016bcfc02761285e67f`
  - 宣傳片大氣渾厚 `aa585dc793fe4dd5bcfd891e3cbd2416`（庫中標題為「宣傳片大氣渾厚男配音」，最接近）
  - 女大學生 `5c353fdb312f4888836a9a5680099ef0`
  - 注意：同名音色有多個副本，映射取的是首個結果；若用戶聽出唔啱，可換同名其他 id。
- 冒煙測試全鏈路跑通：`speak.sh` 中文配音（溫柔動聽女聲，轉寫核驗內容正確）+ `compose.sh` 合成字幕版，產物在 `~/workspace/openmontage-muse/runs/_smoke/final.mp4`（4.99s，-shortest 對齊旁白）。
- 真人克隆類音色（AD學姐等）商用有肖像權風險，公開分發前必須提醒用戶。
