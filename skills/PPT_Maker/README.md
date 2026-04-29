# PPT Maker

**AI 驅動的智能簡報生成系統** - 透過預設風格模板，快速產出專業級演示文稿。

---

## 功能特色

- **風格統一**：預設風格模板確保每頁視覺一致
- **智能規劃**：根據內容自動規劃頁面結構
- **高品質輸出**：4K 超分處理確保清晰度
- **多格式支援**：Markdown、PDF、Word、純文字

---

## 快速安裝

```bash
cd PPT_Maker

# 建立虛擬環境
python -m venv venv

# 啟用虛擬環境
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 設定 API Key
cp config.example.env config.env
# 編輯 config.env，填入 GEMINI_API_KEY
```

### 放置到 Claude Code Skills 目錄（選用）

若要讓 Claude Code 自動識別此 Skill：

| 系統 | 路徑 |
|------|------|
| Windows | `C:\Users\{用戶名}\.claude\skills\PPT_Maker\` |
| macOS/Linux | `~/.claude/skills/PPT_Maker/` |

---

## 使用方式

### 方式一：透過 Claude Code（推薦）

將 Skill 放到 `.claude/skills/` 目錄後，在 Claude Code 中直接說：

- 「幫我做一份簡報」
- 「我要製作 PPT」
- 「做一個關於 AI 的演示文稿」

Claude 會自動識別並引導你完成簡報製作。

### 方式二：手動執行腳本

**Step 1：準備規劃檔 `slides_plan.json`**

```json
{
  "title": "我的簡報",
  "style": "deep-space",
  "slides": [
    {
      "slide_number": 1,
      "page_type": "cover",
      "content": "標題：AI 入門指南\n副標題：從零開始學習人工智能",
      "enhancement": "中央放置一個發光的 3D 玻璃球體，象徵智慧與創新"
    },
    {
      "slide_number": 2,
      "page_type": "content",
      "content": "什麼是人工智能？\n- 機器模擬人類智慧\n- 學習、推理、自我修正\n- 廣泛應用於各行業",
      "enhancement": "三欄卡片佈局，每張卡片配有發光圖標"
    },
    {
      "slide_number": 3,
      "page_type": "end",
      "content": "謝謝聆聽\n聯繫方式：hello@example.com",
      "enhancement": "極簡設計，文字居中，配小型 3D 裝飾"
    }
  ]
}
```

**Step 2：執行生成命令**

```bash
python scripts/generate.py \
  --plan slides_plan.json \
  --style styles/deep_space.md \
  --output .ppt_maker \
  --verify
```

**參數說明：**
| 參數 | 說明 |
|------|------|
| `--plan` | 規劃檔路徑 |
| `--style` | 風格定義檔路徑 |
| `--output` | 輸出目錄 |
| `--verify` | 啟用視覺驗證（檢查文字正確性） |
| `--start-from N` | 從第 N 頁開始（斷點續傳） |

**Step 3：取得成果**

```
.ppt_maker/
├── slides_plan.json      # 規劃檔
├── images/               # 原始圖片
├── images-4k/            # 4K 超分圖片
├── output-4k.pptx        # ← 下載這個 PPTX
└── viewer.html           # ← 或用瀏覽器開啟預覽
```

---

## API 需求

### Google Gemini API

本工具使用 Google Gemini API 進行圖片生成和視覺驗證。

**取得 API Key：**
1. 前往 [Google AI Studio](https://aistudio.google.com/apikey)
2. 登入 Google 帳號
3. 點擊「Create API Key」
4. 複製產生的 Key 到 `config.env`

**使用的模型：**
| 模型 | 用途 |
|------|------|
| `gemini-3-pro-image-preview` | 圖片生成（最新 Gemini 3 Pro 圖像模型） |
| `gemini-2.0-flash` | 視覺驗證（檢查文字正確性） |

---

## 費用說明

### Google Gemini API 定價

截至 2025 年 1 月，Gemini API 提供以下方案：

| 方案 | 費用 | 說明 |
|------|------|------|
| **免費方案** | $0 | 每分鐘有請求次數限制，適合測試 |
| **付費方案** | 依用量計費 | 無請求限制，適合正式使用 |

**預估成本（每份簡報）：**

| 頁數 | 圖片生成成本 | 視覺驗證成本 | 總計 |
|------|-------------|-------------|------|
| 5 頁 | ~$0.05 | ~$0.01 | ~$0.06 |
| 10 頁 | ~$0.10 | ~$0.02 | ~$0.12 |
| 20 頁 | ~$0.20 | ~$0.04 | ~$0.24 |

> **注意**：實際費用可能因 API 定價變動而異，請以 [Google 官方定價](https://ai.google.dev/pricing) 為準。

### 免費額度

Google AI Studio 提供免費額度供開發測試，足夠生成數十份簡報。建議先使用免費額度熟悉工具。

---

## 可用風格

| 風格 | 說明 | 適用場景 |
|------|------|----------|
| `deep_space` | 深空科技風格 | 科技發布會、AI 路演、高端提案 |

> 更多風格開發中，歡迎貢獻新風格！

---

## 檔案結構

```
PPT_Maker/
├── SKILL.md              # Claude Skill 定義（給 AI 看）
├── SPEC.md               # 完整技術規格書（給 AI 複刻用）
├── README.md             # 本檔案（給人看）
├── requirements.txt      # Python 依賴
├── config.example.env    # API 設定範例
├── scripts/
│   ├── generate.py       # 主生成腳本
│   ├── upscale.py        # 超分處理腳本
│   ├── build_pptx.py     # PPTX 打包腳本
│   └── build_viewer.py   # HTML 播放器腳本
└── styles/
    └── deep_space.md     # 深空科技風格
```

---

## 常見問題

### Q: 生成的中文有錯字？

**解決方案**：在規劃時於 `enhancement` 欄位加入英文對照
```json
"enhancement": "顯示文字：團隊效率 (Team Efficiency)"
```

### Q: 文字模糊或亂碼？

系統已內建視覺驗證機制，會自動重試。若仍有問題：
1. 確認使用 `--verify` 參數
2. 嘗試重新生成該頁

### Q: 圖片比例不正確？

Prompt 已強制要求 16:9 比例。打包腳本會自動適配，確保內容不變形。

### Q: API 請求失敗？

1. 確認 API Key 正確
2. 確認網路連線正常
3. 檢查是否超過免費額度限制

### Q: 如何新增風格？

在 `styles/` 目錄建立新的 `.md` 檔案，參考 `deep_space.md` 的格式。

---

## 系統需求

- **Python**：3.10 或更高版本
- **作業系統**：Windows / macOS / Linux
- **網路**：需要連線至 Google API

### 選用：Real-ESRGAN

若安裝 Real-ESRGAN，超分處理品質會更好：
- 下載：[Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
- 安裝後將 `realesrgan-ncnn-vulkan` 加入 PATH

若未安裝，系統會自動使用 Pillow (Lanczos) 進行超分處理，效果也相當不錯。

---

## 授權條款

MIT License

---

## 貢獻指南

歡迎提交 Pull Request！

- 新增風格：在 `styles/` 目錄建立新的 `.md` 檔案
- 修復問題：請先開 Issue 討論
- 功能建議：歡迎開 Issue 提出

---

## 更新日誌

### v1.0.0 (2025-01-21)
- 初始版本發布
- 支援深空科技風格
- 支援 4K 超分處理
- 支援 PPTX 和 HTML 輸出
