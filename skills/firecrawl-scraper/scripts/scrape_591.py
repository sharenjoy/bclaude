#!/usr/bin/env python3
"""
591 租屋網爬取腳本（新北市）
使用方式：
    export FIRECRAWL_API_KEY="fc-your-key"
    python scrape_591.py --pages 3 --output 591_listings.json

地區代碼：
    1=台北市, 2=新北市, 3=桃園, 4=台中, 5=台南, 6=高雄
"""

import argparse
import json
import csv
import os
import sys
import time
from firecrawl import Firecrawl


REGION_NAMES = {
    "1": "台北市",
    "2": "新北市",
    "3": "桃園",
    "4": "台中",
    "5": "台南",
    "6": "高雄",
}

EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "listings": {
            "type": "array",
            "description": "頁面上所有租屋物件",
            "items": {
                "type": "object",
                "properties": {
                    "title":   {"type": "string", "description": "物件標題"},
                    "price":   {"type": "integer", "description": "月租金（新台幣，只要數字）"},
                    "address": {"type": "string", "description": "地址或區域"},
                    "size":    {"type": "number", "description": "坪數（只要數字）"},
                    "layout":  {"type": "string", "description": "格局，例如 2房1廳1衛"},
                    "type":    {"type": "string", "description": "物件類型，例如 整層住家、獨立套房"},
                    "url":     {"type": "string", "description": "物件頁面連結"}
                },
                "required": ["title", "price"]
            }
        },
        "total_count": {
            "type": "integer",
            "description": "搜尋結果總數量"
        }
    }
}


def scrape_591(region: str, max_pages: int, output_file: str):
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ 請設定環境變數 FIRECRAWL_API_KEY")
        sys.exit(1)

    app = Firecrawl(api_key=api_key)
    region_name = REGION_NAMES.get(region, f"地區{region}")
    base_url = f"https://rent.591.com.tw/?region={region}"

    print(f"🏠 591 租屋爬取 — {region_name}")
    print(f"   目標：{max_pages} 頁")
    print(f"   預估消耗：{1 + (max_pages - 1) * 2 * 5} credits（1 scrape + 翻頁 + 萃取）\n")

    all_listings = []

    # 開啟瀏覽器 session
    print("📄 開啟頁面...")
    try:
        result = app.scrape(base_url, formats=["markdown"])
        scrape_id = result.metadata.scrape_id
        print(f"   Session：{scrape_id}")
    except Exception as e:
        print(f"❌ 無法開啟頁面：{e}")
        sys.exit(1)

    for page_num in range(1, max_pages + 1):
        print(f"\n📑 第 {page_num}/{max_pages} 頁...")

        # 萃取當前頁資料
        try:
            extract_resp = app.interact(
                scrape_id,
                prompt="根據頁面內容，取得所有租屋物件資訊，回傳 JSON 格式（listings 陣列）"
            )
            raw = extract_resp.output or ""

            # 嘗試解析 JSON
            # 有時模型會在 JSON 外包一層 markdown，需要清理
            clean = raw.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            clean = clean.strip()

            parsed = json.loads(clean)
            listings = parsed.get("listings", [])
            all_listings.extend(listings)
            total = parsed.get("total_count", "?")
            print(f"   ✅ 取得 {len(listings)} 筆（搜尋結果總計 {total} 筆）")

        except json.JSONDecodeError:
            print(f"   ⚠️  JSON 解析失敗，跳過此頁")
            print(f"      原始回應：{raw[:200]}")
        except Exception as e:
            print(f"   ❌ 萃取失敗：{e}")

        # 最後一頁不需要翻頁
        if page_num >= max_pages:
            break

        # 翻頁
        print("   ➡️  翻到下一頁...")
        try:
            app.interact(scrape_id, prompt="點擊頁面底部的下一頁按鈕")
            time.sleep(2)  # 等待頁面載入
        except Exception as e:
            print(f"   ⚠️  翻頁失敗：{e}，停止爬取")
            break

    # 關閉 session
    try:
        app.stop_interaction(scrape_id)
    except Exception:
        pass

    print(f"\n📊 爬取完成，共 {len(all_listings)} 筆物件")

    if not all_listings:
        print("⚠️  沒有取得任何資料，請確認 API Key 和網站狀況")
        return

    # 去除重複（以 title+price 為 key）
    seen = set()
    unique_listings = []
    for item in all_listings:
        key = f"{item.get('title', '')}-{item.get('price', '')}"
        if key not in seen:
            seen.add(key)
            unique_listings.append(item)

    dedup_count = len(all_listings) - len(unique_listings)
    if dedup_count > 0:
        print(f"   去除重複：{dedup_count} 筆，剩餘 {len(unique_listings)} 筆")
    all_listings = unique_listings

    # 儲存 JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "region": region_name,
            "total": len(all_listings),
            "listings": all_listings
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON：{output_file}")

    # 儲存 CSV
    csv_file = output_file.replace(".json", ".csv")
    fieldnames = ["title", "price", "address", "size", "layout", "type", "url"]
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_listings)
    print(f"📊 CSV：{csv_file}（可用 Excel 直接開啟）")

    # 簡單統計
    prices = [item.get("price", 0) for item in all_listings if item.get("price")]
    if prices:
        print(f"\n💰 租金統計")
        print(f"   最低：{min(prices):,} 元")
        print(f"   最高：{max(prices):,} 元")
        print(f"   平均：{sum(prices) // len(prices):,} 元")


def main():
    parser = argparse.ArgumentParser(description="591 租屋網爬取工具")
    parser.add_argument("--region", default="2", help="地區代碼（預設 2=新北市）")
    parser.add_argument("--pages", type=int, default=3, help="爬取頁數（預設 3）")
    parser.add_argument("--output", default="591_listings.json", help="輸出檔名")
    args = parser.parse_args()

    scrape_591(args.region, args.pages, args.output)


if __name__ == "__main__":
    main()
