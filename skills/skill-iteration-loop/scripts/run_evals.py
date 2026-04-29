#!/usr/bin/env python3
"""
執行 evals.json 中定義的 Binary Eval 斷言測試。

用法:
  python scripts/run_evals.py --evals evals/evals.json --output-dir iteration-1/
  python scripts/run_evals.py --evals evals/evals.json --output-dir iteration-1/ --variant with_skill
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


# ── 斷言執行器 ──────────────────────────────────────────────────────────────

def check_file_exists(output_dir: Path, expected: str, **_) -> tuple[bool, str]:
    target = output_dir / expected
    if target.exists():
        return True, f"✓ 找到 {expected}"
    return False, f"✗ 找不到 {expected}"


def check_word_count_gte(output_dir: Path, expected: int, file: str = None, **_) -> tuple[bool, str]:
    files = [output_dir / file] if file else [
        *output_dir.glob("*.txt"), *output_dir.glob("*.md")
    ]
    total = sum(
        len(f.read_text(encoding="utf-8").split())
        for f in files if f.exists()
    )
    if total >= expected:
        return True, f"✓ 字數 {total} >= {expected}"
    return False, f"✗ 字數 {total} < {expected}"


def check_contains_text(output_dir: Path, expected: str, file: str = None, **_) -> tuple[bool, str]:
    files = [output_dir / file] if file else list(output_dir.glob("*.*"))
    for f in files:
        if f.exists() and f.is_file():
            try:
                if expected in f.read_text(encoding="utf-8"):
                    return True, f'✓ 包含文字: "{expected}"'
            except Exception:
                pass
    return False, f'✗ 找不到文字: "{expected}"'


def check_line_count_gte(output_dir: Path, expected: int, file: str = None, **_) -> tuple[bool, str]:
    files = [output_dir / file] if file else list(output_dir.glob("*.*"))
    for f in files:
        if f.exists() and f.is_file():
            try:
                count = len([l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()])
                if count >= expected:
                    return True, f"✓ 行數 {count} >= {expected}"
                return False, f"✗ 行數 {count} < {expected}"
            except Exception:
                pass
    return False, "✗ 找不到可計算行數的文件"


def check_json_key_exists(output_dir: Path, expected: str, file: str = None, **_) -> tuple[bool, str]:
    files = [output_dir / file] if file else list(output_dir.glob("*.json"))
    for f in files:
        if f.exists():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                keys = expected.split(".")
                node = data
                for k in keys:
                    node = node[k]
                return True, f'✓ JSON key "{expected}" 存在'
            except (KeyError, TypeError, json.JSONDecodeError):
                pass
    return False, f'✗ JSON key "{expected}" 不存在'


CHECKERS = {
    "file_exists": check_file_exists,
    "word_count_gte": check_word_count_gte,
    "contains_text": check_contains_text,
    "line_count_gte": check_line_count_gte,
    "json_key_exists": check_json_key_exists,
}


# ── 核心邏輯 ────────────────────────────────────────────────────────────────

def run_assertions(assertions: list, output_dir: Path) -> list[dict]:
    results = []
    for a in assertions:
        name = a.get("name", "unnamed")
        check = a.get("check")
        expected = a.get("expected")
        file = a.get("file")

        if check not in CHECKERS:
            results.append({"name": name, "passed": False, "message": f"✗ 未知 check 類型: {check}"})
            continue

        passed, message = CHECKERS[check](output_dir, expected, file=file)
        results.append({"name": name, "passed": passed, "message": message})
    return results


def main():
    parser = argparse.ArgumentParser(description="執行 Binary Eval 斷言測試")
    parser.add_argument("--evals", required=True, help="evals.json 路徑")
    parser.add_argument("--output-dir", required=True, help="迭代根目錄（如 iteration-1/）")
    parser.add_argument(
        "--variant",
        choices=["with_skill", "without_skill", "both"],
        default="both",
        help="測試哪個版本的輸出",
    )
    args = parser.parse_args()

    evals_path = Path(args.evals)
    if not evals_path.exists():
        print(f"錯誤：找不到 {evals_path}", file=sys.stderr)
        sys.exit(1)

    with open(evals_path, encoding="utf-8") as f:
        data = json.load(f)

    skill_name = data.get("skill_name", "unknown")
    evals = data.get("evals", [])
    output_root = Path(args.output_dir)
    variants = ["with_skill", "without_skill"] if args.variant == "both" else [args.variant]

    benchmark = {
        "skill_name": skill_name,
        "timestamp": datetime.now().isoformat(),
        "variant": args.variant,
        "evals": [],
    }
    total_pass = total_all = 0

    print(f"\n{'='*60}")
    print(f"Skill: {skill_name}  |  迭代目錄: {args.output_dir}")
    print(f"{'='*60}\n")

    for item in evals:
        eval_id = item.get("id")
        prompt = item.get("prompt", "")
        assertions = item.get("assertions", [])

        print(f"Eval #{eval_id}: {prompt[:65]}{'...' if len(prompt) > 65 else ''}")

        eval_result = {"id": eval_id, "prompt": prompt, "variants": {}}

        for variant in variants:
            variant_dir = output_root / f"eval-{eval_id}" / variant / "outputs"

            if not variant_dir.exists():
                print(f"  [{variant}] ⚠ 目錄不存在: {variant_dir}")
                eval_result["variants"][variant] = {"skipped": True}
                continue

            results = run_assertions(assertions, variant_dir)
            passed = sum(1 for r in results if r["passed"])
            total_pass += passed
            total_all += len(results)

            print(f"  [{variant}] {passed}/{len(results)} 通過")
            for r in results:
                print(f"    {r['message']}")

            eval_result["variants"][variant] = {
                "passed": passed,
                "total": len(results),
                "results": results,
            }

        benchmark["evals"].append(eval_result)
        print()

    rate = (total_pass / total_all * 100) if total_all > 0 else 0
    benchmark["summary"] = {
        "total_assertions": total_all,
        "passed": total_pass,
        "failed": total_all - total_pass,
        "pass_rate": f"{rate:.1f}%",
    }

    print(f"{'='*60}")
    print(f"總結：{total_pass}/{total_all} 通過（{rate:.1f}%）")
    print(f"{'='*60}\n")

    benchmark_path = output_root / "benchmark.json"
    with open(benchmark_path, "w", encoding="utf-8") as f:
        json.dump(benchmark, f, ensure_ascii=False, indent=2)
    print(f"已寫入 {benchmark_path}")


if __name__ == "__main__":
    main()
