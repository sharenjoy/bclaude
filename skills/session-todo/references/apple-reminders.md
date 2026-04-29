# Apple Reminders 整合指引

清單名稱：`工作`
同步方向：雙向（開工拉入 → 收工標記完成）
新任務：session 自己新增的任務**不回寫** Reminders

---

## 標記規則

來自 Reminders 的任務在 session md 中加上 `[R]` 前綴：

```markdown
- [ ] [R] 準備週報        ← 來自 Reminders，收工時會同步狀態
- [ ] 自己新增的任務       ← 不回寫 Reminders
```

收工時靠 `[R]` 識別哪些任務需要同步回去。

---

## AppleScript 指令

### 讀取未完成任務

```bash
osascript -e 'tell application "Reminders" to get name of reminders of list "工作" whose completed is false'
```

輸出格式：`任務A, 任務B, 任務C`（逗號分隔）
若清單為空：無輸出

### 標記單筆任務為完成

```bash
osascript -e 'tell application "Reminders" to set completed of reminder "任務名稱" of list "工作" to true'
```

注意：`任務名稱` 必須與 Reminders 中的名稱**完全一致**（去掉 `[R] ` 前綴後的文字）。

### 批次標記多筆完成（shell loop）

```bash
for task in "任務A" "任務B"; do
  osascript -e "tell application \"Reminders\" to set completed of reminder \"$task\" of list \"工作\" to true"
done
```

---

## 開工整合流程（嵌入流程一 Step 3 之後）

### Step 3.5 — 從 Apple Reminders 拉取待辦

執行：
```bash
osascript -e 'tell application "Reminders" to get name of reminders of list "工作" whose completed is false'
```

**若無輸出**（清單為空）：跳過，繼續建立 session 檔案。

**若有輸出**：將逗號分隔的結果轉成編號清單，顯示給使用者選擇：

```
📱 Apple Reminders「工作」清單有 N 個待辦：
1. 準備週報
2. 回覆 A 廠商 email
3. 更新專案文件

要帶入哪幾個？（說「1 3」、「全部」或「不用」）
```

等待使用者回覆後：
- 選取的任務加入 session，加上 `[R]` 前綴
- 未選的任務不帶入（仍留在 Reminders）
- 說「不用」→ 跳過，不帶入任何 Reminders 任務

---

## 收工整合流程（嵌入流程二 Step 4 之後）

### Step 4.5 — 同步完成狀態回 Reminders

1. 從本次 session 任務中找出所有 `[R]` 前綴且被標記為 `[x]` 的任務
2. 取得原始任務名稱（去掉 `[R] ` 前綴）
3. 對每個任務執行 AppleScript 標記完成
4. 若執行失敗（任務名稱不符等）：不中斷流程，在收工摘要補一行警示

範例同步摘要：
```
📱 已同步至 Apple Reminders：
- [x] 準備週報 ✓
- [x] 回覆 A 廠商 email ✓
```

**未完成的 `[R]` 任務不做任何操作**（保留在 Reminders 原狀）。

---

## 錯誤處理

| 狀況 | 處理方式 |
|------|----------|
| Reminders app 未開啟 | osascript 會自動啟動，通常不需處理 |
| 「工作」清單不存在 | 輸出錯誤，跳過 Reminders 步驟，告知使用者 |
| 任務名稱在 Reminders 中找不到 | 跳過該筆，繼續同步其他任務，摘要中標示 `⚠️ 找不到` |
| 權限被拒絕 | 提示使用者在系統設定中允許 Terminal/Claude Code 存取提醒事項 |
