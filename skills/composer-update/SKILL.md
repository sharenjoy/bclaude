---
name: composer-update
description: 在 Laravel 專案中執行完整的 composer update 流程。當使用者輸入 /composer-update、「composer update」、「更新 composer」、「更新套件」、「update composer packages」時觸發。執行順序：composer update → php artisan boost:update --discover → 偵測新安裝套件 → 自動更新 CLAUDE.md。
---

# Composer Update Skill

自動化執行 Laravel 專案的 composer update 完整流程，包含 Boost 更新與 CLAUDE.md 套件文件同步。

## 執行流程

### Step 1 — 確認環境

確認目前目錄為 Laravel 專案根目錄（存在 `composer.json` 和 `artisan`）。

```bash
ls composer.json artisan 2>/dev/null || echo "NOT_LARAVEL"
```

若不是 Laravel 專案根目錄，停止並告知使用者切換到正確目錄。

### Step 2 — 記錄更新前的套件清單

執行 composer update 前，先記錄目前已安裝的套件（用於比對新增套件）：

```bash
composer show --format=json 2>/dev/null | python3 -c "import json,sys; pkgs=json.load(sys.stdin); print('\n'.join([p['name'] for p in pkgs['installed']]))" > /tmp/composer_before.txt
```

### Step 3 — 執行 composer update

```bash
composer update 2>&1
```

執行時顯示完整輸出。記錄以下關鍵資訊：
- 哪些套件被更新（`Updating`）
- 哪些套件是新安裝（`Installing`）
- 哪些套件被移除（`Removing`）
- 是否有錯誤或衝突

### Step 4 — 執行 Boost 更新

不論 composer update 是否有變更，都必須執行：

```bash
php artisan boost:update --discover
```

回報指令輸出結果。

### Step 5 — 偵測新增套件

比對更新前後的套件清單，找出新安裝的套件：

```bash
composer show --format=json 2>/dev/null | python3 -c "import json,sys; pkgs=json.load(sys.stdin); print('\n'.join([p['name'] for p in pkgs['installed']]))" > /tmp/composer_after.txt
comm -13 <(sort /tmp/composer_before.txt) <(sort /tmp/composer_after.txt)
```

### Step 6 — 更新 CLAUDE.md（有新套件時才執行）

若 Step 5 偵測到新安裝的套件：

1. 讀取專案根目錄的 `CLAUDE.md`（或 `.claude/CLAUDE.md`，視專案結構而定）
2. 對每個新套件，執行 `composer show <package-name>` 取得描述
3. 在 CLAUDE.md 中找到或建立 `## 套件依賴` / `## Dependencies` 區塊
4. 將新套件加入，格式如下：

```markdown
## 套件依賴

| 套件名稱 | 版本 | 用途 |
|---------|------|------|
| vendor/package | ^1.0 | 套件功能描述 |
```

若 CLAUDE.md 不存在，在專案根目錄建立基本版本後加入套件表格。

### Step 7 — 回報摘要

最後輸出完整摘要：
- composer update 結果（更新/新增/移除的套件數）
- boost:update 執行結果
- CLAUDE.md 是否已更新（列出新增的套件名稱）

## 注意事項

- 若 composer update 失敗（非零退出碼），停止流程並回報錯誤，不繼續執行後續步驟
- 若 boost:update 失敗，回報錯誤但仍繼續偵測新套件與更新 CLAUDE.md
- 清理暫存檔：執行完畢後刪除 `/tmp/composer_before.txt` 和 `/tmp/composer_after.txt`
