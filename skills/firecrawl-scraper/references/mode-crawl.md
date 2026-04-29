# 模式 C：整站爬取 `/crawl`

## 適用情境
- 爬取某個網站的所有頁面或特定路徑下的頁面
- 文件網站、新聞頻道、部落格、電商分類
- 需要大量頁面的內容

## ⚠️ 爬取前必做：先用 `/map` 估算頁面數

整站爬取可能消耗大量 credits，先確認範圍：

```python
from firecrawl import Firecrawl
import os

app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

# 先 map，看有多少頁
map_result = app.map("https://example.com/blog")
urls = map_result.get("links", [])
print(f"找到 {len(urls)} 個 URL，預估消耗 {len(urls)} credits")
```

確認頁面數量合理後，再執行爬取。

## 整站爬取範例

```python
from firecrawl import Firecrawl
import os, json, time

app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

# 啟動爬取任務（非同步）
crawl_job = app.crawl_url(
    url="https://example.com/blog",
    params={
        "limit": 50,           # 最多爬幾頁（保護用）
        "maxDepth": 2,         # 爬取深度
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True
        }
    }
)

job_id = crawl_job.get("id")
print(f"爬取任務 ID：{job_id}")

# 輪詢等待完成
while True:
    status = app.check_crawl_status(job_id)
    state = status.get("status")
    completed = status.get("completed", 0)
    total = status.get("total", 0)
    print(f"進度：{completed}/{total} 頁（{state}）")

    if state == "completed":
        break
    elif state == "failed":
        print("❌ 爬取失敗")
        break

    time.sleep(5)

# 取得結果
pages = status.get("data", [])
print(f"✅ 共爬取 {len(pages)} 頁")

# 儲存所有頁面
all_content = []
for page in pages:
    all_content.append({
        "url": page.get("metadata", {}).get("sourceURL"),
        "title": page.get("metadata", {}).get("title"),
        "content": page.get("markdown", "")
    })

with open("crawl_result.json", "w", encoding="utf-8") as f:
    json.dump(all_content, f, ensure_ascii=False, indent=2)

print("✅ 已儲存至 crawl_result.json")
```

## 常用參數說明

| 參數 | 說明 | 建議值 |
|------|------|--------|
| `limit` | 最多爬幾頁 | 先設 50，測試後再調整 |
| `maxDepth` | 連結深度（1=只有首頁連出去的） | 2~3 |
| `allowBackwardLinks` | 是否爬上層連結 | `False` |
| `allowExternalLinks` | 是否爬外部連結 | `False` |
| `includePaths` | 只爬符合這些路徑的 URL | `["/blog/*", "/news/*"]` |
| `excludePaths` | 排除這些路徑 | `["/login", "/cart"]` |

## 用 map + batch_scrape（更精確控制）

如果你知道要爬哪些頁面，用這個方式比 crawl 更省 credits：

```python
# 1. 先取得所有 URL
map_result = app.map("https://example.com/news")
urls = map_result.get("links", [])[:100]  # 只取前 100 個

# 2. 批次爬取
batch_result = app.batch_scrape_urls(
    urls=urls,
    params={"formats": ["markdown"], "onlyMainContent": True}
)
```

## 費用估算
- 100 頁 ≈ 100 credits（約 $0.02 美元，Hobby 方案）
- 建議先 map 確認頁面數，再決定是否執行
