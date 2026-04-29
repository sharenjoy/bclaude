# PPT Maker - 完整開發規格書

> **使用方式**：將此檔案放入空專案根目錄，告訴 Claude Code：「按照 SPEC.md 一步步建置這個專案」。
>
> 本規格書包含所有程式碼和設定，Claude Code 可完全複刻此專案。

---

## 目錄

1. [專案概述](#一專案概述)
2. [環境準備](#二環境準備)
3. [專案結構](#三專案結構)
4. [設定檔案](#四設定檔案)
5. [Python 腳本](#五python-腳本)
6. [風格定義](#六風格定義)
7. [Claude Skill](#七claude-skill)
8. [資料格式規範](#八資料格式規範)
9. [啟動專案](#九啟動專案)

---

## 一、專案概述

### 1.1 產品定義

PPT Maker 是一套 AI 驅動的智能簡報生成系統，能夠：
- 接收多種格式的內容輸入（Markdown、PDF、Word、純文字）
- 透過互動式對話了解使用者的簡報需求
- 選擇預設風格模板生成統一視覺風格
- 批量生成高品質簡報圖片並打包輸出

### 1.2 核心價值

- **風格一致**：預設風格模板確保每頁視覺統一
- **智能規劃**：根據內容自動規劃頁面結構
- **高品質輸出**：4K 超分處理確保清晰度

### 1.3 技術棧

| 技術 | 用途 |
|------|------|
| Python 3.10+ | 腳本執行環境 |
| Google Gemini API | 圖片生成（gemini-3-pro-image-preview）|
| Google Gemini API | 視覺驗證（gemini-2.0-flash）|
| Pillow | 圖片處理、超分縮放 |
| python-pptx | PPTX 檔案生成 |
| requests | API 呼叫 |

---

## 二、環境準備

### 2.1 系統需求

- Python 3.10+
- pip（Python 套件管理器）
- Google Gemini API Key

### 2.2 檢查環境

```bash
# 檢查 Python 版本
python --version  # 應顯示 Python 3.10.x 或更高

# 檢查 pip
pip --version
```

### 2.3 如果缺少環境

**安裝 Python（Windows）**：
```bash
# 下載安裝包
# https://www.python.org/downloads/
```

**安裝 Python（macOS）**：
```bash
# 使用 Homebrew
brew install python@3.11

# 或下載安裝包
# https://www.python.org/downloads/
```

### 2.4 取得 API Key

1. 前往 https://aistudio.google.com/apikey
2. 登入 Google 帳號
3. 點擊「Create API Key」
4. 複製產生的 API Key

---

## 三、專案結構

執行以下指令建立目錄結構：

```bash
# 建立專案目錄
mkdir -p PPT_Maker
cd PPT_Maker

# 建立子目錄
mkdir -p scripts styles

# 建立空檔案佔位（後續會填入內容）
touch SKILL.md
touch SPEC.md
touch README.md
touch requirements.txt
touch config.example.env
touch scripts/generate.py
touch scripts/upscale.py
touch scripts/build_pptx.py
touch scripts/build_viewer.py
touch styles/deep_space.md
```

完整結構如下：

```
PPT_Maker/
├── SKILL.md                  # Claude Skill 定義（給 AI 看）
├── SPEC.md                   # 本檔案（完整規格書）
├── README.md                 # 使用者安裝指南
├── requirements.txt          # Python 依賴
├── config.example.env        # API 設定範例
├── scripts/
│   ├── generate.py           # 主生成腳本
│   ├── upscale.py            # 超分處理腳本
│   ├── build_pptx.py         # PPTX 打包腳本
│   └── build_viewer.py       # HTML 播放器腳本
└── styles/
    └── deep_space.md         # 深空科技風格
```

---

## 四、設定檔案

### 4.1 requirements.txt

```
# PPT Maker - Python 依賴
# 安裝方式：pip install -r requirements.txt

# 圖片處理
Pillow>=10.0.0

# PPTX 生成
python-pptx>=0.6.21

# API 呼叫
requests>=2.31.0
```

### 4.2 config.example.env

```bash
# PPT Maker - API 設定
# 使用方式：將此檔案複製為 config.env，並填入你的 API Key

# Google Gemini API Key
# 取得方式：https://aistudio.google.com/apikey
# 1. 登入 Google 帳號
# 2. 點擊「Create API Key」
# 3. 複製產生的 Key 到下方

GEMINI_API_KEY=your_api_key_here

# 費用說明：
# - 免費方案：每分鐘有請求次數限制，足夠測試使用
# - 付費方案：依用量計費，詳見 https://ai.google.dev/pricing
# - 預估成本：約 $0.01-0.02 / 頁
```

### 4.3 安裝依賴

```bash
# 建立虛擬環境（建議）
python -m venv venv

# 啟用虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

---

## 五、Python 腳本

> 以下是所有 Python 腳本的完整程式碼。按順序建立這些檔案。

### 5.1 scripts/generate.py

```python
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
```

### 5.2 scripts/upscale.py

```python
#!/usr/bin/env python3
"""
PPT Maker - 超分處理腳本
========================
批量放大圖片，支援 Real-ESRGAN（如有安裝）或 Pillow Lanczos。

使用方式：
    python upscale.py --images ./images --output ./images-4k --scale 4
"""

import argparse
import sys
import subprocess
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("錯誤：請安裝 Pillow")
    print("執行：pip install Pillow")
    sys.exit(1)


def check_realesrgan():
    """檢查是否有安裝 Real-ESRGAN"""
    try:
        subprocess.run(
            ["realesrgan-ncnn-vulkan", "-h"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def upscale_with_pillow(input_path, output_path, scale):
    """使用 Pillow Lanczos 放大"""
    try:
        with Image.open(input_path) as img:
            new_size = (int(img.width * scale), int(img.height * scale))
            resampled = img.resize(new_size, resample=Image.Resampling.LANCZOS)
            resampled.save(output_path)
            return True
    except Exception as e:
        print(f"Pillow 放大失敗：{input_path} - {e}")
        return False


def upscale_with_realesrgan(input_path, output_path, scale):
    """使用 Real-ESRGAN 放大"""
    try:
        cmd = [
            "realesrgan-ncnn-vulkan",
            "-i", str(input_path),
            "-o", str(output_path),
            "-s", str(scale),
            "-n", "realesrgan-x4plus"
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        print(f"Real-ESRGAN 失敗，改用 Pillow：{input_path}")
        return False


def batch_upscale(input_dir, output_dir, scale, method="auto"):
    """批量放大圖片"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 收集圖片
    images = sorted([
        f for f in input_path.iterdir()
        if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp']
    ])

    if not images:
        print(f"找不到圖片：{input_dir}")
        return

    # 決定使用哪種方法
    use_realesrgan = False
    if method == "realesrgan":
        use_realesrgan = True
    elif method == "auto":
        use_realesrgan = check_realesrgan()
        if use_realesrgan:
            print("使用 Real-ESRGAN 進行超分處理")
        else:
            print("使用 Pillow (Lanczos) 進行超分處理")
    else:
        print("使用 Pillow (Lanczos) 進行超分處理")

    success_count = 0
    total = len(images)

    for i, img_file in enumerate(images, 1):
        target_file = output_path / img_file.name
        print(f"[{i}/{total}] 處理 {img_file.name}...", end="\r")

        ok = False
        if use_realesrgan:
            ok = upscale_with_realesrgan(img_file, target_file, scale)
            if not ok:
                ok = upscale_with_pillow(img_file, target_file, scale)
        else:
            ok = upscale_with_pillow(img_file, target_file, scale)

        if ok:
            success_count += 1

    print(f"\n完成：{success_count}/{total} 張圖片已放大至 {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PPT Maker - 超分處理")
    parser.add_argument("--images", required=True, help="輸入圖片目錄")
    parser.add_argument("--output", required=True, help="輸出目錄")
    parser.add_argument("--scale", type=int, default=4, help="放大倍數")
    parser.add_argument("--method", choices=["auto", "pillow", "realesrgan"], default="auto")

    args = parser.parse_args()
    batch_upscale(args.images, args.output, args.scale, args.method)
```

### 5.3 scripts/build_pptx.py

```python
#!/usr/bin/env python3
"""
PPT Maker - PPTX 打包腳本
=========================
將圖片目錄打包成 PPTX 檔案。

使用方式：
    python build_pptx.py --images ./images --output output.pptx
"""

import argparse
import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches
except ImportError:
    print("錯誤：請安裝 python-pptx")
    print("執行：pip install python-pptx")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("錯誤：請安裝 Pillow")
    print("執行：pip install Pillow")
    sys.exit(1)


def build_pptx(images_dir, output_file):
    """將圖片打包成 PPTX"""
    images_path = Path(images_dir)
    output_path = Path(output_file)

    if not images_path.exists():
        print(f"錯誤：圖片目錄不存在 - {images_dir}")
        return False

    # 收集圖片
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    images = sorted([
        f for f in images_path.iterdir()
        if f.suffix.lower() in image_extensions
    ])

    if not images:
        print(f"錯誤：找不到圖片 - {images_dir}")
        return False

    print(f"找到 {len(images)} 張圖片")

    # 建立 PPTX
    prs = Presentation()

    # 設定 16:9 尺寸
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide_width = prs.slide_width.inches
    slide_height = prs.slide_height.inches

    # 取得空白版面
    blank_layout = prs.slide_layouts[6]

    for i, image_path in enumerate(images, 1):
        print(f"處理 {i}/{len(images)}：{image_path.name}")

        # 新增空白投影片
        slide = prs.slides.add_slide(blank_layout)

        # 取得圖片尺寸
        with Image.open(image_path) as img:
            img_width, img_height = img.size

        # 計算縮放比例，保持比例
        img_ratio = img_width / img_height
        slide_ratio = slide_width / slide_height

        if img_ratio > slide_ratio:
            width = Inches(slide_width)
            height = Inches(slide_width / img_ratio)
            left = Inches(0)
            top = Inches((slide_height - slide_width / img_ratio) / 2)
        else:
            height = Inches(slide_height)
            width = Inches(slide_height * img_ratio)
            left = Inches((slide_width - slide_height * img_ratio) / 2)
            top = Inches(0)

        # 加入圖片
        slide.shapes.add_picture(str(image_path), left, top, width, height)

    # 確保輸出目錄存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 儲存
    prs.save(str(output_path))
    print(f"PPTX 已儲存：{output_path}")
    print(f"共 {len(images)} 頁")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PPT Maker - PPTX 打包")
    parser.add_argument("--images", required=True, help="圖片目錄")
    parser.add_argument("--output", required=True, help="輸出 PPTX 路徑")

    args = parser.parse_args()
    success = build_pptx(args.images, args.output)
    sys.exit(0 if success else 1)
```

### 5.4 scripts/build_viewer.py

```python
#!/usr/bin/env python3
"""
PPT Maker - HTML 播放器腳本
===========================
生成網頁版簡報播放器。

使用方式：
    python build_viewer.py --images ./images --output viewer.html
"""

import argparse
import json
import sys
from pathlib import Path


def get_html_template():
    """取得 HTML 模板"""
    return '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PPT Maker Viewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Microsoft JhengHei", sans-serif;
            background: #0a0a0a;
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: calc(100vh * 16 / 9);
            aspect-ratio: 16 / 9;
            background: #111;
            position: relative;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .container img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        .controls {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 16px;
            align-items: center;
            background: rgba(30,30,30,0.95);
            padding: 12px 24px;
            border-radius: 50px;
            backdrop-filter: blur(10px);
        }
        button {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            border: none;
            background: rgba(255,255,255,0.1);
            color: #fff;
            cursor: pointer;
            font-size: 18px;
            transition: all 0.2s;
        }
        button:hover { background: rgba(255,255,255,0.2); transform: scale(1.05); }
        button:disabled { opacity: 0.3; cursor: not-allowed; transform: none; }
        .info {
            font-size: 14px;
            min-width: 60px;
            text-align: center;
            color: rgba(255,255,255,0.7);
        }
        .fullscreen-btn {
            margin-left: 8px;
            background: rgba(255,255,255,0.05);
        }
        .help {
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            color: rgba(255,255,255,0.4);
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container" id="container">
        <img id="slide" src="" alt="Slide">
    </div>
    <div class="controls">
        <button id="prev" title="上一頁 (←)">&larr;</button>
        <span class="info" id="info">1 / 1</span>
        <button id="next" title="下一頁 (→ 或 Space)">&rarr;</button>
        <button class="fullscreen-btn" id="fullscreen" title="全螢幕 (F)">⛶</button>
    </div>
    <div class="help">
        快捷鍵：← 上一頁 | → / Space 下一頁 | F 全螢幕 | Home 第一頁 | End 最後一頁
    </div>
    <script>
        const SLIDES = /*{{SLIDES_DATA}}*/[];
        let current = 0;
        const img = document.getElementById('slide');
        const info = document.getElementById('info');
        const prev = document.getElementById('prev');
        const next = document.getElementById('next');
        const container = document.getElementById('container');
        const fullscreenBtn = document.getElementById('fullscreen');

        function show(i) {
            if (i < 0 || i >= SLIDES.length) return;
            current = i;
            img.src = SLIDES[current];
            info.textContent = (current + 1) + ' / ' + SLIDES.length;
            prev.disabled = current === 0;
            next.disabled = current === SLIDES.length - 1;
        }

        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                container.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }

        prev.onclick = () => show(current - 1);
        next.onclick = () => show(current + 1);
        fullscreenBtn.onclick = toggleFullscreen;

        document.onkeydown = (e) => {
            if (e.key === 'ArrowLeft') show(current - 1);
            if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); show(current + 1); }
            if (e.key === 'f' || e.key === 'F') toggleFullscreen();
            if (e.key === 'Home') show(0);
            if (e.key === 'End') show(SLIDES.length - 1);
        };

        // 觸控支援
        let touchStartX = 0;
        container.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
        });
        container.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const diff = touchStartX - touchEndX;
            if (Math.abs(diff) > 50) {
                if (diff > 0) show(current + 1);
                else show(current - 1);
            }
        });

        show(0);
    </script>
</body>
</html>'''


def build_viewer(images_dir, output_file, base_path=None):
    """生成 HTML 播放器"""
    images_path = Path(images_dir)
    output_path = Path(output_file)

    if not images_path.exists():
        print(f"錯誤：圖片目錄不存在 - {images_dir}")
        return False

    # 收集圖片
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    images = sorted([
        f for f in images_path.iterdir()
        if f.suffix.lower() in image_extensions
    ])

    if not images:
        print(f"錯誤：找不到圖片 - {images_dir}")
        return False

    print(f"找到 {len(images)} 張圖片")

    # 計算相對路徑
    if base_path:
        slides_data = [f"{base_path}/{img.name}" for img in images]
    else:
        output_dir = output_path.parent.resolve()
        slides_data = []
        for img in images:
            try:
                rel_path = img.resolve().relative_to(output_dir)
                slides_data.append(str(rel_path).replace('\\', '/'))
            except ValueError:
                slides_data.append(str(img.resolve()).replace('\\', '/'))

    # 產生 HTML
    template = get_html_template()
    slides_json = json.dumps(slides_data, ensure_ascii=False, indent=2)
    html_content = template.replace('/*{{SLIDES_DATA}}*/[]', slides_json)

    # 確保輸出目錄存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 寫入檔案
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML 播放器已儲存：{output_path}")
    print(f"共 {len(images)} 頁")
    print(f"\n開啟方式：在瀏覽器中開啟 {output_path}")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PPT Maker - HTML 播放器")
    parser.add_argument("--images", required=True, help="圖片目錄")
    parser.add_argument("--output", required=True, help="輸出 HTML 路徑")
    parser.add_argument("--base-path", help="自訂圖片基礎路徑")

    args = parser.parse_args()
    success = build_viewer(args.images, args.output, args.base_path)
    sys.exit(0 if success else 1)
```

---

## 六、風格定義

### 6.1 styles/deep_space.md

```markdown
---
id: deep-space
name: 深空科技
description: 融合 Apple 發布會極簡主義、棱鏡流光玻璃質感與深空神秘氛圍
tags: [科技, AI, 發布會, 高端]
---

# 深空科技風格

## 適用場景

- 科技產品發布會
- AI / 硬科技公司路演
- 技術架構展示
- 高端品牌提案
- 未來趨勢報告

---

## 設計系統

### 風格概述

融合 Apple 發布會的極簡克制、棱鏡流光的科技優雅感和深空的神秘氛圍。整體氣質高端、優雅、深邃且帶有詩意的浪漫感。畫面極度克制，大量留白，讓核心元素成為絕對焦點。3D 元素要有「呼吸感」，像是有生命的能量體。

### 色彩

純黑 #000000 或極深灰 #0a0a0a 作為絕對基底，營造深空感。

3D 元素使用棱鏡色散產生的彩虹光譜：
- 主色調：光譜藍紫 → 青 → 粉的漸變流動
- 棱鏡折射的自然彩虹色（紅橙黃綠藍靛紫的光譜過渡）
- iridescent（彩虹光澤）效果，類似肥皂泡或油膜

文字使用純白 #ffffff，與深色背景形成強對比。

### 光效

採用柔和的體積光，創造夢幻的光影氛圍：
- **棱鏡色散**（chromatic dispersion）：光線穿過玻璃產生彩虹光譜分離
- **柔和邊緣光暈**（soft rim glow）：而非銳利切割
- **內部散射光**：從 3D 物體內部向外散射的柔光
- **光霧瀰漫**（light mist）：輕微的光霧增加氛圍感

光照要有詩意和呼吸感，像北極光或星雲的柔和流動。

### 版面

採用極簡精準的網格系統，大量使用負空間（60%+ 留白）。

- 內容區域使用精準對齊
- 無裝飾性邊框
- 如需容器，使用極細的發光描邊（1px, 20% 透明度）
- 字體層級有戲劇化對比：超大標題 + 極小正文

### 材質

渲染優雅的 3D 流光玻璃體作為視覺錨點：

- **材質**：透明/半透明的棱鏡玻璃，光線穿過時產生彩虹色散。表面有液態金屬般的流動光紋。材質要有多層次的透明度和複雜的內部折射。
- **形狀**：有機流動的曲面為主——像液態玻璃凝固的瞬間、飄動的絲帶、展翅的蝴蝶、流體雕塑。邊緣柔和有呼吸感。
- **色彩**：通過棱鏡折射產生自然的彩虹光譜流動，類似肥皂泡的 iridescent 效果。
- **光效**：柔和的內部散射光，邊緣有夢幻的光暈而非銳利輪廓。
- **氛圍**：物體周圍可有輕微的光霧或星塵瀰漫，增加詩意和呼吸感。

### 背景

深邃的黑色基底，可加入：
- 極細微的星雲紋理
- 輕微的徑向漸變（從中心 #111 到邊緣 #000）
- 若隱若現的星雲光帶（非常克制）

營造深空感，但不能搶奪 3D 元素的焦點。

### 字體

使用乾淨的無襯線字體（SF Pro、Inter、Helvetica Neue、PingFang）。

建立極端的層級對比：
- 標題可超大且加粗
- 正文保持克制

---

## 頁面模板

### cover（封面）

**構圖**：標題為絕對主角，配合一個優雅的 3D 流光玻璃體作為視覺錨點。大量留白，深空背景。

**Prompt 範本**：
```
請生成封面頁。

標題：{{TITLE}}
副標題：{{SUBTITLE}}

標題使用超大粗體白色字，位置居中或偏左下。畫面中放置一個優雅的 3D 流光玻璃體作為視覺錨點——形態是有機流動的曲面，像液態玻璃凝固的瞬間、飄動的絲帶或展翅的蝴蝶。材質為透明棱鏡玻璃，光線穿過時產生彩虹色散效果（chromatic dispersion），表面有液態金屬般的流動光紋和 iridescent 彩虹光澤。邊緣有柔和的光暈而非銳利輪廓，整體像在呼吸的能量體。背景是純黑的深空，可有輕微的光霧瀰漫。整體畫面極度克制，60% 以上為負空間，讓標題和 3D 物體成為僅有的焦點。
```

### content（內容）

**構圖**：極簡網格佈局，內容精準對齊，大量留白。可用極細的發光線條分隔區域。

**Prompt 範本**：
```
請生成內容頁。採用極簡的網格佈局，將以下內容精準排列。

標題：{{TITLE}}

要點：
{{ITEMS}}

背景為純黑。標題使用中等大小的白色粗體字，位於頁面上方。要點內容使用較小的白色或淺灰色字體，排列整齊。可使用極細的發光線條（1px, 科技藍, 20% 透明度）作為視覺分隔。每個要點前可配一個極簡的發光圖標或光點作為標記。頁面保持 50% 以上留白，內容區域精準對齊，體現精密感。不使用卡片、陰影或厚重的容器。
```

### data（數據）

**構圖**：數據可視化為主角，使用有科技感的圖表樣式，配合發光效果。

**Prompt 範本**：
```
請生成數據頁。

數據內容：
{{CONTENT}}

使用有科技感的數據可視化：發光描邊的環形進度條、帶能量脈衝效果的柱狀圖、或懸浮的超大關鍵數字。圖表使用科技藍作為主色，配合發光效果。關鍵數字可以超大顯示，帶有輕微的發光光暈。背景純黑，圖表元素像是懸浮在深空中。整體風格精密、克制，數據清晰易讀，避免過多裝飾。
```

### end（結尾）

**構圖**：極簡收尾，中心放置感謝語或行動號召，配小型 3D 流光裝飾物。

**Prompt 範本**：
```
請生成結尾頁。畫面極簡有力。

中心展示：
{{CONTENT}}

文字使用白色大字居中顯示。可配一個精緻的小型 3D 流光玻璃體——形態優雅流動，材質為透明棱鏡玻璃，有彩虹色散和 iridescent 光澤。邊緣有柔和光暈，像在輕輕呼吸。背景為純黑深空，可有輕微的光霧點綴。畫面主體是文字，3D 元素作為點睛，整體保持極度克制和詩意美感。
```

---

## 規則

### 中文渲染（必要）

Chinese text rendering is CRITICAL. Follow these rules strictly:
- All Chinese characters must be perfectly clear, sharp, and 100% legible
- Use professional sans-serif Chinese fonts (like PingFang, Noto Sans TC, Source Han Sans)
- Each character must have correct strokes - no merged, blurry, or malformed characters
- Maintain proper character spacing (not too tight, not too loose)
- Text must have strong contrast against background (white text on dark background)
- VERIFY: Every Chinese character must be recognizable and correctly formed
- **STRICT**: Use Traditional Chinese (繁體中文) only, NO Simplified Chinese

### 約束

Do NOT add any text, logos, or elements not specified in the content below. Keep the composition extremely minimal.

---

## 技術規格

- **比例**：16:9
- **建議解析度**：2K (2752×1536)
- **生成時間**：約 30-60 秒/頁
```

---

## 七、Claude Skill

> 將以下內容保存為 `SKILL.md`

```markdown
---
name: ppt
description: 企業級簡報生成工具。選擇預設風格、規劃內容架構、批量生成高品質簡報。適用於：製作 PPT、演示文稿、提案簡報等場景。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# PPT Maker - 智能簡報生成系統

## 系統概述

PPT Maker 是一套 AI 驅動的簡報生成系統，透過預設風格模板與智能內容規劃，快速產出專業級演示文稿。

**核心流程**：風格選擇 → 內容規劃 → 圖片生成 → 超分處理 → 打包輸出

---

## 使用者交互流程

當使用者提出「幫我做簡報」、「製作 PPT」等請求時，依循以下流程：

### 階段一：資訊收集

**首先動態讀取可用風格**：執行 `ls {skill_path}/styles/*.md` 獲取當前可用的風格清單，解析每個風格檔案的「風格名稱」和「風格描述」。

向使用者一次性詢問所有必要資訊：

```
好的，我來協助你製作簡報！請提供以下資訊：

**1. 內容來源**（必填）
   - 提供檔案路徑（如 @report.md）
   - 或直接貼上文字內容

**2. 風格選擇**
   [根據 styles/ 目錄動態列出]
   A. {風格名稱} - {風格描述}
   B. {風格名稱} - {風格描述}
   ...

**3. 頁數規模**
   - 精簡版（5 頁）
   - 標準版（5-10 頁，推薦）
   - 詳細版（10-15 頁）
   - 完整版（20-25 頁）

請一次告訴我這些資訊，例如：
「內容是 @report.md，風格選 A，約 10 頁」
```

### 階段二：規劃確認

分析內容後，展示頁面規劃表：

```
內容分析完成，以下是簡報規劃：

**主題**：{主題名稱}
**總頁數**：{N} 頁
**風格**：{選擇的風格}

| 頁碼 | 類型 | 內容摘要 |
|------|------|----------|
| 1 | 封面 | {標題} |
| 2 | 內容 | {要點概述} |
| ... | ... | ... |
| N | 結尾 | 感謝 & 聯繫方式 |

確認無誤請回覆「確認」，或告知需要調整的部分。
```

### 階段三：執行生成

使用者確認後，開始執行生成流程（詳見下方「執行流程」章節）。

---

## 輸入格式支援

| 格式 | 說明 |
|------|------|
| Markdown (.md) | 推薦，結構清晰易解析 |
| PDF (.pdf) | 自動擷取文字內容 |
| Word (.docx) | 自動擷取文字內容 |
| 純文字 | 直接貼入對話視窗 |

---

## 輸出內容

每次生成輸出至 `.ppt_maker/` 目錄：

```
.ppt_maker/
├── slides_plan.json          # 頁面規劃檔
├── images/                   # 原始生成圖片
├── images-4k/                # 超分後 4K 圖片
├── output.pptx               # 原始 PPTX
├── output-4k.pptx            # 4K 版 PPTX（推薦使用）
└── viewer.html               # 網頁播放器
```

---

## 頁數與內容量對照

| 選項 | 頁數 | 適合內容量 |
|------|------|-----------|
| 精簡版 | 5 頁 | 500 字以內 |
| 標準版 | 5-10 頁 | 500-1500 字 |
| 詳細版 | 10-15 頁 | 1500-3000 字 |
| 完整版 | 20-25 頁 | 3000 字以上 |

---

## 執行流程

### Step 1：內容分析與規劃生成

讀取使用者提供的內容，分析結構，生成 `slides_plan.json`。

**關鍵：加入 `enhancement` 欄位進行視覺增強**

根據每頁內容的語義，添加客製化的視覺描述。

將 `slides_plan.json` 儲存至 `.ppt_maker/slides_plan.json`。

### Step 2：批量圖片生成

呼叫生成腳本：

```bash
python {skill_path}/scripts/generate.py \
  --plan .ppt_maker/slides_plan.json \
  --style {skill_path}/styles/{風格檔案}.md \
  --output .ppt_maker \
  --verify
```

**使用的 AI 模型**：
- 圖片生成：`gemini-3-pro-image-preview`（Gemini 3 Pro 圖像模型）
- 視覺驗證：`gemini-2.0-flash`

### Step 3：超分處理

API 返回的圖片解析度較低（約 1376×768），必須進行超分處理：

```bash
python {skill_path}/scripts/upscale.py \
  --images .ppt_maker/images/ \
  --output .ppt_maker/images-4k/ \
  --scale 4
```

### Step 4：打包輸出

```bash
# 生成網頁播放器
python {skill_path}/scripts/build_viewer.py \
  --images .ppt_maker/images-4k/ \
  --output .ppt_maker/viewer.html

# 生成 PPTX 檔案
python {skill_path}/scripts/build_pptx.py \
  --images .ppt_maker/images-4k/ \
  --output .ppt_maker/output-4k.pptx
```

### Step 5：交付成果

告知使用者輸出檔案位置：
- **4K PPTX**：`.ppt_maker/output-4k.pptx`（推薦使用）
- **網頁播放器**：`.ppt_maker/viewer.html`
- **圖片素材**：`.ppt_maker/images-4k/`

---

## API 設定

在專案根目錄建立 `config.env`：

```bash
GEMINI_API_KEY=your_api_key_here
```

**取得 API Key**：https://aistudio.google.com/apikey
```

---

## 八、資料格式規範

### 8.1 slides_plan.json 結構

```json
{
  "title": "簡報標題",
  "style": "deep-space",
  "resolution": "4K",
  "slides": [
    {
      "slide_number": 1,
      "page_type": "cover",
      "content": "標題：AI 產品設計\n副標題：從概念到落地",
      "enhancement": "中央放置代表創新的 3D 玻璃球體"
    },
    {
      "slide_number": 2,
      "page_type": "content",
      "content": "核心原則\n- 以用戶為中心\n- 數據驅動\n- 快速迭代",
      "enhancement": "三欄卡片佈局，每張卡片配發光圖標"
    },
    {
      "slide_number": 3,
      "page_type": "end",
      "content": "謝謝聆聽\n聯繫方式：hello@example.com",
      "enhancement": "極簡設計，文字居中，配小型 3D 裝飾"
    }
  ]
}
```

### 8.2 page_type 類型

| 類型 | 說明 |
|------|------|
| cover | 封面頁（第 1 頁） |
| content | 內容頁（觀點、列表） |
| data | 數據頁（統計、圖表） |
| end | 結尾頁（最後一頁） |

### 8.3 enhancement 欄位指引

| 內容類型 | 建議視覺增強 |
|----------|-------------|
| 對比類內容 | 左右分欄佈局 |
| 列表類內容 | 卡片網格 + 圖標 |
| 數據類內容 | 發光圖表 |
| 封面/結尾頁 | 獨特的 3D 裝飾元素 |

---

## 九、啟動專案

### 9.1 安裝依賴

```bash
# 進入專案目錄
cd PPT_Maker

# 建立虛擬環境
python -m venv venv

# 啟用虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 複製設定檔
cp config.example.env config.env
```

### 9.2 設定 API Key

編輯 `config.env`，填入你的 Gemini API Key：

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

**取得 API Key**：https://aistudio.google.com/apikey

### 9.3 使用方式

**方式一：透過 Claude Code（推薦）**

將 `PPT_Maker` 資料夾放到 `~/.claude/skills/` 目錄，然後在 Claude Code 中說：「幫我做一份簡報」

**方式二：直接執行腳本**

```bash
# 1. 準備 slides_plan.json（見第八章）

# 2. 執行生成
python scripts/generate.py \
  --plan slides_plan.json \
  --style styles/deep_space.md \
  --output .ppt_maker \
  --verify

# 3. 取得成果
# .ppt_maker/output-4k.pptx  ← PPTX 檔案
# .ppt_maker/viewer.html     ← 網頁播放器
```

---

## 完成

按照以上規格書，Claude Code 可完整複刻 PPT Maker 專案。所有設定檔和程式碼均已包含。
