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
