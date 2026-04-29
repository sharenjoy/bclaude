#!/usr/bin/env python3
"""
圖表生成器 - 根據數據和結論生成可視化圖表
支持：折線圖、柱狀圖、餅圖、散點圖、面積圖
"""

import json
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# 設置中文字體 (嘗試使用常見的繁體中文字體)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 圖表配色方案
CHART_COLORS = [
    '#2563EB',  # 主藍色
    '#10B981',  # 綠色
    '#F59E0B',  # 橙色
    '#8B5CF6',  # 紫色
    '#EC4899',  # 粉色
    '#06B6D4',  # 青色
    '#EF4444',  # 紅色
]

class ChartGenerator:
    """圖表生成器"""

    def __init__(self, output_dir: str = 'outputs/charts'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_line_chart(self, data: dict, title: str, filename: str) -> str:
        """生成折線圖"""
        fig = go.Figure()

        for i, (name, values) in enumerate(data.get('series', {}).items()):
            fig.add_trace(go.Scatter(
                x=data.get('x_labels', list(range(len(values)))),
                y=values,
                mode='lines+markers',
                name=name,
                line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
                marker=dict(size=6)
            ))

        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            xaxis_title=data.get('x_title', ''),
            yaxis_title=data.get('y_title', ''),
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=60, r=40, t=80, b=60)
        )

        output_path = self.output_dir / f"{filename}.html"
        fig.write_html(str(output_path))

        # 同時保存為圖片
        # 注意：需要安裝 kaleido 才能保存圖片
        try:
            img_path = self.output_dir / f"{filename}.png"
            fig.write_image(str(img_path), width=800, height=500)
        except Exception as e:
            print(f"無法保存圖片 (可能是缺少 kaleido 庫): {e}")

        return str(output_path)

    def generate_bar_chart(self, data: dict, title: str, filename: str) -> str:
        """生成柱狀圖"""
        fig = go.Figure()

        x_labels = data.get('x_labels', [])

        for i, (name, values) in enumerate(data.get('series', {}).items()):
            fig.add_trace(go.Bar(
                x=x_labels,
                y=values,
                name=name,
                marker_color=CHART_COLORS[i % len(CHART_COLORS)]
            ))

        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            xaxis_title=data.get('x_title', ''),
            yaxis_title=data.get('y_title', ''),
            template='plotly_white',
            barmode='group',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=60, r=40, t=80, b=60)
        )

        output_path = self.output_dir / f"{filename}.html"
        fig.write_html(str(output_path))

        try:
            img_path = self.output_dir / f"{filename}.png"
            fig.write_image(str(img_path), width=800, height=500)
        except Exception:
            pass

        return str(output_path)

    def generate_pie_chart(self, data: dict, title: str, filename: str) -> str:
        """生成餅圖"""
        fig = go.Figure(data=[go.Pie(
            labels=data.get('labels', []),
            values=data.get('values', []),
            hole=0.4,  # 環形圖
            marker=dict(colors=CHART_COLORS[:len(data.get('labels', []))]),
            textinfo='label+percent',
            textposition='outside'
        )])

        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template='plotly_white',
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5),
            margin=dict(l=40, r=40, t=80, b=80)
        )

        output_path = self.output_dir / f"{filename}.html"
        fig.write_html(str(output_path))

        try:
            img_path = self.output_dir / f"{filename}.png"
            fig.write_image(str(img_path), width=600, height=500)
        except Exception:
            pass

        return str(output_path)

    def generate_scatter_chart(self, data: dict, title: str, filename: str) -> str:
        """生成散點圖"""
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.get('x', []),
            y=data.get('y', []),
            mode='markers',
            marker=dict(
                size=10,
                color=CHART_COLORS[0],
                opacity=0.7
            ),
            text=data.get('labels', None),
            hovertemplate='%{text}<br>X: %{x}<br>Y: %{y}<extra></extra>'
        ))

        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            xaxis_title=data.get('x_title', 'X'),
            yaxis_title=data.get('y_title', 'Y'),
            template='plotly_white',
            margin=dict(l=60, r=40, t=80, b=60)
        )

        output_path = self.output_dir / f"{filename}.html"
        fig.write_html(str(output_path))

        try:
            img_path = self.output_dir / f"{filename}.png"
            fig.write_image(str(img_path), width=800, height=500)
        except Exception:
            pass

        return str(output_path)

    def generate_area_chart(self, data: dict, title: str, filename: str) -> str:
        """生成面積圖"""
        fig = go.Figure()

        for i, (name, values) in enumerate(data.get('series', {}).items()):
            fig.add_trace(go.Scatter(
                x=data.get('x_labels', list(range(len(values)))),
                y=values,
                mode='lines',
                name=name,
                fill='tonexty' if i > 0 else 'tozeroy',
                line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=1),
            ))

        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            xaxis_title=data.get('x_title', ''),
            yaxis_title=data.get('y_title', ''),
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=60, r=40, t=80, b=60)
        )

        output_path = self.output_dir / f"{filename}.html"
        fig.write_html(str(output_path))

        try:
            img_path = self.output_dir / f"{filename}.png"
            fig.write_image(str(img_path), width=800, height=500)
        except Exception:
            pass

        return str(output_path)

    def generate_chart(self, chart_type: str, data: dict, title: str, filename: str) -> str:
        """根據類型生成圖表"""
        generators = {
            'line': self.generate_line_chart,
            'bar': self.generate_bar_chart,
            'pie': self.generate_pie_chart,
            'scatter': self.generate_scatter_chart,
            'area': self.generate_area_chart
        }

        generator = generators.get(chart_type)
        if generator:
            return generator(data, title, filename)
        else:
            raise ValueError(f"不支持的圖表類型: {chart_type}")

    def generate_from_conclusions(self, conclusions: list) -> list:
        """根據結論列表生成所有圖表"""
        chart_paths = []

        for conclusion in conclusions:
            if conclusion.get('chart_type') and conclusion.get('chart_type') != 'none':
                chart_data = conclusion.get('chart_data', {})
                if chart_data:
                    path = self.generate_chart(
                        chart_type=conclusion['chart_type'],
                        data=chart_data,
                        title=conclusion.get('title', ''),
                        filename=f"chart_{conclusion.get('id', 'unknown')}"
                    )
                    chart_paths.append({
                        'id': conclusion.get('id'),
                        'path': path,
                        'type': conclusion['chart_type']
                    })

        return chart_paths

def main():
    """示例：生成測試圖表"""
    generator = ChartGenerator()

    # 測試折線圖
    line_data = {
        'x_labels': ['1月', '2月', '3月', '4月', '5月', '6月'],
        'series': {
            '銷售額': [120, 150, 180, 220, 200, 250],
            '目標': [150, 150, 180, 200, 200, 220]
        },
        'x_title': '月份',
        'y_title': '金額（萬元）'
    }
    generator.generate_line_chart(line_data, '月度銷售趨勢', 'test_line')

    # 測試柱狀圖
    bar_data = {
        'x_labels': ['產品A', '產品B', '產品C', '產品D'],
        'series': {
            '2023年': [100, 80, 120, 90],
            '2024年': [120, 95, 110, 100]
        },
        'x_title': '產品',
        'y_title': '銷量'
    }
    generator.generate_bar_chart(bar_data, '產品銷量對比', 'test_bar')

    # 測試餅圖
    pie_data = {
        'labels': ['華東', '華南', '華北', '西部', '其他'],
        'values': [35, 25, 20, 15, 5]
    }
    generator.generate_pie_chart(pie_data, '區域銷售佔比', 'test_pie')

    print("測試圖表生成完成！")

if __name__ == '__main__':
    main()
