# 模式 A：單頁爬取 `/scrape`

## 適用情境
- 抓取單一 URL 的全部內容
- 新聞文章、商品詳情頁、說明文件
- 輸出 Markdown 或 HTML

## 基本用法

```python
from firecrawl import Firecrawl
import os, json

app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

result = app.scrape(
    url="https://example.com/page",
    formats=["markdown"]   # 可選 "markdown", "html", "screenshot"
)

print(result["markdown"])
```

## 常用參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `formats` | 輸出格式 | `["markdown", "html"]` |
| `only_main_content` | 只抓主要內容（過濾導覽列/頁尾） | `True` |
| `wait_for` | 等待特定 CSS selector 出現再抓 | `".listing-item"` |
| `headers` | 自訂 HTTP headers | `{"Accept-Language": "zh-TW"}` |
| `timeout` | 超時設定（毫秒） | `30000` |

## 完整範例（含儲存）

```python
from firecrawl import Firecrawl
import os, json

app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

url = "https://rent.591.com.tw/home/house/detail/2/12345678.html"

try:
    result = app.scrape(
        url=url,
        formats=["markdown"],
        only_main_content=True
    )

    # 取得內容
    content = result.get("markdown", "")
    metadata = result.get("metadata", {})

    print(f"標題：{metadata.get('title', '無')}")
    print(f"內容長度：{len(content)} 字元")

    # 儲存結果
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump({
            "url": url,
            "title": metadata.get("title"),
            "content": content
        }, f, ensure_ascii=False, indent=2)

    print("✅ 已儲存至 output.json")

except Exception as e:
    print(f"❌ 爬取失敗：{e}")
```

## 注意事項
- 如果頁面內容是空的，可能需要加 `wait_for` 等 JS 載入完成
- SPA 網站（如 591、蝦皮）內容由 JS 產生，Firecrawl 會自動處理，但可能較慢
- 1 頁 = 1 credit
