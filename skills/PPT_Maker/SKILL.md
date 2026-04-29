---
name: ppt
description: 企業級簡報生成工具。選擇預設風格、規劃內容架構、批量生成高品質簡報。適用於：製作 PPT、演示文稿、提案簡報等場景。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# PPT Maker - 智能簡報生成系統

## 系統概述

PPT Maker 是一套 AI 驅動的簡報生成系統，透過預設風格模板與智能內容規劃，快速產出專業級演示文稿。

**核心流程**：風格選擇 → 內容規劃 → 圖片生成 → 超分處理 → 打包輸出

---

## 使用者交互流程

當使用者提出「幫我做簡報」、「製作 PPT」等請求時，依循以下流程：

### 階段一：資訊收集

**首先動態讀取可用風格**：執行 `ls {skill_path}/styles/*.md` 獲取當前可用的風格清單，解析每個風格檔案的「風格名稱」和「風格描述」。

向使用者一次性詢問所有必要資訊：

```
好的，我來協助你製作簡報！請提供以下資訊：

**1. 內容來源**（必填）
   - 提供檔案路徑（如 @report.md）
   - 或直接貼上文字內容

**2. 風格選擇**
   [根據 styles/ 目錄動態列出]
   A. {風格名稱} - {風格描述}
   B. {風格名稱} - {風格描述}
   ...

**3. 頁數規模**
   - 精簡版（5 頁）
   - 標準版（5-10 頁，推薦）
   - 詳細版（10-15 頁）
   - 完整版（20-25 頁）

請一次告訴我這些資訊，例如：
「內容是 @report.md，風格選 A，約 10 頁」
```

### 階段二：規劃確認

分析內容後，展示頁面規劃表：

```
內容分析完成，以下是簡報規劃：

**主題**：{主題名稱}
**總頁數**：{N} 頁
**風格**：{選擇的風格}

| 頁碼 | 類型 | 內容摘要 |
|------|------|----------|
| 1 | 封面 | {標題} |
| 2 | 內容 | {要點概述} |
| ... | ... | ... |
| N | 結尾 | 感謝 & 聯繫方式 |

確認無誤請回覆「確認」，或告知需要調整的部分。
```

### 階段三：執行生成

使用者確認後，開始執行生成流程（詳見下方「執行流程」章節）。

---

## 輸入格式支援

| 格式 | 說明 |
|------|------|
| Markdown (.md) | 推薦，結構清晰易解析 |
| PDF (.pdf) | 自動擷取文字內容 |
| Word (.docx) | 自動擷取文字內容 |
| 純文字 | 直接貼入對話視窗 |

---

## 輸出內容

每次生成輸出至 `.ppt_maker/` 目錄：

```
.ppt_maker/
├── slides_plan.json          # 頁面規劃檔
├── images/                   # 原始生成圖片
├── images-4k/                # 超分後 4K 圖片
├── output.pptx               # 原始 PPTX
├── output-4k.pptx            # 4K 版 PPTX（推薦使用）
└── viewer.html               # 網頁播放器
```

---

## 頁數與內容量對照

| 選項 | 頁數 | 適合內容量 |
|------|------|-----------|
| 精簡版 | 5 頁 | 500 字以內 |
| 標準版 | 5-10 頁 | 500-1500 字 |
| 詳細版 | 10-15 頁 | 1500-3000 字 |
| 完整版 | 20-25 頁 | 3000 字以上 |

---

## 風格系統

**動態載入**：風格定義檔存放於 `styles/` 目錄，每個 `.md` 檔案代表一種風格。

每個風格檔案包含：
- `id`：風格識別碼（用於 slides_plan.json）
- `name`：顯示名稱
- `description`：風格特點描述
- `DESIGN_SYSTEM`：完整設計規範
- `PAGE_TEMPLATES`：各頁面類型的 Prompt 模板

新增風格只需在 `styles/` 目錄建立新的 `.md` 檔案。

---

## 執行流程

### Step 1：內容分析與規劃生成

讀取使用者提供的內容，分析結構，生成 `slides_plan.json`。

**關鍵：加入 `enhancement` 欄位進行視覺增強**

根據每頁內容的語義，添加客製化的視覺描述：

