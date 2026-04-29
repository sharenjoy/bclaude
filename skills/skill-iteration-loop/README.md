# skill-iteration-loop

自動優化 SKILL.md `description` 欄位，讓 Claude 在對的時機觸發、在不對的時機不觸發。

## 快速開始

進到 skill 目錄，準備好 `trigger-eval.json` 後執行：

```bash
skill-loop
```

預設使用 **Claude Code CLI**（走 Claude Pro 訂閱，不需要 API credits）。

---

## 前置需求

- 已安裝 Claude Code CLI（`claude` 指令可用）
- shell alias 已加入 `~/.zshrc`（見下方設定）

```bash
alias skill-loop='python3 ~/.claude/skills/skill-iteration-loop/scripts/run_loop.py'
```

---

## trigger-eval.json 格式

在 skill 目錄下建立 `trigger-eval.json`：

```json
{
  "skill_name": "my-skill",
  "queries": [
    {"prompt": "（使用者說的話，應觸發 skill）", "should_trigger": true},
    {"prompt": "（關鍵字相似但不該觸發的情境）", "should_trigger": false}
  ]
}
```

建議：應觸發 8–10 個、不應觸發 8–10 個，用不同措辭、正式／口語都要涵蓋。

---

## 指令用法

```bash
# 基本執行（當前目錄 + trigger-eval.json）
skill-loop

# 顯示每個測試案例的通過／失敗
skill-loop --verbose

# 先預覽，不寫入 SKILL.md
skill-loop --dry-run

# 指定不同的 eval 檔案
skill-loop --eval-set my-evals.json

# 指定不同的 skill 目錄
skill-loop --skill-path ~/.claude/skills/my-skill

# 調整迭代次數與目標通過率
skill-loop --max-iterations 3 --target-score 0.85
```

### 使用 Anthropic API（需要 API credits）

```bash
skill-loop --api
skill-loop --api --model claude-haiku-4-5-20251001  # 較便宜的模型
```

---

## 完整參數說明

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `--skill-path` | `./` | Skill 目錄路徑 |
| `--eval-set` | `trigger-eval.json` | 測試集檔案路徑 |
| `--api` | 否（使用 CLI） | 改用 Anthropic API |
| `--model` | `claude-sonnet-4-6` | 模型 ID（僅 `--api` 有效） |
| `--max-iterations` | `5` | 最大迭代次數 |
| `--target-score` | `0.9` | 目標通過率（0–1） |
| `--verbose` | 否 | 顯示每個測試案例結果 |
| `--dry-run` | 否 | 不寫入 SKILL.md |

---

## 輸出結果

每次執行完成後，結果會儲存至：

```
<skill-path>/evals/description_optimization_results.json
```

包含每輪迭代的通過率與 description 變化記錄。
