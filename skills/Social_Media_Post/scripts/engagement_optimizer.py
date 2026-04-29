#!/usr/bin/env python3
"""
Engagement Optimizer

Applies platform-specific optimization rules to social media content.

Usage:
    python engagement_optimizer.py --platform threads --content post-draft.md
"""

import argparse
import json
import sys
import re
from typing import Dict, List, Optional

PLATFORM_LIMITS = {
    'threads': 500,
    'x': 280,
    'linkedin': 3000,
    'facebook': 63206,
    'instagram': 2200
}

PLATFORM_HASHTAG_LIMITS = {
    'threads': 0,
    'x': 2,
    'linkedin': 5,
    'facebook': 0,
    'instagram': 30
}


def clean_content(content: str) -> str:
    """Remove boilerplate if present."""
    return content.strip()


def count_hashtags(content: str) -> int:
    return len(re.findall(r'#\w+', content))


def score_engagement(content: str, platform: str) -> Dict:
    """Calculate engagement score (1-10) based on heuristics."""
    score = 0
    reasons = []

    lines = content.split('\n')
    if lines:
        first_line = lines[0]
        if '?' in first_line:
            score += 2
            reasons.append("Hooks with a question")
        elif len(first_line) < 50:
            score += 1.5
            reasons.append("Concise hook")
        else:
            score += 1

    if any(x in content.lower() for x in ['✅', 'benefit', 'helps', 'new', 'update']):
        score += 2
        reasons.append("Clear value indicators")

    emoji_count = len(re.findall(r'[^\w\s,\.\!]', content))
    if emoji_count > 0:
        score += 2
        reasons.append("Uses emojis/formatting")

    if '?' in content[len(lines[0]):]:
        score += 2
        reasons.append("Asks for engagement")

    char_count = len(content)
    limit = PLATFORM_LIMITS.get(platform, 3000)

    if char_count <= limit:
        score += 2
        reasons.append("Fits character limit")
    else:
        score -= 2
        reasons.append("Exceeds character limit")

    return {
        "score": min(10, max(1, score)),
        "reasons": reasons
    }


def optimize_content(content: str, platform: str) -> Dict:
    """Optimize content for the specific platform."""

    warnings = []
    improvements = []
    optimized_text = content

    limit = PLATFORM_LIMITS.get(platform, 20000)
    if len(content) > limit:
        warnings.append(f"Content exceeds {platform} limit of {limit} chars (Current: {len(content)})")

    hashtag_limit = PLATFORM_HASHTAG_LIMITS.get(platform, 100)
    current_hashtags = count_hashtags(content)

    if platform == 'threads' and current_hashtags > 0:
        optimized_text = re.sub(r'#\w+', '', optimized_text)
        improvements.append("Removed hashtags (Threads algorithm ignores them)")
    elif current_hashtags > hashtag_limit:
        warnings.append(f"Too many hashtags for {platform}. Recommended: {hashtag_limit}, Found: {current_hashtags}")

    if platform == 'instagram':
        if 'http' in content:
            warnings.append("Instagram captions do not support clickable links. Use 'Link in Bio'.")

    if platform == 'x':
        if '\n\n' not in content and len(content) > 100:
            improvements.append("Consider adding line breaks for readability on X")

    engagement = score_engagement(optimized_text, platform)

    return {
        "optimized_content": optimized_text.strip(),
        "character_count": len(optimized_text),
        "character_limit": limit,
        "engagement_score": engagement['score'],
        "engagement_reasons": engagement['reasons'],
        "improvements": improvements,
        "warnings": warnings
    }


def main():
    parser = argparse.ArgumentParser(description='Optimize social media content')
    parser.add_argument('--platform', required=True,
                        choices=['threads', 'x', 'linkedin', 'facebook', 'instagram'],
                        help='Target platform')
    parser.add_argument('--content', required=True, help='Content text or file path')
    args = parser.parse_args()

    try:
        if args.content.endswith('.md') or args.content.endswith('.txt'):
            with open(args.content, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = args.content
    except Exception:
        content = args.content

    result = optimize_content(content, args.platform)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
