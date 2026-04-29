# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📋 專案規則

@.claude/rules/laravel-boost.md

---

## 🌐 語言設定

- 所有產生的 SKILL.md 檔案必須使用繁體中文撰寫
- 文件註解使用繁體中文
- 主要標題可以適當使用 emoji

---

## 📁 目錄架構

這是 Claude Code 的全域設定目錄，包含 skills、sessions、設定與備份。

```
~/.claude/
├── CLAUDE.md              # 本文件（全域規範）
├── settings.json          # 全域設定（hooks、permissions、env vars）
├── skills/                # 自訂技能（DBS Framework）
├── projects/              # 專案與 subagent 對話記錄
├── sessions/              # Session 狀態快照
├── backups/               # 設定檔備份（.claude.json 時間戳記版本）
├── shell-snapshots/       # Zsh 環境快照
├── ide/                   # IDE lock 檔案（避免多實例衝突）
├── agents/                # 子代理定義（獨立 context，自動委派）
└── memory/                # 持久化記憶體（跨 session 知識）
```

---

## 🛠 Skills 架構（DBS Framework）

Skills 遵循三層式 **DBS 架構**（Direction → Blueprints → Solutions）：

```
skills/<skill-name>/
├── SKILL.md               # Direction：觸發規則 + 執行流程（< 500 行）
├── references/            # Blueprints：領域知識，按需載入
│   └── <topic>.md
└── scripts/               # Solutions：需精確輸出時的執行腳本
    └── <script>.py
```

### 關鍵原則

- **SKILL.md frontmatter**：`description` 欄位決定觸發條件，需同時涵蓋英文與繁體中文關鍵詞
- **漸進式載入**：SKILL.md 只在需要時 `Read` 特定 references/ 檔案，避免一次性載入全部
- **Solutions 腳本**：只在需要一致性精確輸出時使用（如 HTML 生成、API 呼叫、驗證）；純邏輯流程不需要腳本
- **新增 skill** 時必須同步更新 `settings.json` 中的 skill 清單（透過 `update-config` skill）

### 現有 Skills

| Skill                    | 用途                                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| `commit`                 | 自動分析 diff、撰寫 Conventional Commits 並提交                                                 |
| `dbs-framework`          | 建立新 skill 的 DBS 結構指南                                                                    |
| `architronix-theme`      | 生成 Bootstrap v5.3.3 Architronix 主題 HTML 頁面                                                |
| `bootstrap-ecommerce-ui` | 電商 UI 元件（Architronix 設計語言）                                                            |
| `firecrawl-scraper`      | 使用 Firecrawl API 爬取網站資料                                                                 |
| `skill-iteration-loop`   | Binary Eval + AutoResearch 迭代優化 skill（含 `scripts/run_evals.py` 和 `scripts/run_loop.py`） |
| `yt-analyze`             | YouTube 影片深度分析系統入口（專案位於 `~/AI/Projects/YT_Analyze/`）                            |
| `Data_Insight`           | 數據洞察分析，支援 Excel/PDF/Word/TXT/CSV 檔案上傳分析                                          |
| `PPT_Maker`              | 企業級簡報生成，選擇風格、規劃架構、批量輸出 PPT                                                |
| `Social_Media_Post`      | 生成 Facebook、Threads、X、LinkedIn 優化社群貼文                                                |
| `deploy`                 | 全自動 git deploy：建立 branch、拆分 commit、建立 PR/MR、auto-merge、清除 branch（支援 GitHub/GitLab） |
| `composer-update`        | Laravel 專案 composer update 完整流程：更新套件 → boost:update → 偵測新套件 → 更新 CLAUDE.md          |
| `llm-wiki`               | 將 URL、Facebook 貼文、YouTube 影片分析後寫入 `~/AI/llm-wiki/raw/articles/`                           |
| `add-agent`              | 新增 subagent 並自動同步更新 `AGENTS.md` 與 `CLAUDE.md`                                                |
| `session-todo`           | 工作 session 任務管理：開工建立 `todo/YYYY-MM-DD_HH-MM.md`、收工標記完成、支援 PRD 討論後續任務       |

---

## 🤖 Agents（子代理）

每個 agent 在 `~/.claude/agents/` 下定義為獨立 `.md` 檔案，擁有獨立 context window。詳見 [agents/AGENTS.md](agents/AGENTS.md)。

| Agent | 用途 |
|-------|------|
| `code-reviewer` | 程式碼品質審查，含嚴重性分級 |
| `debugger` | 系統性除錯，找根因而非掩蓋問題 |
| `test-writer` | 撰寫測試，涵蓋正常、邊界、錯誤路徑 |
| `refactorer` | 重構程式碼，行為不變、步驟小 |
| `doc-writer` | 撰寫技術文件與 README，繁體中文優先 |
| `security-auditor` | 安全稽核，OWASP Top 10 為基礎 |
| `frontend-tester` | 透過 Chrome Extension 操控瀏覽器進行前台 UI 與使用者流程測試 |
| `requirements-planner` | 需求訪談、功能拆解、撰寫 PRD 文件 |

---

## ⚙️ settings.json

自動化行為（「每次 X 時執行 Y」）必須透過 `hooks` 設定，由 harness 執行，無法僅靠記憶實現。使用 `update-config` skill 修改設定，而非直接手動編輯。

---

## 🧠 Memory 系統

`memory/` 目錄儲存跨 session 持久知識，分四類：`user`、`feedback`、`project`、`reference`。索引在 `memory/MEMORY.md`。
