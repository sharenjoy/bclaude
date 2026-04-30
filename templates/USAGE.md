# 🗺️ Claude Code 使用流程指南

> 本文件說明 `~/.claude/` 目錄的完整使用方式，包含日常工作流程、所有 Skills 與 Agents 的觸發時機，以及系統的擴充方法。
>
> ⚡ **Rules 表格、Skills 表格、Agents 表格、Hooks、Permissions 五個區塊會在架構檔案異動後自動更新。**

---

## 📁 目錄總覽

```
~/.claude/
├── CLAUDE.md          # 全域規範（每次對話自動載入）
├── USAGE.md           # 本文件：使用流程指南
├── settings.json      # Hooks、Permissions 設定
├── rules/             # 專案規則（@import 至 CLAUDE.md）
│   └── laravel-boost.md
├── skills/            # 手動觸發的工作流程（/slash 指令）
├── agents/            # 自動委派的專責子代理
├── memory/            # 跨 session 持久記憶
├── scripts/           # 自動化腳本（如 update_usage.py）
└── plugins/           # 已安裝的插件
```

### 📋 Rules 清單

Rules 透過 `@import` 載入 CLAUDE.md，對所有對話生效。

<!-- AUTO:RULES_START -->
| 檔案 | 規則名稱 | 說明 |
|------|----------|------|
| `laravel-boost.md` | Laravel Boost 規則 | 當使用者說「更新 boost」或「update boost」時，**必須執行**以下指令： |
<!-- AUTO:RULES_END -->

---

## 🔄 日常工作流程

### 1. 開發功能

```
寫程式碼
  → Claude 直接協助（主對話）
  → 需要重構？說「幫我重構這段」→ refactorer agent 接手
  → 需要文件？說「幫我寫 README」→ doc-writer agent 接手
```

### 2. 提交程式碼

```
/commit
  → 自動分析 git diff
  → 依變更類型分組
  → 撰寫 Conventional Commits 格式訊息
  → 自動 stage + commit
```

### 3. 部署上線

```
/deploy
  → 建立 branch → 拆分 commit → 建立 PR/MR → auto-merge → 清除 branch
  → 支援 GitHub / GitLab
```

### 4. 程式碼審查

```
「幫我 review 這個 PR」或「審查這段程式碼」
  → code-reviewer agent 接手
  → 輸出：[critical] / [suggestion] / [nit] 分級報告 + 整體評分
```

### 5. 除錯

```
「這裡有 bug，錯誤是 TypeError: ...」
  → debugger agent 接手
  → 流程：理解症狀 → 縮小範圍 → 假設根因 → 驗證 → 修復
```

### 6. 前台測試

```
「幫我測試登入頁面的流程」
  → frontend-tester agent 接手
  → 透過 Chrome Extension 操控瀏覽器
  → 輸出：結構化測試報告（✅ 通過 / ❌ 失敗 / ⚠️ 待確認）
```

### 7. 安全稽核

```
「做一次安全審查」或「檢查這段程式碼有沒有漏洞」
  → security-auditor agent 接手
  → 以 OWASP Top 10 為基礎
  → 輸出：風險等級 + 攻擊情境 + 修復方案
```

### 8. 任務管理（session-todo + PRD 完整流程）

**新專案啟動：**
```
「幫我寫 PRD」或「規劃需求」
  → requirements-planner agent 訪談需求
  → 自動儲存 PRD.md（或 docs/PRD.md）至當前專案目錄

「開工」
  → session-todo 讀取 todo/ 目錄
  → 若找到 PRD.md，討論任務時自動比對未完成功能
  → 建立 todo/YYYY-MM-DD_HH-MM.md，列出本次任務
```

**日常工作循環：**
```
「開工」
  → 建立新 session 檔，帶入上次未完成任務

（工作中）

「收工」
  → 詢問哪些完成了 → 標記 [x]
  → 詢問下次要做什麼 → 記入下次待辦
  → 儲存 todo/YYYY-MM-DD_HH-MM.md
```

**查看進度：**
```
「任務清單」或「目前進度」
  → 顯示進行中 session、最近完成、待辦積壓
```

**討論後續規劃：**
```
「討論任務」
  → session-todo 讀取 PRD.md
  → 比對已完成 session，找出 PRD 尚未排入的功能
  → 主動建議並幫你拆解為子任務
```

---

## 🛠️ Skills 完整清單

Skills 需要**手動觸發**（`/skill-name` 或描述觸發關鍵詞）。

<!-- AUTO:SKILLS_START -->
| Skill | 用途 |
|-------|------|
| `data-insight-orchestrator` | 數據洞察分析 skill |
| `ppt` | 企業級簡報生成工具 |
| `social-media-post` | 為 Facebook、Threads、X (Twitter) 和 LinkedIn 生成優化的社群媒… |
| `add-agent` | 新增 Claude Code subagent 並自動同步更新 AGENTS |
| `commit` | Automatically reads git diff, groups changes, writ… |
| `composer-update` | 在 Laravel 專案中執行完整的 composer update 流程 |
| `dbs-framework` | Use this skill whenever the user wants to create a… |
| `deploy` | Automates the full git deploy flow end-to-end with… |
| `find-skills` | Helps users discover and install agent skills when… |
| `firecrawl-scraper` | 使用 Firecrawl API 爬取網站資料的技能 |
| `llm-wiki` | 將資源寫入 llm-wiki 知識庫 |
| `session-todo` | 工作 session 任務管理系統 |
| `skill-iteration-loop` | 使用 AutoResearch + Binary Eval 迭代改進 Skill 的完整流程指南 |
| `YT Analyze` | YouTube 影片深度分析系統入口 |
<!-- AUTO:SKILLS_END -->