```json
{
  "title": "簡報標題",
  "style": "deep-space-tech",
  "resolution": "4K",
  "slides": [
    {
      "slide_number": 1,
      "page_type": "cover",
      "content": "標題：AI 產品設計\n副標題：從概念到落地",
      "enhancement": "中央放置一個代表「創新」的 3D 玻璃球體，內部有流動的光線"
    },
    {
      "slide_number": 2,
      "page_type": "content",
      "content": "核心設計原則\n- 以用戶為中心\n- 數據驅動決策\n- 快速迭代驗證",
      "enhancement": "使用三欄卡片佈局，每張卡片配有發光圖標"
    }
  ]
}
```

**enhancement 欄位指引**：
- 對比類內容：建議左右分欄佈局
- 列表類內容：建議卡片網格 + 圖標
- 數據類內容：建議配發光圖表
- 封面/結尾頁：建議描述獨特的 3D 裝飾元素

**頁面類型**：
- `cover`：封面頁（第 1 頁）
- `content`：內容頁（觀點、要點列表）
- `data`：數據頁（統計、圖表）
- `end`：結尾頁（最後一頁）

將 `slides_plan.json` 儲存至 `.ppt_maker/slides_plan.json`。

### Step 2：批量圖片生成

呼叫生成腳本：

```bash
python {skill_path}/scripts/generate.py \
  --plan .ppt_maker/slides_plan.json \
  --style {skill_path}/styles/{風格檔案}.md \
  --output .ppt_maker \
  --verify
```

**參數說明**：
- `--plan`：規劃檔路徑
- `--style`：風格定義檔路徑
- `--output`：輸出目錄
- `--verify`：啟用視覺驗證（檢查文字正確性）
- `--start-from N`：從第 N 頁開始（斷點續傳）

**使用的 AI 模型**：
- 圖片生成：`gemini-3-pro-image-preview`（Gemini 3 Pro 圖像模型）
- 視覺驗證：`gemini-2.0-flash`

### Step 3：超分處理

API 返回的圖片解析度較低（約 1376×768），必須進行超分處理：

```bash
python {skill_path}/scripts/upscale.py \
  --images .ppt_maker/images/ \
  --output .ppt_maker/images-4k/ \
  --scale 4
```

### Step 4：打包輸出

```bash
# 生成網頁播放器
python {skill_path}/scripts/build_viewer.py \
  --images .ppt_maker/images-4k/ \
  --output .ppt_maker/viewer.html

# 生成 PPTX 檔案
python {skill_path}/scripts/build_pptx.py \
  --images .ppt_maker/images-4k/ \
  --output .ppt_maker/output-4k.pptx
```

### Step 5：交付成果

告知使用者輸出檔案位置：
- **4K PPTX**：`.ppt_maker/output-4k.pptx`（推薦使用）
- **網頁播放器**：`.ppt_maker/viewer.html`
- **圖片素材**：`.ppt_maker/images-4k/`

---

## 單頁修改流程

當需要修改特定頁面時，**務必不影響其他頁面**：

1. 建立僅包含該頁的臨時規劃檔
2. 單獨生成該頁
3. 合併回原本的圖片目錄
4. 重新打包輸出

**原則**：修改文字內容時，絕不犧牲頁面的視覺品質。

---

## API 設定

在專案根目錄建立 `config.env`：

```bash
GEMINI_API_KEY=your_api_key_here
```

**取得 API Key**：https://aistudio.google.com/apikey

---

## 檔案結構

| 檔案 | 說明 |
|------|------|
| `SKILL.md` | 本檔案，Skill 主入口 |
| `SPEC.md` | 完整技術規格書 |
| `README.md` | 使用者安裝指南 |
| `config.env` | API 設定（需自行建立） |
| `styles/*.md` | 風格定義檔 |
| `scripts/generate.py` | 圖片生成腳本 |
| `scripts/upscale.py` | 超分處理腳本 |
| `scripts/build_pptx.py` | PPTX 打包腳本 |
| `scripts/build_viewer.py` | 網頁播放器生成腳本 |

---

## 常見問題

### Q: 生成的中文有錯字？

在 enhancement 欄位中加入英文對照：
```
"enhancement": "... 顯示文字：團隊效率 (Team Efficiency)"
```

### Q: 文字模糊或亂碼？

系統已內建視覺驗證機制：
1. 生成時傳入完整文字內容作為上下文
2. Prompt 強制要求使用繁體中文
3. 視覺驗證會檢查是否有簡體字或亂碼，自動重試

### Q: 比例不正確？

Prompt 已強制要求 16:9 比例。若仍有問題，打包腳本會自動適配（Fit Inside）確保內容不變形。

### Q: 需要修改某一頁？

參考「單頁修改流程」章節，建立臨時規劃檔單獨生成。
