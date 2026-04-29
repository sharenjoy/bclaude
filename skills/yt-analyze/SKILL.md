---
name: YT Analyze
description: YouTube 影片深度分析系統入口。當使用者提到「分析 YouTube 影片」、「YT 分析」、「財經影片分析」、「口播稿」、「yt-analyze」、「啟動 YT Analyze」、「分析這個頻道」、「股票影片分析」，或提供 YouTube URL 並要求分析時觸發。
---

# YT Analyze — 入口點

專案位置：`~/AI/Projects/YT_Analyze/`

YouTube 影片深度分析 + Dashboard 展示系統。輸入 YouTube URL → AI 分析字幕 → 結構化報告 + 社群貼文 + 口播稿。

## 啟動服務

```bash
cd ~/AI/Projects/YT_Analyze
npm run dev      # 前端 → http://localhost:5173
npm run server   # 後端 API → http://localhost:3001
```

## 可用 Skills（切換到專案目錄後執行）

| Skill | 觸發說明 |
|---|---|
| `analyze-content` | 「分析這條影片」+ YouTube URL，通用 8 模塊分析 |
| `finance-video-analyzer` | 「分析財經影片」「股票影片分析」+ URL，11 模塊 + 即時新聞 |
| `script-content` | 「生成口播稿」「做腳本」，為已分析影片生成口播稿 |

## 執行步驟

### Step 1：切換工作目錄
所有操作必須在 `~/AI/Projects/YT_Analyze/` 目錄下執行。

### Step 2：識別意圖
- 提供 YouTube URL → 詢問「通用分析」還是「財經分析」
- 提到「口播稿」→ 執行 `script-content`
- 要求查看結果 → 啟動服務並開啟 Dashboard

### Step 3：執行對應 Skill
讀取對應 skill 的完整 SKILL.md：
- 通用分析：`~/AI/Projects/YT_Analyze/.agent/skills/analyze-content/SKILL.md`
- 財經分析：`~/AI/Projects/YT_Analyze/.agent/skills/finance-video-analyzer/SKILL.md`
- 口播稿：`~/AI/Projects/YT_Analyze/.agent/skills/script-content/SKILL.md`

## 必要 API Keys（`~/AI/Projects/YT_Analyze/.env`）

| Key | 用途 |
|---|---|
| `SUPADATA_API_KEY` | YouTube 字幕下載 |
| `YOUTUBE_API_KEY` | 影片元數據 |
| `NOTION_API_KEY` | 社群貼文上傳（選用）|
