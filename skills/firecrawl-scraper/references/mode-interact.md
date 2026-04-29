# 模式 D：互動式爬取 `/scrape` + `/interact`

## 適用情境
- 需要翻頁（下一頁、Load More）
- 需要點擊篩選條件（區域、價格範圍）
- 資料在 JS 互動後才出現
- 適合 591 租屋、蝦皮、104 人力銀行等平台

## 基本概念

`/interact` 讓你在爬取後保留瀏覽器 session，繼續對頁面執行操作：

```
scrape(url) → 取得 scrape_id → interact(scrape_id, "點下一頁") → interact(scrape_id, "取得資料")
```

## 591 租屋翻頁完整範例

```python
from firecrawl import Firecrawl
import os, json, time

app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

all_listings = []
max_pages = 5  # 最多爬幾頁（避免費用失控）

# 步驟 1：開啟頁面
print("📄 開啟 591 新北市租屋頁面...")
result = app.scrape(
    url="https://rent.591.com.tw/?region=2",
    formats=["markdown"]
)
scrape_id = result.metadata.scrape_id
print(f"Session ID：{scrape_id}")

for page_num in range(1, max_pages + 1):
    print(f"\n🔍 第 {page_num} 頁...")

    # 步驟 2：萃取當前頁面資料
    extract_result = app.interact(
        scrape_id,
        prompt="""
        取得頁面上所有租屋物件，每筆包含：
        - title（標題）
        - price（月租金，只要數字）
        - address（地址）
        - size（坪數，只要數字）
        - layout（格局，如 2房1廳）
        回傳 JSON 格式，key 為 listings，值為陣列。
        """
    )

    try:
        listings = json.loads(extract_result.output).get("listings", [])
        all_listings.extend(listings)
        print(f"  ✅ 取得 {len(listings)} 筆物件")
    except Exception:
        print(f"  ⚠️ 解析失敗，原始回應：{extract_result.output[:200]}")

    # 最後一頁不需要翻頁
    if page_num == max_pages:
        break

    # 步驟 3：點擊下一頁
    print("  ➡️  翻到下一頁...")
    nav_result = app.interact(
        scrape_id,
        prompt="點擊下一頁按鈕（通常是 '下一頁' 或 '>' 或頁碼）"
    )

    # 等待頁面載入
    time.sleep(2)

# 步驟 4：結束 session
app.stop_interaction(scrape_id)
print(f"\n✅ 共取得 {len(all_listings)} 筆物件")

# 儲存結果
with open("591_listings.json", "w", encoding="utf-8") as f:
    json.dump(all_listings, f, ensure_ascii=False, indent=2)

print("💾 已儲存至 591_listings.json")
```

## 其他互動操作範例

### 填寫篩選條件
```python
# 設定價格範圍
app.interact(scrape_id, prompt="在最低租金欄位輸入 5000")
app.interact(scrape_id, prompt="在最高租金欄位輸入 15000")
app.interact(scrape_id, prompt="點擊搜尋按鈕")
time.sleep(2)
```

### 處理「載入更多」按鈕
```python
for _ in range(3):  # 點 3 次載入更多
    app.interact(scrape_id, prompt="點擊頁面上的『載入更多』按鈕")
    time.sleep(2)
```

### 用 Playwright 精確控制（進階）
```python
# 也可以用 Playwright 語法直接操作
app.interact(scrape_id, playwright="page.click('.pagination-next')")
app.interact(scrape_id, playwright="page.wait_for_selector('.listing-item')")
```

## 費用說明

| 操作 | Credits |
|------|---------|
| 初始 scrape | 1 |
| 每個 interact | 5 |
| 5 頁（1 scrape + 4 翻頁 + 5 萃取） | 1 + 9×5 = 46 |

爬取前先估算費用，設定 `max_pages` 上限保護帳戶。

## 常見問題

**Q：interact 回傳空白或錯誤？**
→ 加上 `time.sleep(2)` 等待 JS 載入完成

**Q：找不到下一頁按鈕？**
→ 改用更具體的描述：`"點擊右下角寫著 '下一頁' 的灰色按鈕"`

**Q：Session 中斷？**
→ scrape_id 只在同一 session 有效，需要重新 scrape 取得新的 ID
