# 🤖 Agent Team Architecture

```mermaid
graph TD
    User(["👤 User"])
    Claude["☁️ Claude\nMain Conversation"]

    User -->|"任務描述"| Claude
    Claude -->|"自動委派\n依 description 判斷"| Agents

    subgraph Agents["~/.claude/agents/"]
        direction TB

        subgraph RO["🔒 Read-Only（純分析）"]
            CR["**code-reviewer**\nRead · Grep · Glob\nmaxTurns: 20"]
            SA["**security-auditor**\nRead · Grep · Glob\nmaxTurns: 20"]
        end

        subgraph RW["📝 Read + Write（分析 + 產出）"]
            RF["**refactorer**\nRead · Write · Edit · Grep · Glob\nmaxTurns: 25"]
            DW["**doc-writer**\nRead · Write · Edit · Grep · Glob\nmaxTurns: 20"]
        end

        subgraph RWX["⚡ Read + Write + Execute（迭代驗證）"]
            DB["**debugger**\nRead · Grep · Glob · Bash\nmaxTurns: 30"]
            TW["**test-writer**\nRead · Write · Edit · Grep · Glob · Bash\nmaxTurns: 30"]
        end
    end

    CR --> Codebase[("📁 Codebase")]
    SA --> Codebase
    RF --> Codebase
    DW --> Codebase
    DB --> Codebase
    TW --> Codebase
    DB --> Terminal["💻 Terminal"]
    TW --> Terminal

    subgraph Memory["🧠 memory: project"]
        M1["專案慣例\n跨 session 持久"]
    end

    Agents -.->|"記憶專案脈絡"| Memory

    style RO fill:#fef3c7,stroke:#d97706
    style RW fill:#dbeafe,stroke:#2563eb
    style RWX fill:#dcfce7,stroke:#16a34a
    style Memory fill:#f3e8ff,stroke:#7c3aed
```

## 權限分層說明

| 層級 | Agents | 可執行動作 |
|------|--------|-----------|
| 🔒 Read-Only | code-reviewer, security-auditor | 讀取、搜尋 |
| 📝 Read + Write | refactorer, doc-writer | 讀取、搜尋、修改檔案 |
| ⚡ Read + Write + Execute | debugger, test-writer | 讀取、搜尋、修改檔案、執行指令 |
