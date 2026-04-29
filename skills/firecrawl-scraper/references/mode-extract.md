# 模式 B：AI 結構化萃取 `/extract`

## 適用情境
- 需要乾淨的 JSON 資料，不想自己解析 HTML
- 租屋列表、商品清單、新聞摘要、公司資訊
- 用自然語言描述要取得的欄位

## 基本用法

```python
from firecrawl import Firecrawl
import os

app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

result = app.extract(
    urls=["https://rent.591.com.tw/?region=2"],
    prompt="取得所有租屋物件的標題、月租金、地址、坪數、格局"
)

print(result["data"])
```

## 使用 JSON Schema（更精確）

定義明確的資料結構，讓萃取結果更穩定：

```python
from firecrawl import Firecrawl
import os, json

app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

schema = {
    "type": "object",
    "properties": {
        "listings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title":   {"type": "string", "description": "物件標題"},
                    "price":   {"type": "integer", "description": "月租金（元）"},
                    "address": {"type": "string", "description": "地址"},
                    "size":    {"type": "number", "description": "坪數"},
                    "layout":  {"type": "string", "description": "格局，例如 2房1廳"},
                    "url":     {"type": "string", "description": "物件連結"}
                },
                "required": ["title", "price", "address"]
            }
        }
    }
}

try:
    result = app.extract(
        urls=["https://rent.591.com.tw/?region=2"],  # 新北市
        prompt="取得頁面上所有租屋物件的詳細資訊",
        schema=schema
    )

    listings = result.get("data", {}).get("listings", [])
    print(f"共取得 {len(listings)} 筆物件")

    # 儲存
    with open("listings.json", "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)

    print("✅ 已儲存至 listings.json")

except Exception as e:
    print(f"❌ 萃取失敗：{e}")
```

## 多頁萃取（批次）

```python
urls = [
    "https://rent.591.com.tw/?region=2&firstRow=0",
    "https://rent.591.com.tw/?region=2&firstRow=30",
    "https://rent.591.com.tw/?region=2&firstRow=60",
]

result = app.extract(
    urls=urls,
    prompt="取得所有租屋物件資訊",
    schema=schema
)
```

## 輸出存成 CSV

```python
import csv

with open("listings.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "price", "address", "size", "layout", "url"])
    writer.writeheader()
    writer.writerows(listings)

print("✅ 已儲存至 listings.csv（可用 Excel 開啟）")
```

## 費用說明
- `/extract` 除了 scrape credits 外，還會額外消耗 LLM tokens
- 建議先用單一 URL 測試，確認結果正確再批次執行
- 用 Schema 比純 prompt 更省 tokens，結果也更穩定
