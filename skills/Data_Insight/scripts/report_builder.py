#!/usr/bin/env python3
"""
報告構建器 - 將分析結論和圖表整合為前端可用的 JSON 格式
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

class ReportBuilder:
    """報告構建器"""

    def __init__(self, output_dir: str = 'outputs/reports'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_report(
        self,
        title: str,
        overall_summary: str,
        conclusions: list,
        source_files: list,
        analysis_focus: Optional[dict] = None
    ) -> dict:
        """構建完整的報告數據結構"""

        report = {
            'meta': {
                'title': title,
                'generated_at': datetime.now().isoformat(),
                'version': '1.0'
            },
            'summary': {
                'overall': overall_summary,
                'total_conclusions': len(conclusions),
                'high_importance_count': len([c for c in conclusions if c.get('importance') == 'high']),
                'source_files': source_files
            },
            'analysis_focus': analysis_focus or {},
            'conclusions': conclusions
        }

        return report

    def save_report(self, report: dict, filename: str = 'report.json') -> str:
        """保存報告到 JSON 文件"""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return str(output_path)

    def create_sample_report(self) -> dict:
        """創建示例報告（用於測試前端）"""

        conclusions = [
            {
                'id': 1,
                'title': 'Q3 銷售額環比下降 23%',
                'description': '第三季度銷售額為 850 萬元，相比 Q2 的 1100 萬元下降了 23%。主要受華東區域拖累，該區域下降 35%，需要重點關注。',
                'data_support': 'Q2: 1100萬 → Q3: 850萬，降幅 250萬',
                'source_files': ['銷售數據.xlsx'],
                'importance': 'high',
                'chart_type': 'line',
                'chart_data': {
                    'x_labels': ['Q1', 'Q2', 'Q3', 'Q4'],
                    'series': {
                        '實際': [980, 1100, 850, None],
                        '目標': [1000, 1000, 1000, 1000]
                    },
                    'x_title': '季度',
                    'y_title': '銷售額（萬元）'
                }
            },
            {
                'id': 2,
                'title': '用戶滿意度與復購率強相關',
                'description': '通過交叉分析發現，用戶滿意度每提升 10 分，復購率平均提升 8%。滿意度低於 60 分的用戶復購率僅 12%，而高於 80 分的用戶復購率達 45%。',
                'data_support': '相關係數 r=0.82，P<0.01',
                'source_files': ['用戶調研報告.pdf', '銷售數據.xlsx'],
                'importance': 'high',
                'chart_type': 'scatter',
                'chart_data': {
                    'x': [45, 52, 58, 65, 72, 78, 85, 90],
                    'y': [8, 12, 18, 25, 32, 38, 45, 52],
                    'labels': ['用戶群1', '用戶群2', '用戶群3', '用戶群4', '用戶群5', '用戶群6', '用戶群7', '用戶群8'],
                    'x_title': '滿意度評分',
                    'y_title': '復購率（%）'
                }
            },
            {
                'id': 3,
                'title': '華東區域佔總銷售的 42%',
                'description': '從區域分佈來看，華東區域貢獻了最大的銷售份額（42%），其次是華南（28%）和華北（18%）。西部和其他區域佔比較小，合計僅 12%。',
                'data_support': '華東 42%，華南 28%，華北 18%，西部 8%，其他 4%',
                'source_files': ['銷售數據.xlsx'],
                'importance': 'medium',
                'chart_type': 'pie',
                'chart_data': {
                    'labels': ['華東', '華南', '華北', '西部', '其他'],
                    'values': [42, 28, 18, 8, 4]
                }
            },
            {
                'id': 4,
                'title': '線上渠道增速超過線下',
                'description': '線上渠道同比增長 35%，而線下渠道僅增長 8%。線上佔比從去年的 25% 提升到今年的 38%，渠道結構正在發生顯著變化。',
                'data_support': '線上同比 +35%，線下同比 +8%',
                'source_files': ['銷售數據.xlsx'],
                'importance': 'medium',
                'chart_type': 'bar',
                'chart_data': {
                    'x_labels': ['線上渠道', '線下渠道'],
                    'series': {
                        '去年': [250, 750],
                        '今年': [338, 810]
                    },
                    'x_title': '渠道',
                    'y_title': '銷售額（萬元）'
                }
            },
            {
                'id': 5,
                'title': '新客獲取成本上升 18%',
                'description': '今年新客獲取成本（CAC）為 180 元/人，相比去年的 152 元上升了 18%。主要原因為競爭加劇和廣告成本上漲。',
                'data_support': 'CAC: 152元 → 180元，漲幅 18%',
                'source_files': ['銷售數據.xlsx'],
                'importance': 'low',
                'chart_type': 'bar',
                'chart_data': {
                    'x_labels': ['2023年', '2024年'],
                    'series': {
                        'CAC（元）': [152, 180]
                    },
                    'x_title': '年份',
                    'y_title': '獲客成本（元）'
                }
            }
        ]

        report = self.build_report(
            title='銷售數據分析報告',
            overall_summary='基於銷售數據和用戶調研報告的綜合分析，發現 Q3 銷售下滑主要受華東區域影響，用戶滿意度與復購率存在強相關性。建議：1) 重點改善華東區域服務質量；2) 加強滿意度管理提升復購；3) 加速線上渠道建設。',
            conclusions=conclusions,
            source_files=['銷售數據.xlsx', '用戶調研報告.pdf'],
            analysis_focus={
                'core_question': '銷售下滑的原因',
                'focus_metrics': 'Q3 數據、復購率',
                'usage_scenario': '內部匯報'
            }
        )

        return report

def main():
    """生成示例報告"""
    builder = ReportBuilder()
    report = builder.create_sample_report()
    output_path = builder.save_report(report)
    print(f"示例報告已生成: {output_path}")

if __name__ == '__main__':
    main()
