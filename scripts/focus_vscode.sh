#!/bin/bash
# Focus the correct VSCode window: try by PID first, fall back to app name
PID="${1:-}"
if [[ -n "$PID" ]]; then
    python3 -c "
import AppKit, sys
app = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_($PID)
if app:
    app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
    sys.exit(0)
sys.exit(1)
" 2>/dev/null && exit 0
fi
osascript -e 'tell application "Code" to activate' 2>/dev/null
