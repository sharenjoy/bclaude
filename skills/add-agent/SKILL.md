---
name: add-agent
description: 新增 Claude Code subagent 並自動同步更新 AGENTS.md 與 CLAUDE.md。當使用者說「新增 agent」、「add agent」、「建立 agent」、「我要加一個 agent」或輸入 /add-agent 時觸發。
---

# Add Agent Skill

新增一個 subagent 並自動同步所有索引文件。

## 執行流程

### Step 1 — 收集資訊

若使用者未提供，逐一詢問：

1. **agent 名稱**（小寫 + 連字號，如 `api-tester`）
2. **用途描述**（一句話，英文為主，涵蓋觸發關鍵詞）
3. **需要哪些工具**（提供選項讓使用者選擇）：
   - 🔒 Read-Only：`Read, Grep, Glob`
   - 📝 Read + Write：`Read, Write, Edit, Grep, Glob`
   - ⚡ Read + Write + Execute：`Read, Write, Edit, Grep, Glob, Bash`
   - 自訂（讓使用者指定）
4. **maxTurns**（預設依權限層級：Read-Only=20、Read+Write=25、Execute=30）
5. **agent 的主要職責說明**（用於 system prompt 內容）

### Step 2 — 建立 Agent 檔案

在 `~/.claude/agents/<name>.md` 建立內容：

```markdown
---
name: <name>
description: <description>
tools: <tools>
model: sonnet
memory: project
maxTurns: <maxTurns>
---

<system prompt 內容，繁體中文撰寫>
```

System prompt 結構：
- 第一行：角色定位（「你是一位...」）
- 核心職責區塊（## 職責）
- 執行原則（## 原則）
- 輸出格式（## 輸出格式）

### Step 3 — 更新 AGENTS.md

讀取 `~/.claude/agents/AGENTS.md`，在現有 Agent 表格新增一行：

```
| [<name>](<name>.md) | <觸發情境> | <tools> | sonnet |
```

### Step 4 — 更新 CLAUDE.md

讀取 `~/.claude/CLAUDE.md`，在 `## 🤖 Agents` 區塊的表格新增一行：

```
| `<name>` | <一行用途說明> |
```

### Step 5 — 確認完成

回報：
- ✅ 已建立 `~/.claude/agents/<name>.md`
- ✅ 已更新 `AGENTS.md`
- ✅ 已更新 `CLAUDE.md`
- 提示使用者若需要，可手動更新 `ARCHITECTURE.md` 的分層分類

## 權限分層判斷

| 包含工具 | 分層 | 建議 maxTurns |
|---------|------|--------------|
| 無 Bash、無 Write/Edit | 🔒 Read-Only | 20 |
| 有 Write/Edit、無 Bash | 📝 Read+Write | 25 |
| 有 Bash | ⚡ Read+Write+Execute | 30 |

## 注意事項

- agent 名稱不可與現有 agent 重複，執行前先檢查 `~/.claude/agents/` 目錄
- description 欄位決定 Claude 自動委派的觸發條件，需清楚且具體
- system prompt 使用繁體中文撰寫
