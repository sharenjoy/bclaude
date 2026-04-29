#!/usr/bin/env python3
"""
AutoResearch Description Optimization Loop。
讓 Claude 自動測試並改進 SKILL.md 的 description 欄位，
使 skill 在對的時機觸發、在不對的時機不觸發。

前置需求（預設 CLI 模式）：
  已安裝 Claude Code CLI（claude 指令可用）

前置需求（--api 模式）：
  pip install anthropic
  export ANTHROPIC_API_KEY=...

trigger-eval.json 格式:
  {
    "skill_name": "my-skill",
    "queries": [
      {"prompt": "...", "should_trigger": true},
      {"prompt": "...", "should_trigger": false}
    ]
  }

用法:
  # 預設：使用 Claude Code CLI（走 Claude Pro 訂閱）
  skill-loop --verbose

  # 使用 Anthropic API（需要 API credits）
  skill-loop --api --verbose
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ── SKILL.md 讀寫 ────────────────────────────────────────────────────────────

def load_description(skill_path: Path) -> str:
    content = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"^description:\s*[>|]?\s*\n((?:[ \t]+.+\n?)+)", content, re.MULTILINE)
    if match:
        lines = match.group(1).splitlines()
        return " ".join(l.strip() for l in lines if l.strip())
    match = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return ""


def save_description(skill_path: Path, new_desc: str):
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")
    wrapped = "  " + new_desc.replace(". ", ".\n  ")
    new_block = f"description: >\n{wrapped}\n"
    new_content = re.sub(
        r"description:.*?(?=\n\w|\n---)",
        new_block.rstrip(),
        content,
        flags=re.DOTALL,
    )
    skill_md.write_text(new_content, encoding="utf-8")


# ── Claude 呼叫抽象層 ─────────────────────────────────────────────────────────

def find_claude_binary() -> str:
    path = shutil.which("claude")
    if path:
        return path
    result = subprocess.run(["zsh", "-lc", "which claude"], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    raise RuntimeError(
        "找不到 claude 指令。請安裝 Claude Code CLI：npm install -g @anthropic-ai/claude-code"
    )


def call_claude(prompt: str, *, use_api: bool, client=None, model: str, claude_bin: str = "claude") -> str:
    if use_api:
        response = client.messages.create(
            model=model,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    result = subprocess.run(
        [claude_bin, "-p", prompt],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip() or "未知錯誤"
        raise RuntimeError(f"claude CLI 執行失敗：{err}")
    return result.stdout.strip()


# ── 評估觸發行為 ─────────────────────────────────────────────────────────────

TRIGGER_PROMPT = """\
你是一個評估 Claude Code skill 觸發行為的評估員。

以下是某個 skill 的 description（用來讓 Claude 判斷何時啟動這個 skill）：
---
{description}
---

使用者輸入：
{prompt}

問題：根據上面的 description，Claude 是否應該啟動這個 skill 來處理這個使用者輸入？

只回答 YES 或 NO，不要解釋。"""


def evaluate_triggers(
    description: str,
    queries: list,
    *,
    use_api: bool,
    client,
    model: str,
    claude_bin: str = "claude",
    verbose: bool = False,
) -> list[dict]:
    results = []
    for item in queries:
        prompt_text = item["prompt"]
        should_trigger = item["should_trigger"]

        answer = call_claude(
            TRIGGER_PROMPT.format(description=description, prompt=prompt_text),
            use_api=use_api,
            client=client,
            model=model,
            claude_bin=claude_bin,
        ).upper()
        triggered = answer.startswith("YES")
        passed = triggered == should_trigger

        if verbose:
            expected = "觸發" if should_trigger else "不觸發"
            actual = "觸發" if triggered else "不觸發"
            status = "✓" if passed else "✗"
            print(f"  {status} 預期{expected}／實際{actual}：{prompt_text[:55]}")

        results.append({
            "prompt": prompt_text,
            "should_trigger": should_trigger,
            "triggered": triggered,
            "passed": passed,
        })
    return results


# ── 請 Claude 改進 description ───────────────────────────────────────────────

IMPROVE_PROMPT = """\
你是一個 Claude Code skill description 的優化專家。

目前的 description：
{description}

以下測試案例的觸發行為與預期不符：
{failures}

請生成一個改進後的 description，修正上述失敗案例，同時不影響原本正確觸發的案例。

