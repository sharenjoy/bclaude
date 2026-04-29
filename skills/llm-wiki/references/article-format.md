# Article Format — raw/articles 格式規範

## Frontmatter 必填欄位

```yaml
---
title: "文章或影片標題"
origin: external
type: article # article | video | social
source_url: "https://..."
tags: [標籤1, 標籤2, 標籤3]
---
```

### `type` 對照表

| 輸入來源             | type 值   |
| -------------------- | --------- |
| 一般網頁文章、部落格 | `article` |
| YouTube 影片         | `video`   |
| Facebook / Threads / X / Instagram / 社群貼文 | `social` |

### `platform` 規則（social 類型必填）

填入平台名稱，小寫英文，從 URL 或使用者說明自動判斷。例如：`facebook`、`threads`、`x`、`instagram`、`linkedin`、`reddit`、`ptt`……不限定清單，遇到新平台直接填對應名稱。

### `origin` 規則

- 外部連結、他人內容 → `external`
- 使用者自己的貼文 → `self`

---

## 各類型的內容結構

### `article`（一般網頁文章）

```
[保留原文段落結構，移除廣告與無關區塊]

## 重點段落
（直接保留原文最核心的 3–5 個段落，維持原文標題結構）
```

範例：

```markdown
---
title: "The Complete Guide to Building Skills for Claude"
origin: external
type: article
source_url: "https://example.com/article"
tags: [claude, skills, AI, anthropic]
---

## Introduction

（原文內容...）

## Fundamentals

（原文內容...）
```

---

### `video`（YouTube 影片）

```markdown
---
title: "影片標題"
origin: external
type: video
source_url: "https://youtube.com/watch?v=..."
tags: [...]
---

## 影片資訊

- **頻道**：頻道名稱
- **發布日期**：YYYY-MM-DD
- **片長**：mm:ss

## 核心內容

（yt-analyze 8 模塊分析結果，完整保留）

## 重點整理

（3–5 條最關鍵的要點）
```

---

### `social`（Facebook / Threads / X / Instagram）

```markdown
---
title: "貼文主題摘要"
origin: external      # 他人貼文用 external，自己的貼文用 self
type: social
platform: facebook    # facebook | threads | x | instagram
source_url: "https://..." # 無連結時填 ""
tags: [...]
---

## 貼文來源

- **作者**：作者名稱
- **發布時間**：YYYY-MM-DD（或「未知」）
- **平台**：Facebook / Threads / X / Instagram

## 貼文內容

（完整貼文文字，原文保留）

## 補充說明

（相關連結、重要留言、背景脈絡，無則省略此段）
```

---

## 命名範例

| 資源類型 | 檔名範例                                    |
| -------- | ------------------------------------------- |
| 文章     | `20260420 Claude Skills 完整建構指南.md`    |
| 影片     | `20260420 GPT-4o 與 Claude 3.7 深度比較.md` |
| FB 貼文  | `20260420 Sam Altman 談 AGI 時間線.md`      |
