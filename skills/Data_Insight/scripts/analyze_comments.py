import json
import sys
import os
from datetime import datetime
from collections import defaultdict, Counter
import pandas as pd

# Ensure scripts directory is in path so we can import chart_generator
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from chart_generator import ChartGenerator
except ImportError:
    pass # Might be running in extensive environment

def get_analysis_data(data_json: dict, months_back: int = 1):
    """
    Process the JSON data and return aggregated metrics and charts logic.
    Accepts raw JSON dict, returns structured dict for frontend.
    """
    rows = data_json['files'][0]['sheets']['工作表1']['data']
    valid_rows = []
    
    # Filter by date (approximate logic for "last month" or custom range)
    # Defaulting to Dec 1, 2025 based on current context if months_back is small
    # For a generic app, we might want to let the user filter, but here we keep the business logic
    start_date = datetime(2025, 12, 1) 
    
    for row in rows:
        date_str = row.get('日期')
        if not date_str:
            continue
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            if dt >= start_date:
                valid_rows.append(row)
        except ValueError:
            continue

    # Aggregation
    sentiment_counts = Counter(row.get('AI_情緒', 'Unknown') for row in valid_rows)
    dept_counts = Counter(row.get('AI_責任部門', 'Unassigned') for row in valid_rows)
    
    # 4. Time Series Volume (Daily)
    daily_volume = defaultdict(int)
    for row in valid_rows:
        date_str = row.get('日期')
        if not date_str: continue
        try:
             # Just date part
             d = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
             daily_volume[d] += 1
        except: pass
    
    sorted_dates = sorted(daily_volume.keys())
    time_series_data = {
        'dates': [d.strftime('%Y-%m-%d') for d in sorted_dates],
        'volumes': [daily_volume[d] for d in sorted_dates]
    }

    # 5. Radar Chart Data (Category Performance)
    # We will score categories based on Volume + Sentiment
    # Score = Volume * Sentiment_Weight (Pos=1, Neg=-1)? 
    # Or just dimension score 0-100?
    # Let's simple use: Volume fraction * 100 on 5-6 dimensions
    # Dimensions: '口味/口感', '價格/CP值', '通路/便利性', '包裝/規格', '品牌/行銷'
    target_dimensions = ['口味/口感', '價格/CP值', '通路/便利性', '包裝/規格', '品牌/行銷']
    dimension_scores = {dim: 0 for dim in target_dimensions}
    
    for row in valid_rows:
        cats = row.get('AI_議題', '')
        # Simple keyword matching to map actual categories to these dimensions
        # Assuming AI_議題 might contain these or similar
        for dim in target_dimensions:
            # Check if any part of dimension is in category string
            parts = dim.split('/')
            if any(p in cats for p in parts):
                dimension_scores[dim] += 1
    
    # Normalize to 0-100 relative to max? Or just raw count?
    # Context: Radar usually 0-5 or 0-100.
    # Let's normalize to max 100
    max_score = max(dimension_scores.values()) if dimension_scores.values() else 1
    radar_data = {
        'dimensions': list(dimension_scores.keys()),
        'scores': [int((v / max_score) * 100) if max_score > 0 else 0 for v in dimension_scores.values()]
    }

    # Detailed Department Issues (Aggregated by Issue Key)
    # Structure:
    # {
    #   'Dept': {
    #      'IssueName': {
    #           'mentions': 0,
    #           'sentiment_score': 0, # Pos=+1, Neg=-1
    #           'factors': set(),
    #           'actions': set(),
    #           'examples': [], # List of representative quotes
    #           'status': 'Warning' # Critical, Warning, Opportunity
    #       }
    #   }
    # }
    
    dept_structured = defaultdict(lambda: defaultdict(lambda: {
        'mentions': 0,
        'sentiment_score': 0,
        'factors': set(),
        'actions': set(),
        'examples': []
    }))

    for row in valid_rows:
        dept = row.get('AI_責任部門') or "General"
        issue = row.get('AI_關鍵議題')
        content = row.get('內容') # Raw user comment
        
        if not issue: continue
        
        # Normalize issue key? For now use raw string, assuming some consistency
        entry = dept_structured[dept][issue]
        entry['mentions'] += 1
        
        # Capture Evidence (Quotes) - Keep reasonably short ones, max 3 per issue
        if content and len(entry['examples']) < 3:
            # Clean content briefly?
            clean_content = content.replace('\n', ' ').strip()
            if 10 < len(clean_content) < 100: # Filter for readable snippets
                 entry['examples'].append(clean_content)
        
        # Sentiment
        sent = row.get('AI_情緒')
        if sent in ['Positive', 'Strongly Positive']:
            entry['sentiment_score'] += 1
            if row.get('AI_正面因素'): entry['factors'].add(row.get('AI_正面因素'))
        elif sent in ['Negative', 'Strongly Negative']:
            entry['sentiment_score'] -= 1
            if row.get('AI_負面因素'): entry['factors'].add(row.get('AI_負面因素'))
        
        # Actions
        if row.get('AI_可控因素'):
            entry['actions'].add(row.get('AI_可控因素'))

    # Finalize Structure for Frontend
    # Convert sets to lists, determine status
    final_dept_issues = {}
    
    top_opportunities = []
    top_risks = []
    
    for dept, issues_map in dept_structured.items():
        issue_list = []
        for issue_name, data in issues_map.items():
            # Determine Status
            # High Neg Score -> Critical
            # Moderate Neg Score -> Warning
            # Positive Score -> Opportunity
            
            score = data['sentiment_score']
            count = data['mentions']
            
            if score > 0:
                status = 'Opportunity'
                severity = 1 # for sorting opportunities
            else:
                ratio = abs(score) / count if count > 0 else 0
                if ratio > 0.6 and count >= 2: # Strongly negative consistently
                    status = 'Critical'
                    severity = 3
                else:
                    status = 'Warning'
                    severity = 2
            
            card_data = {
                'issue': issue_name,
                'status': status,
                'mentions': count,
                'factors': list(data['factors']),
                'actions': list(data['actions']),
                'examples': data['examples'],
                'score': score
            }
            issue_list.append(card_data)
            
            # Add to global top lists
            if status == 'Opportunity':
                top_opportunities.append((card_data, dept))
            elif status in ['Critical', 'Warning']:
                top_risks.append((card_data, dept))
                
        # Sort issues within dept by mentions or severity
        issue_list.sort(key=lambda x: x['mentions'], reverse=True)
        final_dept_issues[dept] = issue_list

    # Sort Global Top Lists
    top_opportunities.sort(key=lambda x: x[0]['mentions'], reverse=True)
    top_risks.sort(key=lambda x: x[0]['score'], reverse=False) # Most negative first

    # Categories
    category_counts = Counter()
    for row in valid_rows:
        cats = row.get('AI_議題')
        if cats:
            for cat in cats.split(','):
                category_counts[cat.strip()] += 1
                
    return {
        'total_rows': len(valid_rows),
        'sentiment_counts': dict(sentiment_counts),
        'dept_counts': dict(dept_counts),
        'dept_issues': final_dept_issues, # New detailed structure
        'top_risks': [ {'dept': d, **c} for c, d in top_risks[:3] ],
        'top_opportunities': [ {'dept': d, **c} for c, d in top_opportunities[:3] ],
        'category_counts': dict(category_counts),
        'time_series': time_series_data,
        'radar_data': radar_data,
        'raw_rows': valid_rows
    }

def analyze_and_chart():
    # Legacy wrapper for command line usage
    try:
        with open('outputs/reports/processed_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: content not found.")
        return

    results = get_analysis_data(data)
    print(f"Total rows: {results['total_rows']}")
    # ... (Rest of legacy print logic could go here if needed, but we focus on the app now)

if __name__ == "__main__":
    analyze_and_chart()
