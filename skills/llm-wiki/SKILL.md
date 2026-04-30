---
name: llm-wiki
description: 將資源寫入 llm-wiki 知識庫。當使用者說「寫入wiki」、「存到wiki」、「加入知識庫」、「放進wiki」、「/llm-wiki」、「save to wiki」，或提供連結/貼文/影片並要求存入知識庫時觸發。支援四種輸入：一般網頁URL、YouTube影片、任意社群平台貼文、本地資源檔案（PDF/圖檔/PPT/PPTX/Word/Excel）。當使用者說「讀取資源目錄」、「列出assets」、「資源目錄」、「讀取資源」、「show assets」時，列出 ~/AI/llm-wiki/assets/ 最近新增的檔案供使用者選取。可指定分類：articles、books、notes、papers、podcasts、projects。
---

# llm-wiki — 知識庫寫入工具

接收任意資源（URL、社群貼文、YouTube 影片、本地檔案）→ 分析內容 → 依 llm-wiki 格式產生 Markdown → 存入 `~/AI/llm-wiki/raw/<分類>/`。

## Step 1：判斷儲存分類

從使用者的提示詞判斷要存入哪個子目錄：

| 使用者說的關鍵詞                      | 子目錄             |
| ------------------------------------- | ------------------ |
| 書、book、書摘、讀書筆記              | `books`            |
| 筆記、note、心得、memo                | `notes`            |
| 論文、paper、研究、report             | `papers`           |
| podcast、廣播、節目、episode          | `podcasts`         |
| 專案、project、作品                   | `projects`         |
| 文章、article、部落格、新聞，或未指定 | `articles`（預設） |

若無法判斷，**預設存入 `articles/`**，不需詢問使用者。

## Step 2：識別輸入類型

判斷使用者提供的是哪種資源：

| 輸入類型             | 判斷條件                                                         |
| -------------------- | ---------------------------------------------------------------- |
| **Assets 本地檔案**  | 使用者說「讀取資源目錄」、「列出assets」、「資源目錄」等關鍵詞  |
| **YouTube 影片**     | URL 包含 `youtube.com` 或 `youtu.be`                             |
| **一般網頁 URL**     | 其他 http/https 連結                                             |
| **社群貼文**         | 使用者貼上貼文文字，或提供社群平台 URL（非一般文章、非 YouTube） |

輸入類型不明確時直接詢問使用者。

## Step 2A：Assets 目錄流程（本地資源檔案）

當使用者說「讀取資源目錄」、「列出 assets」、「資源目錄」、「讀取資源」、「show assets」時觸發此流程：

### 1. 列出最近新增的檔案

執行以下 Bash 指令，列出最近新增的前 20 個檔案：

```bash
ls -lt ~/AI/llm-wiki/assets/ | head -21
```

將結果格式化後展示給使用者（含序號、檔案名、修改日期），讓使用者選取要處理的檔案。

### 2. 依檔案類型讀取內容

使用者選取後，依副檔名決定讀取方式：

| 副檔名               | 讀取方式                                                                 |
| -------------------- | ------------------------------------------------------------------------ |
| `.pdf`               | 使用 Read 工具讀取（最多 20 頁），提取標題、摘要、主要內容               |
| `.png` `.jpg` `.jpeg` `.webp` | 使用 Read 工具讀取圖片（多模態分析），描述圖片內容與關鍵資訊  |
| `.ppt` `.pptx`       | 執行 `python3 -c "from pptx import Presentation; ..."` 提取文字內容；若失敗則告知使用者無法自動解析 |
| `.doc` `.docx`       | 執行 `python3 -c "from docx import Document; ..."` 提取段落文字；若失敗則嘗試 `pandoc` 轉純文字 |
| `.xls` `.xlsx`       | 執行 `python3 -c "import openpyxl; ..."` 讀取各工作表內容；若失敗則嘗試 `python3 -c "import pandas as pd; ..."` |
| 其他                 | 嘗試 Read 工具；若失敗則以 Bash 讀取前 200 行                            |

### 3. 接續標準流程

取得檔案內容後，從 **Step 1（判斷分類）** 重新開始，接著執行 Step 3 → Step 6 的完整流程：

- `source_url` 填入本地檔案路徑（`file://~/AI/llm-wiki/assets/<檔名>`）
- `origin` 填入 `local`
- `type` 依副檔名決定（`pdf` / `image` / `slides` / `document` / `spreadsheet` / `file`）

## Step 2B：獲取與分析內容（URL / 社群貼文 / YouTube）

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
