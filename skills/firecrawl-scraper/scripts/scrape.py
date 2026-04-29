#!/usr/bin/env python3
"""
Firecrawl 通用爬取腳本
使用方式：
    export FIRECRAWL_API_KEY="fc-your-key"
    python scrape.py --url "https://example.com" --mode extract --output output.json
"""

import argparse
import json
import os
import sys
import time
import csv
from firecrawl import Firecrawl


def get_client():
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ 請設定環境變數 FIRECRAWL_API_KEY")
        print("   export FIRECRAWL_API_KEY='fc-your-key-here'")
        sys.exit(1)
    return Firecrawl(api_key=api_key)


def mode_scrape(app, url, output_file):
    """單頁爬取"""
    print(f"📄 爬取頁面：{url}")
    try:
        result = app.scrape(
            url=url,
            formats=["markdown"],
            only_main_content=True
        )
        content = {
            "url": url,
            "title": result.get("metadata", {}).get("title", ""),
            "content": result.get("markdown", "")
        }
        save_json(content, output_file)
        print(f"✅ 完成，內容長度：{len(content['content'])} 字元")
    except Exception as e:
        print(f"❌ 失敗：{e}")


def mode_extract(app, url, prompt, schema_file, output_file):
    """AI 結構化萃取"""
    print(f"🤖 AI 萃取：{url}")

    schema = None
    if schema_file and os.path.exists(schema_file):
        with open(schema_file, encoding="utf-8") as f:
            schema = json.load(f)
        print(f"📋 使用 Schema：{schema_file}")

    try:
        kwargs = {"urls": [url], "prompt": prompt}
        if schema:
            kwargs["schema"] = schema

        result = app.extract(**kwargs)
        data = result.get("data", {})
        save_json(data, output_file)

        # 如果是陣列資料，也輸出 CSV
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                csv_file = output_file.replace(".json", f"_{key}.csv")
                save_csv(value, csv_file)
                print(f"📊 CSV 已儲存：{csv_file}")

        print(f"✅ 萃取完成")
    except Exception as e:
        print(f"❌ 失敗：{e}")


def mode_crawl(app, url, limit, max_depth, output_file):
    """整站爬取"""
    print(f"🕷️  整站爬取：{url}（最多 {limit} 頁）")

    # 先 map 確認範圍
    print("🗺️  掃描網站結構...")
    try:
        map_result = app.map(url)
        found_urls = map_result.get("links", [])
        print(f"   找到 {len(found_urls)} 個 URL，將爬取最多 {limit} 頁")
    except Exception:
        print("   無法 map，直接開始爬取")

    try:
        crawl_job = app.crawl_url(
            url=url,
            params={
                "limit": limit,
                "maxDepth": max_depth,
                "scrapeOptions": {
                    "formats": ["markdown"],
                    "onlyMainContent": True
                }
            }
        )

        job_id = crawl_job.get("id")
        print(f"   任務 ID：{job_id}")

        # 等待完成
        while True:
            status = app.check_crawl_status(job_id)
            state = status.get("status")
            completed = status.get("completed", 0)
            total = status.get("total", "?")
            print(f"\r   進度：{completed}/{total}（{state}）", end="", flush=True)

            if state in ("completed", "failed"):
                print()
                break
            time.sleep(3)

        if state == "completed":
            pages = status.get("data", [])
            all_content = [
                {
                    "url": p.get("metadata", {}).get("sourceURL"),
                    "title": p.get("metadata", {}).get("title"),
                    "content": p.get("markdown", "")
                }
                for p in pages
            ]
            save_json(all_content, output_file)
            print(f"✅ 共爬取 {len(all_content)} 頁")
        else:
            print("❌ 爬取失敗")

    except Exception as e:
        print(f"❌ 失敗：{e}")


def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON 已儲存：{filename}")


def save_csv(rows, filename):
    if not rows:
        return
    fieldnames = list(rows[0].keys()) if isinstance(rows[0], dict) else []
    if not fieldnames:
        return
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Firecrawl 通用爬取工具")
    parser.add_argument("--url", required=True, help="目標網址")
    parser.add_argument(
        "--mode",
        choices=["scrape", "extract", "crawl"],
        default="scrape",
        help="爬取模式"
    )
    parser.add_argument("--prompt", default="取得頁面上所有重要資訊", help="Extract 模式的提示詞")
    parser.add_argument("--schema", help="JSON Schema 檔案路徑（Extract 模式用）")
    parser.add_argument("--limit", type=int, default=50, help="Crawl 模式最多爬幾頁")
    parser.add_argument("--depth", type=int, default=2, help="Crawl 模式深度")
    parser.add_argument("--output", default="output.json", help="輸出檔案名稱")

    args = parser.parse_args()
    app = get_client()

    if args.mode == "scrape":
        mode_scrape(app, args.url, args.output)
    elif args.mode == "extract":
        mode_extract(app, args.url, args.prompt, args.schema, args.output)
    elif args.mode == "crawl":
        mode_crawl(app, args.url, args.limit, args.depth, args.output)


if __name__ == "__main__":
    main()