### Laravel 專案特別規則

在任何 Laravel 專案目錄中，說「**更新 boost**」或「**update boost**」會自動執行：

```bash
php artisan boost:update --discover
```

---

## 🤖 Agents 完整清單

Agents 由 Claude **自動委派**（也可明確指定）。每個 agent 有獨立 context window。  
詳細觸發情境與使用範例見 [agents/AGENTS.md](agents/AGENTS.md)。

<!-- AUTO:AGENTS_START -->
| Agent | tools | 權限層級 | maxTurns |
|-------|-------|---------|---------|
| `code-reviewer` | Read, Grep, Glob | 🔒 Read-Only | 20 |
| `debugger` | Read, Grep, Glob, Bash | ⚡ +Bash | 30 |
| `doc-writer` | Read, Write, Edit, Grep, Glob | 📝 +Write | 20 |
| `frontend-tester` | Bash, Read, Grep, Glob | ⚡ +Bash | 30 |
| `refactorer` | Read, Write, Edit, Grep, Glob | 📝 +Write | 25 |
| `requirements-planner` | Read, Write, Edit, Grep, Glob | 📝 +Write | 25 |
| `security-auditor` | Read, Grep, Glob | 🔒 Read-Only | 20 |
| `test-writer` | Read, Write, Edit, Grep, Glob, Bash | ⚡ +Bash | 30 |
<!-- AUTO:AGENTS_END -->

**明確指定 agent：**

```
用 security-auditor 檢查這段程式碼
請 refactorer 幫我重構這個 class
讓 frontend-tester 測試購物車流程
```

**新增 agent：**

```
/add-agent
```

---

## 🔔 自動化行為（Hooks）

<!-- AUTO:HOOKS_START -->
| 事件 | 行為 |
|------|------|
| Claude 需要回應（Notification） | command |
| Claude 完成任務（Stop） | command |
| 工具執行前（PreToolUse） | command（matcher: AskUserQuestion） |
| 工具執行後（PostToolUse） | command（matcher: Write|Edit） |
| 工具執行後（PostToolUse） | command（matcher: Write|Edit） |
<!-- AUTO:HOOKS_END -->

---

## 🔐 權限設定

<!-- AUTO:PERMISSIONS_START -->
### 自動允許（不提示）

```
Bash(git add:*)
Bash(git commit:*)
Bash(php artisan:*)
Bash(npm run:*)
Bash(composer:*)
WebSearch
WebFetch
```

### 永遠拒絕

```
Bash(git push:*)
Bash(rm -rf:*)
Bash(php artisan db:wipe:*)
Bash(sudo *)
```
<!-- AUTO:PERMISSIONS_END -->

---

## 🧠 Memory 系統

Memory 儲存跨 session 的持久知識，分四類：

| 類型 | 用途 | 位置 |
|------|------|------|
| `user` | 你的角色、偏好、技術背景 | `memory/user_*.md` |
| `feedback` | 你給 Claude 的行為糾正 | `memory/feedback_*.md` |
| `project` | 進行中的專案脈絡 | `memory/project_*.md` |
| `reference` | 外部系統位置（Linear、Grafana 等） | `memory/reference_*.md` |

**主動記憶：** 說「幫我記住...」即可儲存。  
**主動遺忘：** 說「忘掉...」即可刪除。

索引在 [memory/MEMORY.md](memory/MEMORY.md)。

---

## 🔧 擴充系統

### 新增 Skill

```
/dbs-framework
```

依照 DBS 三層架構（Direction → Blueprints → Solutions）建立新 skill。

### 新增 Agent

```
/add-agent
```

自動建立 `~/.claude/agents/<name>.md` 並同步更新索引文件。

### 修改設定

```
「加入 X 的自動允許權限」
「設定每次 Claude 停止後執行 Y」
```

→ 觸發 `update-config` skill，自動修改 `settings.json`。

---

## 📌 快速參考卡

```
日常提交        → /commit
推上遠端 + PR   → /deploy
Laravel 套件    → /composer-update
爬網站          → /firecrawl-scraper 或說「爬取 <URL>」
存知識          → /llm-wiki 或說「寫入 wiki」
分析資料        → 上傳檔案並說「分析這份資料」
做簡報          → 說「製作簡報」
新增 agent      → /add-agent
新增 skill      → /dbs-framework
開工            → 說「開工」（session-todo）
收工            → 說「收工」（session-todo）
規劃需求 + PRD  → 說「寫 PRD」（requirements-planner → 自動存 PRD.md）
```

---

## 📚 延伸閱讀

- [CLAUDE.md](CLAUDE.md) — 全域規範與 skills/agents 索引
- [agents/AGENTS.md](agents/AGENTS.md) — Agent 詳細說明與使用範例
- [agents/ARCHITECTURE.md](agents/ARCHITECTURE.md) — Agent 架構圖（Mermaid）
- [memory/MEMORY.md](memory/MEMORY.md) — 跨 session 記憶索引