要求：
1. description 用繁體中文撰寫，可包含英文關鍵詞
2. 只回傳 description 的純文字內容，不加引號、標題或說明
3. 長度控制在 100–300 字之間"""


def suggest_improvement(
    description: str,
    failed: list,
    *,
    use_api: bool,
    client,
    model: str,
    claude_bin: str = "claude",
) -> str:
    failures_text = "\n".join(
        f"- 「{c['prompt']}」{'應觸發但未觸發' if c['should_trigger'] else '不應觸發但觸發了'}"
        for c in failed
    )
    return call_claude(
        IMPROVE_PROMPT.format(description=description, failures=failures_text),
        use_api=use_api,
        client=client,
        model=model,
        claude_bin=claude_bin,
    )


# ── 錯誤訊息（API 模式） ──────────────────────────────────────────────────────

def _api_error_message(e: Exception) -> str:
    try:
        import anthropic
    except ImportError:
        return str(e)

    if isinstance(e, anthropic.AuthenticationError):
        return "API 金鑰無效或未設定。請確認環境變數 ANTHROPIC_API_KEY 是否正確。"
    if isinstance(e, anthropic.BadRequestError):
        msg = str(e)
        if "credit balance is too low" in msg or "insufficient" in msg.lower():
            return (
                "Anthropic API 帳戶餘額不足。\n"
                "  → 請前往 https://console.anthropic.com/settings/billing 充值後再試。\n"
                "  → 注意：Claude Pro 訂閱無法用於 API，需另外購買 API credits。\n"
                "  → 或直接執行 skill-loop（不加 --api）改用 Claude Code CLI。"
            )
        return f"API 請求格式錯誤：{e}"
    if isinstance(e, anthropic.RateLimitError):
        return "已達到 API 速率限制，請稍後再試。"
    if isinstance(e, anthropic.APIConnectionError):
        return "無法連線至 Anthropic API，請確認網路連線。"
    if isinstance(e, anthropic.APIStatusError):
        return f"API 回傳錯誤（HTTP {e.status_code}）：{e.message}"
    return f"未預期的錯誤：{e}"


# ── 主流程 ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AutoResearch Description Optimization Loop")
    parser.add_argument("--skill-path", default="./", help="Skill 目錄路徑（預設：當前目錄）")
    parser.add_argument("--eval-set", default="trigger-eval.json", help="eval 測試集路徑（預設：trigger-eval.json）")
    parser.add_argument("--api", action="store_true", help="使用 Anthropic API（預設：Claude Code CLI）")
    parser.add_argument("--model", default="claude-sonnet-4-6", help="模型 ID（僅 --api 模式有效）")
    parser.add_argument("--max-iterations", type=int, default=5, help="最大迭代次數")
    parser.add_argument("--target-score", type=float, default=0.9, help="目標通過率 0–1")
    parser.add_argument("--verbose", action="store_true", help="顯示每個測試案例結果")
    parser.add_argument("--dry-run", action="store_true", help="不寫入 SKILL.md")
    args = parser.parse_args()

    skill_path = Path(args.skill_path).expanduser()
    eval_path = Path(args.eval_set)

    for p, label in [(skill_path, "skill 目錄"), (eval_path, "eval-set 檔案")]:
        if not p.exists():
            print(f"\n❌ 找不到 {label}: {p}\n", file=sys.stderr)
            sys.exit(1)

    with open(eval_path, encoding="utf-8") as f:
        eval_data = json.load(f)

    queries = eval_data.get("queries", [])
    if not queries:
        print("\n❌ trigger-eval.json 中沒有 queries\n", file=sys.stderr)
        sys.exit(1)

    client = None
    claude_bin = "claude"
    if args.api:
        try:
            import anthropic
            client = anthropic.Anthropic()
        except ImportError:
            print("\n❌ 缺少套件：請先執行 pip install anthropic\n", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            claude_bin = find_claude_binary()
        except RuntimeError as e:
            print(f"\n❌ {e}\n", file=sys.stderr)
            sys.exit(1)

    provider_label = f"Anthropic API ({args.model})" if args.api else f"Claude Code CLI ({claude_bin})"
    print(f"\n{'='*60}")
    print(f"AutoResearch Description Optimization")
    print(f"Skill: {skill_path.name}  |  模式: {provider_label}")
    print(f"目標通過率: {args.target_score*100:.0f}%  |  最大迭代: {args.max_iterations}")
    print(f"{'='*60}\n")

    best_description = load_description(skill_path)
    best_score = 0.0
    history = []

    for iteration in range(1, args.max_iterations + 1):
        print(f"── 迭代 {iteration}/{args.max_iterations} ──")
        results = evaluate_triggers(
            best_description, queries,
            use_api=args.api, client=client, model=args.model,
            claude_bin=claude_bin, verbose=args.verbose,
        )

        passed = sum(1 for r in results if r["passed"])
        score = passed / len(results)
        print(f"通過率：{passed}/{len(results)} ({score*100:.1f}%)")

        history.append({"iteration": iteration, "score": score, "description": best_description})

        if score > best_score:
            best_score = score

        if score >= args.target_score:
            print(f"\n✓ 達到目標通過率，停止迭代。")
            break

        if iteration < args.max_iterations:
            failed = [r for r in results if not r["passed"]]
            print(f"改進中（{len(failed)} 個失敗案例）...")
            best_description = suggest_improvement(
                best_description, failed,
                use_api=args.api, client=client, model=args.model, claude_bin=claude_bin,
            )
        print()

    print(f"\n{'='*60}")
    print(f"最佳通過率：{best_score*100:.1f}%")
    print(f"\n最佳 description：\n{best_description}")
    print(f"{'='*60}\n")

    results_dir = skill_path / "evals"
    results_dir.mkdir(exist_ok=True)
    results_path = results_dir / "description_optimization_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(
            {"best_description": best_description, "best_score": best_score, "history": history},
            f, ensure_ascii=False, indent=2,
        )
    print(f"結果已儲存至 {results_path}")

    if not args.dry_run:
        save_description(skill_path, best_description)
        print(f"已更新 {skill_path / 'SKILL.md'} 的 description。")
    else:
        print("(--dry-run：未寫入 SKILL.md)")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"\n❌ {e}\n", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷執行。\n", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        try:
            import anthropic
            if isinstance(e, anthropic.APIError):
                print(f"\n❌ {_api_error_message(e)}\n", file=sys.stderr)
                sys.exit(1)
        except ImportError:
            pass
        print(f"\n❌ 執行失敗：{e}\n", file=sys.stderr)
        sys.exit(1)
