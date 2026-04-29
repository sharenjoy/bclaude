---
name: skill-iteration-loop
description: >
  使用 AutoResearch + Binary Eval 迭代改進 Skill 的完整流程指南。
  當使用者提到「讓 skill 越來越好」、「評估 skill 效果」、「優化 skill」、「測試 skill 是否正確觸發」、
  「改進 skill 描述」、「Binary Eval」、「AutoResearch」、「skill 迭代」、「evals.json」或
  想知道「如何讓 skill 越來越符合使用目的」時，務必觸發此 skill。
  也適用於使用者已有 skill 草稿，想透過結構化測試循環來驗證與改進的情境。
---

# Skill 迭代優化循環

這個 skill 指導你如何用「草稿 → 測試 → Binary Eval 評分 → 人工審閱 → 改進」的循環，讓任何 skill 越來越符合你的使用目的。

核心概念：**用真實案例測試，用結構化回饋改進，每輪迭代都可量化進步幅度。**

---

## 整體流程概覽

```
寫 Skill 草稿（或從現有 skill 開始）
        ↓
設計測試案例（evals/evals.json）
        ↓
執行測試：with-skill vs baseline 並行
        ↓
Binary Eval 自動評分 + 人工審閱（Eval Viewer）
        ↓
分析失敗模式，改寫 SKILL.md
        ↓
進入下一輪迭代（iteration-2/、iteration-3/...）
        ↓
（滿意後）Description Optimization（AutoResearch）
```

---

## 第一步：設計測試案例

將測試案例存到 `evals/evals.json`，格式如下：

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "（真實用戶會說的話，含具體情境）",
      "expected_output": "（期望的輸出描述）",
      "files": []
    }
  ]
}
```

**好的測試案例原則：**
- 使用真實、具體的描述（含檔案名稱、欄位、情境背景）
- 涵蓋典型使用情境 + 邊緣案例
- 2–5 個案例即可，寧缺勿濫

**壞的測試案例（避免）：**
- 「測試我的 skill」→ 太抽象
- 「幫我整理資料」→ 沒有具體情境

---

## 第二步：Binary Eval 評分設計

為每個測試案例設計可客觀驗證的「斷言（assertions）」，每個斷言只有**通過（pass）或失敗（fail）**。

**好的斷言範例：**

| 斷言描述 | 驗證方式 |
|----------|----------|
| 產生了 .docx 檔案 | 檔案是否存在 |
| 標題出現在第一段 | 文字位置比對 |
| 摘要超過 100 字 | 字數計算 |
| 包含三個章節標題 | 標題數量計算 |

**斷言加入 evals.json 的格式：**

```json
{
  "id": 1,
  "prompt": "...",
  "assertions": [
    {
      "name": "產生了 .docx 檔案",
      "check": "file_exists",
      "expected": "output.docx"
    },
    {
      "name": "摘要超過 100 字",
      "check": "word_count_gte",
      "expected": 100
    }
  ]
}
```

支援的 `check` 類型：`file_exists`、`word_count_gte`、`contains_text`、`line_count_gte`、`json_key_exists`。
這些斷言由 `scripts/run_evals.py` 實際執行（見第三步）。

主觀性輸出（寫作風格、設計質感）不需要斷言，改用人工審閱。

---

## 第三步：執行測試（兩組平行執行）

每個測試案例跑兩個版本：

| 版本 | 說明 | 輸出目錄 |
|------|------|----------|
| **with-skill** | 有載入 skill | `iteration-N/eval-ID/with_skill/outputs/` |
| **baseline** | 沒有 skill（或舊版） | `iteration-N/eval-ID/without_skill/outputs/` |

工作目錄結構（在 skill 目錄外另建）：
```
my-skill-workspace/
├── evals/evals.json
├── iteration-1/
│   ├── eval-1/
│   │   ├── with_skill/outputs/    ← 手動或 subagent 產生的輸出
│   │   └── without_skill/outputs/
│   └── benchmark.json             ← run_evals.py 自動產生
└── iteration-2/
    └── ...
```

**執行斷言測試（自動化）：**
```bash
python ~/.claude/skills/skill-iteration-loop/scripts/run_evals.py \
  --evals evals/evals.json \
  --output-dir iteration-1/
