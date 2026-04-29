# 🤖 Agents 使用指南

`~/.claude/agents/` 目錄下的每個 `.md` 檔案定義一個子代理（subagent）。  
每個 agent 擁有**獨立的 context window**，不污染主對話，適合專責任務。

---

## 📋 現有 Agents

| Agent | 觸發情境 | tools | model |
|-------|----------|-------|-------|
| [code-reviewer](code-reviewer.md) | 審查程式碼品質、PR review | Read, Grep, Glob | sonnet |
| [debugger](debugger.md) | 除錯、分析錯誤訊息與 stack trace | Read, Grep, Glob, Bash | sonnet |
| [test-writer](test-writer.md) | 撰寫單元測試、整合測試 | Read, Write, Edit, Grep, Glob, Bash | sonnet |
| [refactorer](refactorer.md) | 重構程式碼結構（不改變行為） | Read, Write, Edit, Grep, Glob | sonnet |
| [doc-writer](doc-writer.md) | 撰寫技術文件、README、API 說明 | Read, Write, Edit, Grep, Glob | sonnet |
| [security-auditor](security-auditor.md) | 安全稽核、OWASP 漏洞檢查 | Read, Grep, Glob | sonnet |
| [frontend-tester](frontend-tester.md) | 瀏覽器前台 UI 測試、使用者流程驗證 | Bash, Read, Grep, Glob | sonnet |
| [requirements-planner](requirements-planner.md) | 需求訪談、功能拆解、撰寫 PRD 文件 | Read, Write, Edit, Grep, Glob | sonnet |

---

## 🚀 使用方式

### 自動委派（推薦）

直接描述任務，Claude 會根據 agent 的 `description` 自動判斷是否委派：

```
幫我 review 這段程式碼的品質
→ 自動委派給 code-reviewer

這個函式有 bug，錯誤訊息是 TypeError: ...
→ 自動委派給 debugger

幫我對 UserService 寫測試
→ 自動委派給 test-writer
```

### 明確指定

若要強制使用特定 agent：

```
用 security-auditor 檢查這段程式碼
請 refactorer 幫我重構這個 class
```

---

## 🔧 新增 Agent

1. 在 `~/.claude/agents/` 建立 `<name>.md`
2. 加入 YAML frontmatter：

```markdown
---
name: your-agent-name
description: 清楚描述何時觸發此 agent（英文與繁中關鍵詞都要涵蓋）
---

你的 agent 系統提示內容...
```

3. 更新本文件的 Agent 列表

---

## 📌 與 Skills 的差異

| | Skills (`skills/`) | Agents (`agents/`) |
|--|--------------------|--------------------|
| 觸發方式 | 使用者手動 `/slash` 指令 | Claude 自動委派或使用者指定 |
| Context | 共用主對話 context | 獨立 context window |
| 支援子目錄 | ✅ `references/`, `scripts/` | ❌ 單一 `.md` 檔案 |
| 適合場景 | 結構化工作流程 | 專責分析與產出任務 |
