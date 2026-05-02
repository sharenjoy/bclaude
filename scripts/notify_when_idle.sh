#!/bin/bash
# Usage: notify_when_idle.sh [ask]
MODE="${1:-stop}"
CAPTURED_PID="${VSCODE_PID:-}"
FOCUS_CMD="bash /Users/ronald/.claude/scripts/focus_vscode.sh $CAPTURED_PID"
DIR_NAME=$(basename "${PWD:-$(pwd)}")

if [[ "$MODE" == "ask" ]]; then
    afplay /System/Library/Sounds/Ping.aiff 2>/dev/null
    /opt/homebrew/bin/terminal-notifier -message "Claude 需要你回覆問題" -title "CC @ ${DIR_NAME}" -subtitle "點擊跳至正確視窗" -execute "$FOCUS_CMD" 2>/dev/null
else
    afplay /System/Library/Sounds/Glass.aiff 2>/dev/null
    /opt/homebrew/bin/terminal-notifier -message "任務已完成" -title "CC @ ${DIR_NAME}" -subtitle "✓ 完成" -execute "$FOCUS_CMD" 2>/dev/null
fi
