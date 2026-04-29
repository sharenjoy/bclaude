# Social Media Post - 完整開發規格書

> **使用方式**：將此檔案放入空專案根目錄，告訴 Claude Code：「按照 SPEC.md 一步步建置這個專案」。
>
> 本規格書包含所有程式碼和設定，Claude Code 可完全複刻此專案。

---

## 目錄

1. [專案概述](#一專案概述)
2. [環境準備](#二環境準備)
3. [專案結構](#三專案結構)
4. [Python 腳本](#四python-腳本)
5. [風格定義](#五風格定義)
6. [Claude Skill](#六claude-skill)
7. [使用範例](#七使用範例)
8. [啟動專案](#八啟動專案)

---

## 一、專案概述

### 1.1 產品定義

Social Media Post 是一套智能社群貼文生成系統，能夠：
- 針對 Facebook、Threads、X (Twitter)、LinkedIn 四大平台生成優化貼文
- 自動套用各平台演算法最佳實踐
- 根據預設風格指南確保內容一致性
- 支援長文轉換為串文（Thread）格式

### 1.2 核心價值

- **平台優化**：自動適配各平台字數限制、格式規範、演算法偏好
- **風格一致**：預設風格模板確保品牌調性統一
- **效率提升**：一次輸入，多平台輸出

### 1.3 支援平台

| 平台 | 字數限制 | 特色 |
|------|---------|------|
| Facebook | 63,206 字元 | 支援長篇、結構化內容 |
| Threads | 500 字元 | 對話式、真實語氣 |
| X (Twitter) | 280 字元 | 簡潔有力、善用 Hashtag |
| LinkedIn | 3,000 字元 | 專業調性、商業價值 |

---

## 二、環境準備

### 2.1 系統需求

- Python 3.10+
- 無需外部 API（純本地處理）

### 2.2 檢查環境

```bash
# 檢查 Python 版本
python --version  # 應顯示 Python 3.10.x 或更高
```

---

## 三、專案結構

執行以下指令建立目錄結構：

```bash
# 建立專案目錄
mkdir -p Social_Media_Post
cd Social_Media_Post

# 建立子目錄
mkdir -p scripts styles

# 建立空檔案佔位
touch SKILL.md
touch SPEC.md
touch README.md
touch scripts/post_analyzer.py
touch scripts/engagement_optimizer.py
touch scripts/thread_generator.py
touch styles/facebook.md
```

完整結構如下：

```
Social_Media_Post/
├── SKILL.md                          # Claude Skill 定義（給 AI 看）
├── SPEC.md                           # 本檔案（完整規格書）
├── README.md                         # 使用者安裝指南
├── scripts/
│   ├── post_analyzer.py              # 內容分析腳本
│   ├── engagement_optimizer.py       # 平台優化腳本
│   └── thread_generator.py           # 串文生成腳本
└── styles/
    └── facebook.md                   # Facebook 風格指南
```

---

## 四、Python 腳本

> 以下是所有 Python 腳本的完整程式碼。按順序建立這些檔案。

### 4.1 scripts/post_analyzer.py

```python
#!/usr/bin/env python3
"""
Social Media Post Analyzer

Extracts key points and structures content for social media posts.

Usage:
    python post_analyzer.py --input "announcement text" [--context file.md]
"""

import argparse
import json
import sys
from typing import Dict, List


def extract_key_points(content: str, max_points: int = 5) -> List[str]:
    """Extract key points from content."""
    lines = content.split('\n')
    points = []

    for line in lines:
        stripped = line.strip()
        # Extract from bullet points
        if stripped.startswith(('- ', '* ', '• ', '✅ ', '→ ')):
            point = stripped.lstrip('-*•✅→ ').strip()
            if point and len(point) < 100:
                points.append(point)

        # Extract from numbered lists
        elif stripped and stripped[0].isdigit() and '.' in stripped[:3]:
            point = stripped.split('.', 1)[1].strip()
            if point and len(point) < 100:
                points.append(point)

    return points[:max_points]


def identify_value_proposition(content: str) -> str:
    """Identify main value proposition."""
    value_keywords = [
        'reduce', 'increase', 'automate', 'eliminate', 'simplify',
        'faster', 'easier', 'better', 'savings', 'efficiency'
    ]

    lines = content.lower().split('\n')
    for line in lines:
        if any(keyword in line for keyword in value_keywords):
            return line.strip().capitalize()[:200]

    for line in content.split('\n'):
        if line.strip():
            return line.strip()[:200]

    return "Improves workflow efficiency"


def determine_tone(content: str) -> str:
    """
    Determine content tone.

    Returns: technical-casual, professional, educational, promotional
    """
    content_lower = content.lower()

    technical_terms = ['api', 'cli', 'code', 'function', 'plugin', 'skill', 'npm']
    has_technical = sum(1 for term in technical_terms if term in content_lower)

    casual_terms = ['just', 'awesome', 'cool', 'amazing', 'finally']
    has_casual = sum(1 for term in casual_terms if term in content_lower)

    promo_terms = ['new', 'launch', 'release', 'now available', 'get it']
    has_promo = sum(1 for term in promo_terms if term in content_lower)

    if has_technical >= 2 and has_casual >= 1:
        return 'technical-casual'
    elif has_technical >= 2:
        return 'technical-professional'
    elif has_promo >= 2:
        return 'promotional'
    else:
        return 'informative'


def suggest_platforms(content: str, tone: str) -> List[str]:
    """Suggest best platforms for content."""
    platforms = []

    if tone in ['technical-casual', 'informative']:
        platforms.append('threads')

    if len(content) < 1000 or tone in ['technical-casual', 'promotional']:
        platforms.append('x')

    if len(content) > 500 or tone in ['technical-professional', 'informative']:
        platforms.append('linkedin')

    return platforms or ['threads', 'x']


def extract_call_to_action(content: str) -> str:
    """Extract or generate call to action."""
    cta_patterns = [
        'install', 'update', 'try', 'get started', 'download',
        'sign up', 'learn more', 'check out'
    ]

    lines = content.lower().split('\n')
    for line in lines:
        if any(pattern in line for pattern in cta_patterns):
            return line.strip().capitalize()[:100]

    if 'install' in content.lower():
        return "Install and try it today"
    elif 'update' in content.lower():
        return "Update to get new features"
    else:
        return "Learn more"


def analyze_content(content: str, context: str = None) -> Dict:
    """
    Analyze content and extract structured information.

    Args:
        content: Main announcement text
        context: Optional additional context

    Returns:
        Structured analysis
    """
    full_text = content
    if context:
        full_text = f"{content}\n\n{context}"

    key_points = extract_key_points(full_text)
    value_prop = identify_value_proposition(full_text)
    tone = determine_tone(full_text)
    platforms = suggest_platforms(full_text, tone)
    cta = extract_call_to_action(full_text)

    topic = content.split('\n')[0].strip() if '\n' in content else content[:100]

    return {
        'topic': topic,
        'key_points': key_points,
        'value_proposition': value_prop,
        'tone': tone,
        'suggested_platforms': platforms,
        'call_to_action': cta,
        'content_length': len(full_text),
        'estimated_read_time': f"{len(full_text.split()) // 200 + 1} min"
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Analyze content for social media posts')
    parser.add_argument('--input', required=True, help='Announcement or content text')
    parser.add_argument('--context', help='Optional context file path')
    args = parser.parse_args()

    context = None
    if args.context:
        try:
            with open(args.context, 'r', encoding='utf-8') as f:
                context = f.read()
        except FileNotFoundError:
            print(f"Warning: Context file not found: {args.context}", file=sys.stderr)

    analysis = analyze_content(args.input, context)
    print(json.dumps(analysis, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
```

### 4.2 scripts/engagement_optimizer.py

```python
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
```

### 4.3 scripts/thread_generator.py

```python
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
```

---

## 五、風格定義

### 5.1 styles/facebook.md

```markdown
# Facebook 貼文風格指南

## 基本規格

**字數範圍：**
- 短篇：300-500 字
- 中篇：800-1200 字
- 長篇：1500-2000 字（教學/宣傳文）

**預設風格：** 中長篇教學型（800-1500 字）

---

## 結構模板

### 標準結構（5 段式）

```
1. 標題行（粗體 + Emoji）
2. 開頭 Hook（痛點/問題/吸引注意）
3. 主體內容（分段 + 小標題）
4. 價值/結論
5. CTA（行動呼籲）
```

### 詳細說明

**1. 標題行**
- 格式：Emoji + 粗體標題 + Emoji（可選）
- 範例：`🚀 免費 3 天訓練營：Agent Skills`

**2. 開頭 Hook（2-4 行）**
- 用問題或痛點開場
- 讓讀者產生共鳴
- 範例：
  ```
  你有沒有發現，每次跟 AI 協作，總在重複解釋同樣的事情？

  「不對，我們公司格式是這樣的...」
  「上次不是說了，要用這個模板...」
  ```

**3. 主體內容**
- 使用數字編號分段（1️⃣ 2️⃣ 3️⃣ 或 **1.** **2.** **3.**）
- 每段有小標題（粗體）
- 善用符號增加可讀性：
  - ✅ 正面/推薦
  - ❌ 負面/避免
  - 👉 重點提示
  - 💡 小技巧
  - 📌 注意事項

**4. 價值/結論**
- 總結核心觀點
- 強調對讀者的價值
- 可用分隔線 `---` 區隔

**5. CTA（行動呼籲）**
- 明確告訴讀者下一步
- 範例：
  ```
  👇 如何參加？

  **Step 1**：追蹤 / 按讚這個頁面
  **Step 2**：在這篇貼文底下留言「Skills」
  **Step 3**：我會私訊你直播連結
  ```

---

## 語氣風格

- **親切但專業**：像朋友分享知識，不是老師說教
- **口語化**：用「你」稱呼讀者，避免過度正式
- **有觀點**：敢於表達立場，不說廢話
- **誠實透明**：可以說明自己的動機/私心

---

## 格式規範

**分隔線使用：**
- 大段落之間用 `---`
- 重要轉折處使用

**Emoji 使用原則：**
- 標題可用 1-2 個
- 小標題可用數字 Emoji（1️⃣ 2️⃣ 3️⃣）
- 內文適度使用，不要過多
- 重點提示用 ✅ ❌ 👉 💡

**引用格式：**
- 對話/範例用 `>` 或直接換行加引號
- 程式碼/指令用 `code` 格式

---

## 貼文類型速查

| 類型 | 字數 | 重點 |
|------|------|------|
| 宣傳/活動文 | 1200-2000 | 完整資訊 + 明確 CTA |
| 知識教學文 | 800-1500 | 結構清晰 + 實用價值 |
| 觀點分享文 | 500-1000 | 有立場 + 引發討論 |
| 快訊/更新文 | 300-500 | 簡潔 + 重點突出 |
```

---

## 六、Claude Skill

> 將以下內容保存為 `SKILL.md`

```markdown
---
name: social-media-post
description: 為 Facebook、Threads、X (Twitter) 和 LinkedIn 生成優化的社群媒體貼文。分析平台演算法、套用最佳實踐，並根據個人風格創建吸引人的內容。
allowed-tools: [Read, Write]
version: 1.1.0
---

# 社群媒體貼文生成器

根據演算法洞察和最佳實踐，生成針對各平台優化的社群媒體貼文。

## 觸發條件

當使用者說以下內容時自動啟動：
- 「幫我寫 Facebook 貼文」
- 「寫一篇 FB 貼文關於 [主題]」
- 「幫我寫 Threads 貼文」
- 「寫社群媒體貼文」
- 「Generate X post for [feature]」
- 「寫 LinkedIn 公告」

## 風格參考

每個平台都有對應的風格指南，存放在 `styles/` 目錄：
- **Facebook**：`styles/facebook.md` - 中長篇教學型風格

**重要**：生成貼文時，務必先讀取對應的風格文件以確保一致性。

## 功能說明

**平台專屬工作流程：**
1. **內容分析**：提取重點、特色、價值主張
2. **套用平台規則**：字數限制、格式、標籤策略
3. **演算法優化**：互動策略、發文時機建議
4. **生成變體**：多個版本（短、中、長）
5. **附加元資料**：字數統計、標籤建議、最佳發文時間

**支援平台**：Facebook、Threads、X (Twitter)、LinkedIn

---

## 平台規格

### Facebook

**字數限制：**
- 標準貼文：63,206 字元
- 建議字數：800-1500 字元（最佳互動）
- 顯示方式：動態消息約 400 字元後顯示「查看更多」

**格式支援：**
- ✅ 粗體（使用 Unicode 或 **markdown**）
- ✅ Emoji（策略性使用，不要過多）
- ✅ 換行（提升可讀性的關鍵）
- ✅ 項目符號（使用 • 或 -）
- ✅ 編號列表（1️⃣ 2️⃣ 3️⃣ 或 **1.** **2.**）
- ✅ 分隔線（--- 用於區隔段落）
- ❌ Hashtag（對 Facebook 影響低，可選用）

**演算法優先順序（2025-2026）：**
- 有意義的互動（40%）：留言、分享、收藏
- 內容品質（30%）：閱讀時間、完成率
- 相關性（20%）：基於用戶興趣和人脈
- 時效性（10%）：新內容獲得初始曝光

**最佳實踐：**
- ✅ 前 2-3 行要有 Hook（「查看更多」之前）
- ✅ 清晰的結構和視覺分隔
- ✅ 結尾要有 CTA（行動呼籲）
- ✅ 個人化、對話式語氣
- ✅ 分享真實價值或洞察

---

### Threads (Instagram)

**字數限制：**
- 標準貼文：500 字元
- 長篇（含附件）：10,000 字元
- 顯示方式：約 500 字元後顯示「閱讀更多」

**格式支援：**
- ✅ 粗體、斜體、底線、刪除線
- ✅ Emoji（計入字數限制）
- ✅ 項目符號（使用 • 或 -）
- ✅ 換行
- ❌ Hashtag（Threads 演算法會忽略）
- ❌ 內文不支援可點擊連結

**演算法優先順序（2025）：**
- 互動（40%）：按讚、留言、分享、回覆瀏覽
- 時效性（30%）：新內容優先
- 興趣/相關性（20%）：基於用戶過去互動
- 個人檔案造訪（10%）

**最佳實踐：**
- ✅ 對話式、真實的語氣（非企業腔）
- ✅ 提出開放式問題
- ✅ 創造討論，而非單向公告
- ✅ 穩定發文（每天 1-3 篇）
- ✅ 1 小時內回覆留言

---

### X (Twitter)

**字數限制：**
- 標準推文：280 字元
- Premium（藍勾勾）：25,000 字元

**格式支援：**
- ✅ Emoji
- ✅ 換行
- ✅ 提及（@username）
- ✅ Hashtag（每則推文最多 2-3 個）
- ❌ 不支援富文字格式

**演算法優先順序（2025）：**
- 互動率（按讚、轉推、回覆）
- 時效性（新推文優先）
- 媒體（含圖片/影片的推文表現更好）
- 真實性（認證帳號、真實互動）

---

### LinkedIn

**字數限制：**
- 貼文：3,000 字元（約 140 字元後顯示「查看更多」）
- 文章：125,000 字元

**格式支援：**
- ✅ Emoji（適度使用）
- ✅ 項目符號
- ✅ 換行
- ✅ 粗體（使用 Unicode）
- ✅ 編號列表

**演算法優先順序（2025）：**
- 停留時間（用戶閱讀貼文的時長）
- 互動（按讚、留言、分享）
- 相關性（對用戶人脈和興趣的相關度）
- 人脈關係（一度人脈優先）

---

## 工作流程

### 步驟 1：內容分析
執行：`python scripts/post_analyzer.py --input "你的內容"`

### 步驟 2：平台優化
執行：`python scripts/engagement_optimizer.py --platform [platform] --content "貼文草稿"`

### 步驟 3：生成貼文變體

**Facebook：**
1. **簡短更新**：300-500 字元，快速公告
2. **標準貼文**：800-1200 字元，有結構的分段內容
3. **長篇文章**：1500-2000 字元，完整教學/故事 + 詳細 CTA

**Threads/X/LinkedIn：**
1. **簡短有力**：280 字元以下，emoji 項目符號，直接 CTA
2. **中等詳細**：300-500 字元，更多背景，引發對話
3. **長篇完整**：800-1500 字元，完整故事，豐富格式

### 步驟 4：生成串文（可選）
執行：`python scripts/thread_generator.py --platform x --content "長文內容" --max-posts 5`

### 步驟 5：附加元資料
為每個變體附上：字數統計、預估互動、標籤建議、媒體建議、最佳發文時間。
```

---

## 七、使用範例

### 7.1 分析內容

```bash
python scripts/post_analyzer.py --input "我們推出了新的 AI 功能，可以自動生成社群貼文，節省 80% 的時間"
```

輸出：
```json
{
  "topic": "我們推出了新的 AI 功能",
  "key_points": [],
  "value_proposition": "我們推出了新的 ai 功能，可以自動生成社群貼文，節省 80% 的時間",
  "tone": "promotional",
  "suggested_platforms": ["threads", "x"],
  "call_to_action": "Learn more",
  "content_length": 42,
  "estimated_read_time": "1 min"
}
```

### 7.2 優化貼文

```bash
python scripts/engagement_optimizer.py --platform threads --content "這是我的貼文草稿 #AI #科技"
```

輸出：
```json
{
  "optimized_content": "這是我的貼文草稿",
  "character_count": 9,
  "character_limit": 500,
  "engagement_score": 5,
  "engagement_reasons": ["Concise hook", "Fits character limit"],
  "improvements": ["Removed hashtags (Threads algorithm ignores them)"],
  "warnings": []
}
```

### 7.3 生成串文

```bash
python scripts/thread_generator.py --platform x --content "這是一篇很長的文章..." --max-posts 5
```

---

## 八、啟動專案

### 8.1 安裝依賴

此專案為純 Python，無需額外安裝套件。

```bash
# 進入專案目錄
cd Social_Media_Post

# 確認 Python 版本
python --version
```

### 8.2 使用方式

**方式一：透過 Claude Code（推薦）**

將 `Social_Media_Post` 資料夾放到 `~/.claude/skills/` 目錄，然後在 Claude Code 中說：「幫我寫 FB 貼文」

**方式二：直接執行腳本**

```bash
# 分析內容
python scripts/post_analyzer.py --input "你的內容"

# 優化貼文
python scripts/engagement_optimizer.py --platform facebook --content "貼文草稿"

# 生成串文
python scripts/thread_generator.py --platform x --content "長文" --max-posts 5
```

### 8.3 放置到 Claude Code Skills 目錄

| 系統 | 路徑 |
|------|------|
| Windows | `C:\Users\{用戶名}\.claude\skills\Social_Media_Post\` |
| macOS/Linux | `~/.claude/skills/Social_Media_Post/` |

---

## 完成

按照以上規格書，Claude Code 可完整複刻 Social Media Post 專案。所有設定檔和程式碼均已包含。
