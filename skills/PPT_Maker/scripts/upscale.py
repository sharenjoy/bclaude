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
