---
name: session-todo
description: 工作 session 任務管理系統。當使用者說「開工」、「收工」、「停工」、「打完收工」、「今天要做什麼」、「列出任務」、「任務清單」、「我要開始工作」、「工作結束」、「start work」、「end work」、「session-todo」、「目前進度」、「現在要做什麼」、「顯示 todo」時觸發。在 todo/ 目錄下為每次 session 建立獨立 md 檔（以日期時間命名），以 session（每次開工/收工）為單位追蹤任務，保有完整歷史，支援 PRD 參照討論後續任務。
---

# Session Todo — 工作任務管理

以「session」（每次開工到收工）為單位的任務追蹤系統。每次開工在 `todo/` 目錄下建立一個以日期時間命名的 md 檔，同一天可以有多個 session，所有歷史完整保留。

## 觸發指令對照

| 使用者說 | 執行流程 |
|----------|----------|
| 開工 / start work / 我要開始工作 | → 開工流程 |
| 收工 / end work / 工作結束 | → 收工流程 |
| 任務清單 / 現在要做什麼 / 目前進度 | → 顯示任務流程 |
| 打完收工 | → 快速收工流程（所有任務標為完成，無互動，直接結束） |
| 停工 | → 強制收工流程（任務維持現狀，無互動，直接結束） |
| 討論任務 / 後續要做什麼 | → 討論任務流程 |

---

## 流程一：開工

### Step 1 — 確認 todo/ 目錄
```bash
pwd
ls -la todo/ 2>/dev/null || echo "not found"
```
- 若 `todo/` 不存在 → 詢問使用者「找不到 todo/ 目錄，是否在此目錄建立？」，確認後 `mkdir todo`

### Step 2 — 計算 Session 編號
```bash
ls todo/*.md 2>/dev/null | wc -l
```
- Session 編號 = 現有 md 檔數量 + 1（從 #1 開始）

### Step 3 — 尋找上次未完成的任務
- 找出 `todo/` 中最新的 md 檔（按檔名排序取最後一個）
- 讀取該檔，找出「⏸ 未完成」區塊下所有 `- [ ]` 項目
- 若最新檔沒有收工時間 → 提示使用者：「上次 session 似乎未收工（`上次檔名`），是否先處理收工？」

### Step 3.5 — 從 Apple Reminders 拉取待辦
載入整合指引：`references/apple-reminders.md`

```bash
osascript -e 'tell application "Reminders" to get name of reminders of list "工作" whose completed is false'
```

- 若無輸出 → 跳過此步驟
- 若有輸出 → 顯示編號清單讓使用者選擇要帶入哪幾個
- 選取的任務加上 `[R]` 前綴帶入本次 session
- 說「不用」→ 跳過

### Step 4 — 建立新 Session 檔案
載入格式規範：`references/todo-format.md`

檔名格式：`todo/YYYY-MM-DD_HH-MM.md`（使用開工的當前日期時間）

寫入初始內容：
```markdown
# Session #N — YYYY-MM-DD HH:MM 開工

## 🎯 本次任務
- [ ] （從上次未完成帶入，若無則等使用者補充）
```

### Step 5 — 回覆使用者
```
🚀 Session #N 開工！YYYY-MM-DD HH:MM
📄 todo/YYYY-MM-DD_HH-MM.md

📌 本次任務：
1. [ ] 任務 A（來自上次）
2. [ ] 任務 B（來自上次）

（若無待辦）：目前沒有待辦任務，要新增這次的目標嗎？
```

---

## 流程二：收工

### Step 1 — 找到進行中的 Session 檔案
```bash
ls -t todo/*.md 2>/dev/null | head -1
```
- 讀取最新的 md 檔
- 確認檔案**沒有** `🕐 收工：` 行 → 這是進行中的 session
- 若有收工時間 → 回覆「找不到進行中的 session，是否先執行開工？」

### Step 2 — 互動式確認完成項目
列出本次任務，詢問哪些完成：

```
📋 Session #N 任務：
1. [ ] 任務 A
2. [ ] 任務 B
3. [ ] 任務 C

哪些完成了？（說「1 2」或「全部」或「都沒有」）
```

等待使用者回覆。

### Step 3 — 詢問下次任務
完成確認後，詢問：
```
下次 session 還需要做什麼？
（新增、調整、或說「沒有了」）
```
若專案有 PRD，參照 `references/prd-integration.md` 主動建議後續任務。

### Step 4 — 更新 Session 檔案
載入格式規範：`references/todo-format.md`

以完整格式更新 md 檔，包含：
- `## ✅ 已完成`：標記 `[x]` 的項目
- `## ⏸ 未完成（移至下次）`：未完成的 `[ ]` 項目
- `## 📝 下次待辦`：使用者說的下次要做的事
- 最後一行加上 `🕐 收工：HH:MM`

### Step 4.5 — 同步完成狀態回 Apple Reminders
載入整合指引：`references/apple-reminders.md`

- 找出本次任務中所有 `[x] [R]` 項目（完成且來自 Reminders）
- 取得原始名稱（去掉 `[R] ` 前綴）
- 對每筆執行 AppleScript 標記完成
- 未完成的 `[R]` 任務不做操作（保留在 Reminders 原狀）

### Step 5 — 回覆收工摘要
```
✅ Session #N 收工！HH:MM

本次完成（N 項）：
- [x] 任務 A
- [x] 任務 B

未完成（下次繼續）：
- [ ] 任務 C

下次待辦：
- [ ] 新任務 D

📄 已儲存至 todo/YYYY-MM-DD_HH-MM.md
```

---

## 流程三：顯示任務清單

1. 列出 `todo/` 下所有 md 檔（按時間排序）
2. 讀取最新 2-3 個 session 的內容
3. 整理並顯示：
   - **進行中 session**（若有，無收工時間）：目前任務
   - **最近完成**：最後已收工 session 的摘要
   - **待辦積壓**：最新未完成的所有 `[ ]` 項目

---

## 流程五：打完收工（快速收工）

執行流程二，但跳過所有互動：
1. 找到進行中 session（同流程二 Step 1）
2. 將所有 `[ ]` 任務直接標為 `[x]`（不詢問）
3. 同步 `[R]` 項目回 Apple Reminders（同流程二 Step 4.5）
4. 寫入收工時間，下次待辦欄位填「（無）」
5. 輸出完成摘要，結束

---

## 流程四：討論任務

1. 讀取最新 session 的待辦項目
2. 載入 PRD 整合指引：`references/prd-integration.md`
3. 尋找並讀取 PRD 文件（若存在）
4. 與使用者討論後續任務，建議優先順序、拆解大任務
5. 使用者確認後，更新目前 session 的「📝 下次待辦」區塊

---

## 流程六：停工（強制收工）

執行流程二，但跳過所有互動：
1. 找到進行中 session（同流程二 Step 1）
2. 任務狀態維持原樣（`[ ]` 保留為 `[ ]`，不詢問）
3. 同步已完成 `[R]` 項目回 Apple Reminders（同流程二 Step 4.5）
4. 寫入收工時間，下次待辦欄位填「（無）」
5. 輸出摘要，結束

---

## 硬性規則

- `todo/` 目錄**一律在當前工作目錄**（不是 ~/.claude/）
- 每次開工建立**一個新的 md 檔**，不覆蓋舊檔
- Session 以「每次開工/收工」為單位，**與日期天數無關**，同天可有多個 session
- **不刪除**任何歷史 session 檔案
- 若使用者未明確告知哪些完成，**必須逐項詢問**，不自動假設
- 寫入前先讀取最新版本，避免覆蓋衝突
