#!/usr/bin/env python3
"""
Thread Generator

Splits long content into platform-appropriate threaded posts.

Usage:
    python thread_generator.py --platform x --content full-announcement.md --max-posts 5
"""

import argparse
import json
import sys
import re
from typing import List, Dict

PLATFORM_LIMITS = {
    'x': 280,
    'threads': 500,
    'linkedin': 3000
}


def split_text_smart(text: str, limit: int) -> List[str]:
    """Split text into chunks aiming for sentence boundaries."""
    chunks = []
    current_chunk = ""

    # Reserve space for counter " (1/5)" approx 8 chars
    effective_limit = limit - 8

    paragraphs = text.split('\n\n')

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= effective_limit:
            current_chunk += ("\n\n" if current_chunk else "") + para
        else:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            if len(para) > effective_limit:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sent in sentences:
                    if len(current_chunk) + len(sent) + 1 <= effective_limit:
                        current_chunk += (" " if current_chunk else "") + sent
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sent
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def generate_thread(content: str, platform: str, max_posts: int) -> List[Dict]:
    """Generate threaded posts from content."""
    limit = PLATFORM_LIMITS.get(platform, 280)

    raw_chunks = split_text_smart(content, limit)

    if max_posts and len(raw_chunks) > max_posts:
        raw_chunks = raw_chunks[:max_posts]

    total = len(raw_chunks)
    formatted_posts = []

    for i, chunk in enumerate(raw_chunks):
        formatted_posts.append({
            "index": i + 1,
            "total": total,
            "text": chunk,
            "char_count": len(chunk),
            "display": f"[{i+1}/{total}] {chunk}"
        })

    return formatted_posts


def main():
    parser = argparse.ArgumentParser(description='Generate social media threads')
    parser.add_argument('--platform', required=True,
                        choices=['x', 'threads', 'linkedin'],
                        help='Target platform')
    parser.add_argument('--content', required=True, help='Content text or file path')
    parser.add_argument('--max-posts', type=int, default=10, help='Maximum number of posts in thread')
    args = parser.parse_args()

    try:
        if args.content.endswith('.md') or args.content.endswith('.txt'):
            with open(args.content, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = args.content
    except Exception:
        content = args.content

    thread = generate_thread(content, args.platform, args.max_posts)

    output = {
        "platform": args.platform,
        "total_posts": len(thread),
        "posts": thread
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
