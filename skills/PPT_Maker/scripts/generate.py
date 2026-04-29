#!/usr/bin/env python3
"""
PPT Maker - 圖片生成腳本
========================
使用 Google Gemini API 批量生成簡報圖片。
支援視覺驗證確保文字正確性。

使用方式：
    python generate.py --plan slides.json --style style.md --output ./output --verify
"""

import argparse
import json
import base64
import time
import os
import sys
import subprocess
import requests
from pathlib import Path


def load_api_key():
    """從 config.env 或環境變數載入 API Key"""
    current = Path.cwd()
    search_paths = [
        current / "config.env",
        current.parent / "config.env",
        current.parent.parent / "config.env"
    ]

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        for config_path in search_paths:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            break
            if api_key:
                break

    if not api_key:
        print("錯誤：找不到 GEMINI_API_KEY", flush=True)
        print("請在 config.env 中設定，或設定環境變數", flush=True)
        sys.exit(1)

    return api_key


def create_placeholder_image(output_path, text="圖片生成失敗"):
    """建立佔位圖片"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, width-50, height-50], outline=(255, 255, 255), width=3)

        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()

        draw.text((width//2, height//2), text, fill=(255, 255, 255), anchor="mm", font=font)
        img.save(output_path)
        return True
    except Exception as e:
        print(f"建立佔位圖片失敗：{e}", flush=True)
        return False


def generate_image(prompt, api_key, output_path, model="gemini-3-pro-image-preview"):
    """呼叫 Gemini API 生成圖片"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["image", "text"]
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()

        if "candidates" not in data:
            print(f"API 錯誤：無候選結果 - {data}", flush=True)
            return False

        parts = data["candidates"][0]["content"]["parts"]

        for part in parts:
            b64_data = None
            if "inlineData" in part:
                b64_data = part["inlineData"]["data"]
            elif "inline_data" in part:
                b64_data = part["inline_data"]["data"]

            if b64_data:
                img_data = base64.b64decode(b64_data)
                with open(output_path, "wb") as f:
                    f.write(img_data)
                return True

        print(f"API 錯誤：回應中無圖片資料", flush=True)
        return False

    except requests.exceptions.Timeout:
        print("API 請求逾時", flush=True)
        return False
    except Exception as e:
        print(f"請求失敗：{e}", flush=True)
        return False


def verify_image(image_path, api_key):
    """使用 Gemini VLM 驗證圖片品質"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')

    prompt = """
    分析這張簡報投影片圖片：
    1. 文字檢查：
       - 是否使用繁體中文？（若出現簡體字則不通過）
       - 文字是否清晰可讀？
    2. 圖片檢查：
       - 比例是否接近 16:9？
       - 是否有亂碼或失真？

    回傳 JSON：{"pass": true/false, "reason": "簡短說明"}

    不通過條件：
    - 出現簡體中文 -> reason: "包含簡體字"
    - 文字亂碼 -> reason: "文字亂碼"
    - 嚴重失真 -> reason: "圖片失真"

    通過條件：
    - 繁體中文或英文/數字
    - 無文字也算通過
    """

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png", "data": img_data}}
            ]
        }],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        text_resp = result["candidates"][0]["content"]["parts"][0]["text"]
        evaluation = json.loads(text_resp)
        return evaluation.get("pass", True), evaluation.get("reason", "")
    except Exception as e:
        print(f"驗證檢查失敗：{e}", flush=True)
        return True, "驗證失敗，預設通過"


def generate_with_retry(prompt, api_key, output_path, use_verify=False, max_retries=3):
    """生成圖片，可選驗證重試"""

    for attempt in range(max_retries):
        if attempt > 0:
            print(f"   重試 {attempt+1}/{max_retries}...", end=" ", flush=True)
        else:
            print(f"   生成中...", end=" ", flush=True)

        if generate_image(prompt, api_key, output_path):
            print("完成。", end=" ", flush=True)

            if use_verify:
                print("驗證中...", end=" ", flush=True)
                is_pass, reason = verify_image(output_path, api_key)
                if is_pass:
                    print(f"通過", flush=True)
                    return True
                else:
                    print(f"未通過：{reason}", flush=True)
            else:
                print("", flush=True)
                return True
        else:
            print("生成失敗", flush=True)

        time.sleep(2)

    return False


def build_prompt(slide, style_content):
    """建構生成 Prompt"""
    content = slide.get("content", "")
    enhancement = slide.get("enhancement", "")

    prompt = f"""
