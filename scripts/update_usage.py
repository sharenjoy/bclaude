#!/usr/bin/env python3
"""
Auto-update ~/.claude/USAGE.md dynamic sections.
Triggered by PostToolUse hook when agents/, skills/, rules/, settings.json, or CLAUDE.md change.
"""

import json
import re
import sys
from pathlib import Path

CLAUDE = Path.home() / '.claude'
USAGE = CLAUDE / 'USAGE.md'


def parse_frontmatter(content: str) -> dict:
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    result = {}
    lines = match.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ':' not in line or line.startswith(' '):
            i += 1
            continue
        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip()
        if value in ('>', '|'):
            # 收集後續縮排行
            parts = []
            i += 1
            while i < len(lines) and (lines[i].startswith(' ') or lines[i].startswith('\t')):
                parts.append(lines[i].strip())
                i += 1
            result[key] = ' '.join(parts) if value == '>' else '\n'.join(parts)
        else:
            # 去除 YAML 字串引號
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            result[key] = value
            i += 1
    return result


def permission_tier(tools: str) -> str:
    parts = [t.strip() for t in tools.split(',')]
    if 'Bash' in parts:
        return '⚡ +Bash'
    if 'Write' in parts or 'Edit' in parts:
        return '📝 +Write'
    return '🔒 Read-Only'


def build_rules_table() -> str:
    rows = []
    rules_dir = CLAUDE / 'rules'
    if not rules_dir.exists():
        return '| 規則檔 | 說明 |\n|--------|------|'
    for f in sorted(rules_dir.glob('*.md')):
        content = f.read_text()
        # 取第一個 # 標題作為名稱
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        name = title_match.group(1).strip() if title_match else f.stem
        # 取第一個非空、非標題行作為說明
        desc = ''
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('```'):
                desc = line
                break
        if len(desc) > 50:
            desc = desc[:50] + '…'
        rows.append(f'| `{f.name}` | {name} | {desc} |')

    header = '| 檔案 | 規則名稱 | 說明 |\n|------|----------|------|'
    return header + ('\n' + '\n'.join(rows) if rows else '')


def build_skills_table() -> str:
    rows = []
    for skill_dir in sorted((CLAUDE / 'skills').iterdir()):
        skill_file = skill_dir / 'SKILL.md'
        if not skill_file.exists():
            continue
        fm = parse_frontmatter(skill_file.read_text())
        name = fm.get('name') or skill_dir.name
        desc = fm.get('description', '')
        # 取第一句（全形/半形句號前），超過 50 字截斷加 …
        short = re.split(r'[。.]', desc)[0].strip()
        if len(short) > 50:
            short = short[:50] + '…'
        rows.append(f'| `{name}` | {short} |')

    header = '| Skill | 用途 |\n|-------|------|'
    return header + ('\n' + '\n'.join(rows) if rows else '')


def build_agents_table() -> str:
    skip = {'AGENTS.md', 'ARCHITECTURE.md'}
    rows = []
    for f in sorted((CLAUDE / 'agents').glob('*.md')):
        if f.name in skip:
            continue
        fm = parse_frontmatter(f.read_text())
        name = fm.get('name')
        if not name:
            continue
        tools = fm.get('tools', '')
        tier = permission_tier(tools)
        max_turns = fm.get('maxTurns', '-')
        rows.append(f'| `{name}` | {tools} | {tier} | {max_turns} |')

    header = (
        '| Agent | tools | 權限層級 | maxTurns |\n'
        '|-------|-------|---------|---------|'
    )
    return header + ('\n' + '\n'.join(rows) if rows else '')


def build_hooks_table() -> str:
    settings = json.loads((CLAUDE / 'settings.json').read_text())
    hooks = settings.get('hooks', {})
    event_labels = {
        'Notification': 'Claude 需要回應（Notification）',
        'Stop':         'Claude 完成任務（Stop）',
        'PreToolUse':   '工具執行前（PreToolUse）',
        'PostToolUse':  '工具執行後（PostToolUse）',
    }
    rows = []
    for event, handlers in hooks.items():
        label = event_labels.get(event, event)
        for handler in handlers:
            matcher = handler.get('matcher', '')
            suffix = f'（matcher: {matcher}）' if matcher else ''
            for hook in handler.get('hooks', []):
                htype = hook.get('type', '')
                if htype == 'command':
                    rows.append(f'| {label} | command{suffix} |')
                elif htype in ('agent', 'prompt'):
                    rows.append(f'| {label} | {htype}{suffix} |')

    header = '| 事件 | 行為 |\n|------|------|'
    return header + ('\n' + '\n'.join(rows) if rows else '')


def build_permissions() -> str:
    settings = json.loads((CLAUDE / 'settings.json').read_text())
    perms = settings.get('permissions', {})
    allow = '\n'.join(perms.get('allow', []))
    deny  = '\n'.join(perms.get('deny', []))
    return (
        f'### 自動允許（不提示）\n\n```\n{allow}\n```\n\n'
        f'### 永遠拒絕\n\n```\n{deny}\n```'
    )


def replace_section(content: str, marker: str, new_body: str) -> str:
    pattern = rf'(<!-- AUTO:{marker}_START -->).*?(<!-- AUTO:{marker}_END -->)'
    repl = rf'\g<1>\n{new_body}\n\g<2>'
    return re.sub(pattern, repl, content, flags=re.DOTALL)


def main():
    if not USAGE.exists():
        print('USAGE.md not found, skipping.', file=sys.stderr)
        return

    content = USAGE.read_text()
    if '<!-- AUTO:' not in content:
        print('No AUTO markers in USAGE.md, skipping.', file=sys.stderr)
        return

    content = replace_section(content, 'RULES',       build_rules_table())
    content = replace_section(content, 'SKILLS',      build_skills_table())
    content = replace_section(content, 'AGENTS',      build_agents_table())
    content = replace_section(content, 'HOOKS',       build_hooks_table())
    content = replace_section(content, 'PERMISSIONS', build_permissions())
    USAGE.write_text(content)
    print('USAGE.md updated.')


if __name__ == '__main__':
    main()
