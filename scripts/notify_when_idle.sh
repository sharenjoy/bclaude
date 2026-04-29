#!/bin/bash
# Usage: notify_when_idle.sh [ask]
# "ask" mode: notify after WAIT_SECONDS if no new action, click focuses VSCode
# default mode: notify immediately if VSCode not frontmost
TIMESTAMP_FILE="/tmp/claude_notify_ts"
WAIT_SECONDS=30
MODE="${1:-stop}"

TS=$(date +%s)
echo "$TS" > "$TIMESTAMP_FILE"
CAPTURED_PID="${VSCODE_PID:-}"

FOCUS_CMD="bash /Users/ronald/.claude/scripts/focus_vscode.sh $CAPTURED_PID"

_notify_ask="afplay /System/Library/Sounds/Ping.aiff 2>/dev/null; /opt/homebrew/bin/terminal-notifier -message 'Claude 需要你回覆問題' -title 'Claude Code' -subtitle '點擊跳至正確視窗' -sound default -execute '$FOCUS_CMD' 2>/dev/null"

if [[ "$MODE" == "ask" ]]; then
    nohup bash -c "sleep $WAIT_SECONDS; SAVED=\$(cat '$TIMESTAMP_FILE' 2>/dev/null); [[ \"\$SAVED\" == '$TS' ]] && $_notify_ask" > /dev/null 2>&1 &
    exit 0
fi

FRONTMOST=$(osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true' 2>/dev/null)

if [[ "$FRONTMOST" != "Code" ]]; then
    afplay /System/Library/Sounds/Glass.aiff 2>/dev/null
    /opt/homebrew/bin/terminal-notifier -message "任務已完成" -title "Claude Code" -subtitle "✓ 完成" -sound default -execute "$FOCUS_CMD" 2>/dev/null
    osascript -e 'display notification "任務已完成" with title "Claude Code" sound name "Glass"' 2>/dev/null
fi
