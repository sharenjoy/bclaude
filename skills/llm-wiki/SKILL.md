---
name: LLM Wiki
description: 將資源寫入 llm-wiki 知識庫。當使用者說「寫入wiki」、「存到wiki」、「加入知識庫」、「放進wiki」、「/llm-wiki」、「save to wiki」，或提供連結/貼文/影片並要求存入知識庫時觸發。支援三種輸入：一般網頁URL、YouTube影片、任意社群平台貼文。可指定分類：articles、books、notes、papers、podcasts、projects。
---

# LLM Wiki — 知識庫寫入工具

接收任意資源（URL、社群貼文、YouTube 影片）→ 分析內容 → 依 llm-wiki 格式產生 Markdown → 存入 `~/AI/llm-wiki/raw/<分類>/`。

## Step 1：判斷儲存分類

從使用者的提示詞判斷要存入哪個子目錄：

| 使用者說的關鍵詞 | 子目錄 |
|-----------------|--------|
| 書、book、書摘、讀書筆記 | `books` |
| 筆記、note、心得、memo | `notes` |
| 論文、paper、研究、report | `papers` |
| podcast、廣播、節目、episode | `podcasts` |
| 專案、project、作品 | `projects` |
| 文章、article、部落格、新聞，或未指定 | `articles`（預設） |

若無法判斷，**預設存入 `articles/`**，不需詢問使用者。

## Step 2：識別輸入類型

判斷使用者提供的是哪種資源：

| 輸入類型 | 判斷條件 |
|----------|----------|
| **YouTube 影片** | URL 包含 `youtube.com` 或 `youtu.be` |
| **一般網頁 URL** | 其他 http/https 連結 |
| **社群貼文** | 使用者貼上貼文文字，或提供社群平台 URL（非一般文章、非 YouTube） |

輸入類型不明確時直接詢問使用者。

## Step 2：獲取與分析內容

### 一般網頁 URL
使用 WebFetch 抓取頁面：
- 提取：標題、作者、發佈日期、主要正文
- 忽略：廣告、導覽列、頁尾、作者簡介框

### YouTube 影片
啟動 yt-analyze skill 的通用分析流程：
- 讀取 `~/AI/Projects/YT_Analyze/.agent/skills/analyze-content/SKILL.md`
- 執行 8 模塊分析取得完整結果
- 以分析結果作為文章內容

### 社群貼文（任意社群平台）
- 如果使用者直接貼上文字 → 直接使用該文字
- 如果提供社群平台 URL → 使用 WebFetch 嘗試獲取，失敗則請使用者貼上貼文內容
- 從 URL 或使用者說明自動判斷平台名稱（填入 `platform` 欄位）
- 提取：作者名稱、發佈時間（如有）、完整貼文文字

## Step 3：載入格式規範

讀取 `references/article-format.md`，確認該輸入類型對應的 Markdown frontmatter 與內容結構。

## Step 4：產生 Markdown

依格式規範生成完整的 Markdown 內容：
- YAML frontmatter 必填欄位：`title`、`origin`、`type`、`source_url`、`compiled`、`tags`
- `compiled` 填入今天日期（YYYY-MM-DD）
- `tags` 從內容自動提取 3-5 個最相關的繁體中文關鍵詞
- 內容以繁體中文為主，保留原文重要段落

讀取 `references/writing-style.md` 確認摘要或說明段落的語氣風格。

## Step 5：命名與儲存

檔案命名：`YYYYMMDD 標題.md`
- 日期：今天的日期（YYYYMMDD 格式）
- 標題：從內容提取的簡短繁體中文標題（10–20 字）
- 儲存路徑：`~/AI/llm-wiki/raw/<Step 1 判斷的子目錄>/`

使用 Write 工具建立檔案。

## Step 6：確認並提示下一步

告知使用者：
- 已建立的完整檔案路徑（含子目錄）
- 自動提取的 tags 清單
- 提示可執行 `/compile` 將此文章編譯進 `wiki/`

## 規則

- 原始內容只放 `raw/<子目錄>/`，不直接寫 `wiki/`
- 一個資源建立一個檔案，不合併
- 檔名格式嚴格遵守 `YYYYMMDD 標題.md`
- frontmatter 所有必填欄位不可省略
- 輸出語言：繁體中文
