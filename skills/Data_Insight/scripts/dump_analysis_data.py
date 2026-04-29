from scripts.file_processor import FileProcessor
from scripts.analyze_comments import get_analysis_data
import json
import os

try:
    file_path = 'c:/Users/oilme/.gemini/antigravity/Data Analytics/uploads/雅方食品輿情 (3).xlsx'
    print(f"Processing {file_path}...")
    
    p = FileProcessor()
    data = p.process_file(file_path)
    
    full_data = {'files': [{'sheets': data.get('sheets', {}), 'name': 'static_analysis'}]}
    results = get_analysis_data(full_data)
    
    # Save to file
    with open('debug_data.json', 'w', encoding='utf-8') as f:
        json.dump(results['dept_issues'], f, ensure_ascii=False, indent=2)
        
    print("Done. Saved to debug_data.json")

except Exception as e:
    print(f"Error: {e}")
