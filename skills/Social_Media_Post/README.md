# Social Media Post

**智能社群貼文生成器** - 針對 Facebook、Threads、X、LinkedIn 四大平台生成優化貼文，自動套用演算法最佳實踐。

---

## 功能特色

- **平台優化**：自動適配各平台字數限制、格式規範
- **演算法洞察**：套用 2025-2026 最新演算法策略
- **風格一致**：預設風格模板確保品牌調性統一
- **串文生成**：長文自動拆分為串文格式

---

## 支援平台

| 平台 | 字數限制 | 特色 |
|------|---------|------|
| Facebook | 63,206 字元 | 長篇教學、結構化內容 |
| Threads | 500 字元 | 對話式、真實語氣 |
| X (Twitter) | 280 字元 | 簡潔有力、善用 Hashtag |
| LinkedIn | 3,000 字元 | 專業調性、商業價值 |

---

## 快速安裝

此專案為純 Python，無需安裝額外套件。

```bash
cd Social_Media_Post

# 確認 Python 版本
python --version  # 需要 3.10+
```

### 放置到 Claude Code Skills 目錄（選用）

若要讓 Claude Code 自動識別此 Skill：

| 系統 | 路徑 |
|------|------|
| Windows | `C:\Users\{用戶名}\.claude\skills\Social_Media_Post\` |
| macOS/Linux | `~/.claude/skills/Social_Media_Post/` |

---

## 使用方式

### 方式一：透過 Claude Code（推薦）

將 Skill 放到 `.claude/skills/` 目錄後，在 Claude Code 中直接說：

- 「幫我寫 FB 貼文」
- 「寫一篇 Threads 貼文關於 AI」
- 「Generate X post for my product」
- 「寫 LinkedIn 公告」

Claude 會自動識別並引導你完成貼文生成。

### 方式二：手動執行腳本

**Step 1：分析內容**

```bash
python scripts/post_analyzer.py --input "你的內容或公告"
```

輸出包含：主題、重點、語氣、建議平台、行動呼籲。

**Step 2：優化貼文**

```bash
python scripts/engagement_optimizer.py --platform facebook --content "貼文草稿"
```

支援平台：`facebook`、`threads`、`x`、`linkedin`、`instagram`

輸出包含：優化後內容、字數統計、互動分數、改進建議。

**Step 3：生成串文（可選）**

```bash
python scripts/thread_generator.py --platform x --content "長文內容" --max-posts 5
```

將長文自動拆分為多則串文。

---

## 腳本說明

| 腳本 | 功能 |
|------|------|
| `post_analyzer.py` | 分析內容，提取重點、判斷語氣、建議平台 |
| `engagement_optimizer.py` | 套用平台規則，計算互動分數，提供優化建議 |
| `thread_generator.py` | 將長文拆分為串文格式 |

---

## 演算法洞察

### Facebook（2025-2026）

- 有意義的互動（40%）：留言、分享、收藏
- 內容品質（30%）：閱讀時間、完成率
- 相關性（20%）：基於用戶興趣
- 時效性（10%）：新內容曝光

### Threads（2025）

- 互動（40%）：按讚、留言、分享
- 時效性（30%）：新內容優先
- 興趣/相關性（20%）
- Hashtag 無效，系統會忽略

### X（2025）

- 互動率：按讚、轉推、回覆
- 時效性：新推文優先
- 媒體：含圖片/影片表現更好
- Hashtag：建議 2-3 個

### LinkedIn（2025）

- 停留時間：用戶閱讀時長
- 互動：按讚、留言、分享
- 人脈關係：一度人脈優先

---

## 風格指南

### 預設風格檔

- `styles/facebook.md` - Facebook 中長篇教學型風格

### 新增自訂風格

在 `styles/` 目錄建立新的 `.md` 檔案，參考 `facebook.md` 格式。

---

## 檔案結構

```
Social_Media_Post/
├── SKILL.md                          # Claude Skill 定義（給 AI 看）
├── SPEC.md                           # 完整技術規格書（給 AI 複刻用）
├── README.md                         # 本檔案（給人看）
├── scripts/
│   ├── post_analyzer.py              # 內容分析腳本
│   ├── engagement_optimizer.py       # 平台優化腳本
│   └── thread_generator.py           # 串文生成腳本
└── styles/
    └── facebook.md                   # Facebook 風格指南
```

---

## 常見問題

### Q: 為什麼 Threads 的 Hashtag 被移除？

Threads 演算法會忽略 Hashtag，保留反而可能影響閱讀體驗。系統會自動移除。

### Q: 如何新增其他平台風格？

在 `styles/` 目錄建立新的 `.md` 檔案（如 `linkedin.md`），然後在 `SKILL.md` 中加入參考。

### Q: 互動分數如何計算？

基於以下因素：
- Hook 強度（開頭是否有吸引力）
- 價值指標（是否有明確價值）
- 格式（是否使用 Emoji、換行）
- 互動提示（是否有問句引發討論）
- 字數是否符合平台限制

---

## 系統需求

- **Python**：3.10 或更高版本
- **作業系統**：Windows / macOS / Linux
- **無需 API Key**：純本地處理

---

## 授權條款

MIT License

---

## 更新日誌

### v1.1.0 (2025-01-21)
- 支援 Facebook、Threads、X、LinkedIn 四大平台
- 新增 2025-2026 演算法洞察
- 新增串文生成功能
- 新增 Facebook 風格指南
