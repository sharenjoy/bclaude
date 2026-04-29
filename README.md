# bclaude

Personal Claude Code configuration installer — skills, agents, rules, hooks.

## Install

```bash
# Interactive mode（推薦）
npx bclaude

# 依 Profile 安裝
npx bclaude --profile laravel
npx bclaude --profile fullstack
npx bclaude --profile general

# 手動指定 Skills
npx bclaude --skills commit,deploy,llm-wiki

# 全裝
npx bclaude --profile all

# 預覽（不寫入）
npx bclaude --dry-run --profile laravel

# 覆蓋已存在的檔案
npx bclaude --profile laravel --force
```

## Profiles

| Profile    | Skills                                                                   |
| ---------- | ------------------------------------------------------------------------ |
| `general`  | commit, deploy, dbs-framework, find-skills, session-todo, llm-wiki       |
| `laravel`  | general + composer-update                                                |
| `fullstack`| general + firecrawl-scraper, skill-iteration-loop                        |
| `content`  | commit, dbs-framework, find-skills, yt-analyze, llm-wiki, Social_Media_Post, PPT_Maker |
| `all`      | 全部 skills                                                              |

## Available Skills

| Skill                 | 說明                                          |
| --------------------- | --------------------------------------------- |
| `commit`              | 自動分析 diff、撰寫 Conventional Commits      |
| `deploy`              | 全自動 git deploy：branch → PR → merge        |
| `dbs-framework`       | 建立新 skill 的 DBS 結構指南                  |
| `find-skills`         | 幫助發現與安裝 agent skills                   |
| `add-agent`           | 新增 subagent 並同步更新 AGENTS.md            |
| `session-todo`        | 工作 session 任務管理                         |
| `skill-iteration-loop`| Binary Eval + AutoResearch 迭代優化 skill     |
| `llm-wiki`            | 將 URL/YouTube 分析後寫入知識庫               |
| `firecrawl-scraper`   | 使用 Firecrawl API 爬取網站資料               |
| `composer-update`     | Laravel composer update 完整流程              |
| `yt-analyze`          | YouTube 影片深度分析                          |
| `Data_Insight`        | 數據洞察分析，支援 Excel/PDF/CSV              |
| `PPT_Maker`           | 企業級簡報生成                                |
| `Social_Media_Post`   | 生成 Facebook/Threads/X/LinkedIn 貼文        |

## Post-install Notes

部分 skills 需要額外安裝 Python 套件：

```bash
# Data_Insight
cd ~/.claude/skills/Data_Insight && pip install -r requirements.txt

# PPT_Maker
cd ~/.claude/skills/PPT_Maker && pip install -r requirements.txt
```

## Agents

安裝後 `~/.claude/agents/` 會包含以下 sub-agents：
`code-reviewer`, `debugger`, `doc-writer`, `frontend-tester`, `refactorer`, `requirements-planner`, `security-auditor`, `test-writer`

## Update

```bash
npx bclaude@latest --profile laravel --force
```

---

## For Maintainers — 維護同步機制

本專案設計為從 `~/.claude` 自動同步，共三層機制：

### 層 1 — 手動同步指令

```bash
npm run sync          # 只同步檔案（不 commit）
npm run sync:commit   # 同步 + git commit
npm run sync:push     # 同步 + git commit + npm publish
```

同步範圍：

| 來源 `~/.claude/` | 目的地（本專案） |
|---|---|
| `skills/` | `skills/` |
| `agents/` | `agents/` |
| `rules/` | `rules/` |
| `scripts/` | `scripts/` |
| `claude.md` | `templates/CLAUDE.md` |
| `settings.json` | `templates/settings.json` |

### 層 2 — PostToolUse Hook（自動觸發）

在 `~/.claude/settings.json` 已設定 hook：每當 Claude 修改 `~/.claude/skills/`、`agents/`、`rules/`、`scripts/` 內的任何檔案，自動在背景執行 `sync.js`。

Log 輸出至：`/tmp/bclaude-sync.log`

### 層 3 — GitHub Actions（push 自動發佈）

推送到 `main` branch，只要以下任一路徑有變動，自動執行：

`skills/` · `agents/` · `rules/` · `scripts/` · `templates/` · `src/` · `bin/` · `profiles.json` · `skills-registry.json` · `package.json`

1. `npm version patch`
2. `npm publish --access public`（使用 NPM_TOKEN，無需 OTP）
3. 將 version bump commit 推回 repo

**啟用前置步驟：**

```bash
# 1. 取得 npm Access Token（Automation 類型，不需要 OTP）
# 前往 https://www.npmjs.com/settings/<your-name>/tokens → Generate New Token → Automation

# 2. 到 GitHub repo → Settings → Secrets and variables → Actions
# 新增 secret：NPM_TOKEN = <貼上 token>
```

設定完成後，每次 push 到 main 即自動發佈新版本。

### 手動發佈

不透過 GitHub Actions，直接在本機發佈：

```bash
npm version patch
npm publish --access public --otp=<你的6位數驗證碼>
```

> OTP 驗證碼請從你的 Authenticator App 取得。