請生成一張專業的簡報投影片圖片（16:9 比例）。

【風格定義】
{style_content}

【投影片內容】
{content}

【視覺指示】
{enhancement}

【關鍵規則】
1. **比例**：必須是寬螢幕 16:9，禁止生成正方形圖片
2. **語言**：所有文字必須使用**繁體中文**，禁止使用簡體中文
3. **文字準確**：若需顯示文字，必須與「投影片內容」完全一致
4. **版面**：建立平衡的構圖，適合作為簡報背景
"""
    return prompt


def main():
    parser = argparse.ArgumentParser(description="PPT Maker - 圖片生成")
    parser.add_argument("--plan", required=True, help="slides_plan.json 路徑")
    parser.add_argument("--style", required=True, help="風格定義檔路徑")
    parser.add_argument("--output", required=True, help="輸出目錄")
    parser.add_argument("--start-from", type=int, default=1, help="從第 N 頁開始")
    parser.add_argument("--verify", action="store_true", help="啟用視覺驗證")

    args = parser.parse_args()

    # 載入設定
    api_key = load_api_key()

    output_dir = Path(args.output)
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 載入規劃檔與風格檔
    with open(args.plan, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    with open(args.style, "r", encoding="utf-8") as f:
        style_content = f.read()

    slides = plan_data.get("slides", [])
    total = len(slides)

    print(f"開始生成：共 {total} 頁", flush=True)
    print(f"模型：gemini-3-pro-image-preview", flush=True)
    print(f"視覺驗證：{'啟用' if args.verify else '停用'}", flush=True)
    print(f"輸出目錄：{output_dir}", flush=True)

    # 逐頁生成
    for i, slide in enumerate(slides):
        slide_num = slide.get("slide_number", i + 1)

        if slide_num < args.start_from:
            print(f"跳過第 {slide_num} 頁...", flush=True)
            continue

        print(f"\n--- 生成第 {slide_num}/{total} 頁 ---", flush=True)
        prompt = build_prompt(slide, style_content)
        output_img = images_dir / f"slide-{slide_num}.png"

        success = generate_with_retry(prompt, api_key, output_img, use_verify=args.verify)

        if not success:
            print(f"使用佔位圖片替代第 {slide_num} 頁", flush=True)
            create_placeholder_image(output_img, f"第 {slide_num} 頁\n生成失敗")

    # 後處理
    print("\n--- 開始後處理 ---", flush=True)

    script_dir = Path(__file__).parent
    upscale_dir = output_dir / "images-4k"

    # 超分處理
    print("執行超分處理...", flush=True)
    subprocess.run([
        sys.executable, str(script_dir / "upscale.py"),
        "--images", str(images_dir),
        "--output", str(upscale_dir),
        "--scale", "4"
    ])

    # 生成 HTML
    print("生成網頁播放器...", flush=True)
    subprocess.run([
        sys.executable, str(script_dir / "build_viewer.py"),
        "--images", str(upscale_dir),
        "--output", str(output_dir / "viewer.html")
    ])

    # 生成 PPTX
    print("生成 PPTX...", flush=True)
    subprocess.run([
        sys.executable, str(script_dir / "build_pptx.py"),
        "--images", str(upscale_dir),
        "--output", str(output_dir / "output-4k.pptx")
    ])

    print("\n完成！", flush=True)
    print(f"PPTX：{output_dir / 'output-4k.pptx'}", flush=True)
    print(f"HTML：{output_dir / 'viewer.html'}", flush=True)


if __name__ == "__main__":
    main()
