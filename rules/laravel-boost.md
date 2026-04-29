# Laravel Boost 規則

當使用者說「更新 boost」或「update boost」時，**必須執行**以下指令：

```bash
php artisan boost:update --discover
```

- 此指令為完整的 Boost 更新流程，包含自動發現（discover）
- 執行前確認目前目錄為 Laravel 專案根目錄
- 執行後回報指令輸出結果