```

---

## 第四步：人工審閱

`run_evals.py` 執行後會產生 `iteration-N/benchmark.json`，記錄每個斷言的通過/失敗。

人工審閱的重點：
- 讀 `benchmark.json`：哪些斷言失敗？是偶發還是穩定失敗？
- 直接看輸出檔案：`with_skill/outputs/` vs `without_skill/outputs/` 的差異
- 主觀判斷（格式、語氣、完整性）無法被斷言捕捉到，這部分靠肉眼

回饋越具體，下一輪改進越有效。

---

## 第五步：根據回饋改進 Skill

改進的四個原則：

1. **從回饋中找共同模式**，不要只修那一個例子（避免過擬合）
2. **解釋「為什麼」而非只給指令**——讓模型理解意圖，而不是死記規則
3. **刪掉沒用的部分**，精簡比堆砌更有效
4. **看完整執行過程**，不只看最終輸出——如果模型每次都在重複做同樣的前置作業，考慮把它打包成 scripts/

改完後進入 `iteration-2/`，重跑全部測試。

---

## 第六步：Description Optimization（AutoResearch）

> **注意**：完整自動化版本需要 Claude Code 環境（使用 `run_loop.py`）。  
> Claude.ai 可手動執行此步驟。

### 目的
優化 SKILL.md 的 `description` 欄位，讓 Claude 在對的時機觸發、在不對的時機不觸發。

### 生成觸發測試集（trigger-eval.json）

```json
{
  "skill_name": "my-skill",
  "queries": [
    {"prompt": "（不同措辭、正式/口語、不直接說 skill 名稱）", "should_trigger": true},
    {"prompt": "（關鍵字相似但實際需要別的工具）", "should_trigger": false}
  ]
}
```

設計原則：
- 應觸發（8–10 個）：用不同措辭、正式/口語表達，不直接說 skill 名稱
- 不應觸發（8–10 個）：關鍵字相似但場景不符（近似錯誤才有測試價值）

**好的查詢範例：**
```
✅ 「我老闆傳了一個 xlsx，叫我加一欄利潤率，收入在 C 欄成本在 D 欄」
❌ 「幫我寫個 Python 腳本讀取 CSV 檔案然後計算統計數據」
```

### 執行 AutoResearch 自動優化

前置需求：`pip install anthropic`

```bash
python ~/.claude/skills/skill-iteration-loop/scripts/run_loop.py \
  --skill-path ~/.claude/skills/my-skill \
  --eval-set trigger-eval.json \
  --model claude-sonnet-4-6 \
  --max-iterations 5 \
  --verbose
```

加上 `--dry-run` 可先預覽建議，不寫入 SKILL.md。

輸出：最佳 `best_description` → 自動更新到 SKILL.md frontmatter，並在 `evals/description_optimization_results.json` 儲存每輪迭代記錄。

---

## 停止迭代的條件

滿足以下任一條件即可停止：
- 你說「這樣就好了」
- 所有測試案例的回饋都是空白（沒有問題）
- 連續兩輪沒有明顯進步

---

## 在 Claude.ai 的精簡版循環

| 步驟 | Claude Code | Claude.ai |
|------|-------------|-----------|
| 執行測試 | 子代理並行 | Claude 逐一模擬執行 |
| 審閱介面 | 本地網頁 | 直接在對話中回饋 |
| 量化評分 | 自動跑斷言 | 手動檢查關鍵項目 |
| Description 優化 | run_loop.py 自動化 | 手動設計測試集 + 調整 |

核心循環不變，只是更依賴對話中的直接回饋。

---

## 快速啟動清單

新建一個 skill 的迭代循環：

- [ ] 寫好 SKILL.md 草稿
- [ ] 設計 2–5 個真實測試案例（evals.json）
- [ ] 為每個案例寫 2–4 個 Binary 斷言
- [ ] 執行 with-skill 和 baseline 測試
- [ ] 審閱輸出，留下具體回饋
- [ ] 改進 SKILL.md，進入下一輪
- [ ] 重複直到滿意
- [ ] （選用）執行 Description Optimization
