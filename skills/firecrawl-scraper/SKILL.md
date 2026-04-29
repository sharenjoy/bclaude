---
name: firecrawl-scraper
description: 使用 Firecrawl API 爬取網站資料的技能。當使用者想要爬取網站、抓取網頁內容、取得結構化資料、監控網站變化、爬取租屋網/電商/新聞等平台，或提到 Firecrawl、網頁爬蟲、scraping、crawling 時觸發。支援單頁抓取、整站爬取、AI 結構化萃取、互動式操作（翻頁/點擊/填表）等模式。
---

# Firecrawl 網站爬取技能

此技能幫助使用者使用 Firecrawl API 爬取任何網站，自動處理 JS 渲染、反爬機制、動態內容，並將結果輸出為乾淨的 Markdown、JSON 或結構化資料。

## 使用前提

- 需要 Firecrawl API Key（至 https://firecrawl.dev 取得，新帳號有免費 credits）
- 安裝 SDK：`pip install firecrawl-py` 或 `npm install @mendable/firecrawl-js`
- 費用：Scrape 1頁 = 1 credit、Interact 每動作 = 5 credits、Extract 額外消耗 LLM tokens

---

## 步驟一：釐清爬取需求

詢問使用者以下問題（若對話中已有答案則跳過）：

1. **目標網站是什麼？** 貼上 URL
2. **要爬什麼資料？** 例如：租金、地址、商品價格、新聞標題等
3. **範圍多大？** 單頁 / 特定幾頁 / 整個網站
4. **網站類型？** 靜態頁面、SPA（需要 JS）、需要登入、需要翻頁
5. **輸出格式？** JSON（結構化）、Markdown（純文字）、CSV

根據回答選擇下方的爬取模式。

---

## 步驟二：選擇爬取模式

### 模式 A：單頁爬取 `/scrape`
適合：抓取一個特定頁面的內容
- 靜態頁面、文章、商品頁
- 輸出 Markdown 或 HTML

→ 詳見 `references/mode-scrape.md`

### 模式 B：AI 結構化萃取 `/extract`
適合：用自然語言描述要取得的欄位，直接輸出 JSON
- 租屋列表、商品清單、新聞摘要
- 省去自己解析 HTML 的麻煩

→ 詳見 `references/mode-extract.md`

### 模式 C：整站爬取 `/crawl`
適合：爬取網站所有頁面或特定子路徑下的頁面
- 文件網站、新聞頻道、電商分類頁

→ 詳見 `references/mode-crawl.md`

### 模式 D：互動式爬取 `/scrape` + `/interact`
適合：需要點擊、翻頁、填表、登入後才看得到的資料
- 591 租屋翻頁、電商「載入更多」、需要篩選條件

→ 詳見 `references/mode-interact.md`

---

## 步驟三：產生可執行程式碼

根據選擇的模式，讀取對應的 references 檔案，再依照以下原則產生程式碼：

**Python（預設推薦）**
```python
from firecrawl import Firecrawl
import json, os

app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
```

**注意事項：**
- API Key 一律從環境變數讀取，不寫死在程式碼
- 加入錯誤處理（try/except）
- 大量爬取時加入 `time.sleep(1)` 控制頻率
- 結果存到 JSON 或 CSV 檔

→ 詳見 `scripts/` 資料夾內的範本腳本

---

## 步驟四：說明執行方式

提供完整的執行指令：

```bash
# 設定 API Key
export FIRECRAWL_API_KEY="fc-your-key-here"

# 安裝依賴
pip install firecrawl-py

# 執行
python scrape.py
```

---

## 步驟五：說明結果與後續處理

告訴使用者：
- 輸出檔案在哪裡（`output.json` / `output.csv`）
- 如何檢視結果
- 如果資料不完整，建議切換哪種模式
- Credits 消耗估算

---

## 硬性規則

- **永遠不要把 API Key 寫進程式碼**，一律用環境變數
- **尊重 robots.txt**：Firecrawl 預設遵守，不要刻意繞過
- **控制頻率**：批次爬取時加入延遲，避免對目標伺服器造成負擔
- **只爬公開資料**：不協助爬取需要繞過登入驗證的私人資料
- **大量爬取先估算費用**：整站爬取前先用 `/map` 確認頁面數量
- 如果使用者的目標網站有明確禁止爬蟲的條款，要提醒使用者自行評估法律風險
