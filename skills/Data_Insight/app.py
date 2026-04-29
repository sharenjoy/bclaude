import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from scripts.file_processor import FileProcessor
from scripts.analyze_comments import get_analysis_data
from scripts.ai_insight import generate_strategic_insight

# Page Config
st.set_page_config(
    page_title="雅方食品 (YA-FANG) 策略決策看板",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for Strategy Board Style
st.markdown("""
<style>
    /* Global Font */
    body {
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
        background-color: #F8FAFC;
    }
    
    .main-title {
        background-color: #E2E8F0;
        padding: 1.5rem;
        border-bottom: 3px solid #0F2C59;
        color: #0F2C59;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 0.5rem;
    }
    
    /* Executive Cards */
    .exec-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        height: 100%;
    }
    
    .risk-item {
        background: #FEF2F2;
        border-left: 4px solid #EF4444;
        padding: 10px;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    .opp-item {
        background: #F0FDF4;
        border-left: 4px solid #10B981;
        padding: 10px;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    
    /* Department Cards */
    .dept-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        padding: 1.5rem;
        border-top: 4px solid #CBD5E1;
    }
    
    /* Issue Card Internal */
    .issue-box {
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #fff;
    }
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        color: white;
        font-size: 0.75rem;
        font-weight: bold;
        float: right;
    }
    .status-Critical { background-color: #EF4444; }
    .status-Warning { background-color: #F59E0B; }
    .status-Opportunity { background-color: #10B981; }
    
    .issue-title {
        font-weight: bold;
        color: #334155;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .fact-section {
        background-color: #F1F5F9;
        padding: 8px;
        border-radius: 4px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #475569;
    }
    
    .action-section {
        border: 1px dashed #94A3B8;
        padding: 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        background-color: #FFFBEB; /* Light yellow */
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar - Simplified for Static Report Mode
    with st.sidebar:
        st.header("📊 雅方食品 策略決策報告")
        st.caption("由 Antigravity Agent 自動分析生成")
        st.divider()
        st.markdown("**分析時間:** 2026-01-19")
        st.markdown("**資料來源:** 雅方食品輿情 (3).xlsx")

    # Auto-load file from uploads/ (Static Report Mode)
    auto_load_path = os.path.join("uploads", "雅方食品輿情 (3).xlsx")
    brand_name = "雅方"
    api_key_input = None  # Not needed in static mode
    
    if not os.path.exists(auto_load_path):
         st.markdown(f"""
         <div style="text-align: center; padding: 50px; color: #888;">
            <h1>策略決策看板</h1>
            <h3>找不到分析檔案</h3>
            <p>請確認 uploads/雅方食品輿情 (3).xlsx 存在</p>
         </div>
         """, unsafe_allow_html=True)
         return
    
    uploaded_file = auto_load_path

    # Process Data
    processor = FileProcessor()
    # Handle both Streamlit UploadedFile and string path
    if isinstance(uploaded_file, str):
         processed_data = processor.process_file(uploaded_file)
         file_name = os.path.basename(uploaded_file)
    else:
         processed_data = processor.process_stream(uploaded_file, uploaded_file.name)
         file_name = uploaded_file.name
         
    if 'error' in processed_data:
        st.error(f"Error: {processed_data['error']}")
        return
        
    full_data_structure = {'files': [{'sheets': processed_data.get('sheets', {}), 'name': file_name}]}
    results = get_analysis_data(full_data_structure)
    
    # Load Reference Content once
    param_ref_content = ""
    try:
        with open(r"c:\Users\oilme\.gemini\antigravity\Data Analytics\references\hypothesis-driven-analysis.md", "r", encoding="utf-8") as f:
            param_ref_content = f.read()
    except Exception as e:
        print(f"Warning: Could not read reference file: {e}")

    # Main Title (Dynamic)
    st.markdown(f"""
    <div class="main-title">
        <h1>{brand_name} 策略決策看板</h1>
        <small>Strategic Decision Dashboard | Status: FINAL</small>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. Executive Summary (CEO View)
    st.markdown('<div class="section-header">1. Executive Summary (CEO View)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        st.markdown("""
        <div class="exec-card">
            <h4>本月戰略總結</h4>
            <p>本月品牌輿情總量達 <b>{}</b> 則。主要正面聲量集中於 <b>{}</b>，顯示品牌優勢持續穩固。
            然而，需特別注意 <b>{}</b> 相關的負面討論，需立即介入處理。</p>
            <hr>
            <p><small>建議瀏覽下方各部門詳細行動計畫，優先處理 Critical 等級議題。</small></p>
        </div>
        """.format(
            results['total_rows'],
            "、".join([o['issue'] for o in results['top_opportunities'][:2]]) or "無",
            "、".join([r['issue'] for r in results['top_risks'][:2]]) or "無"
        ), unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="exec-card"><h4>🔥 Top 3 Risks</h4>', unsafe_allow_html=True)
        if results['top_risks']:
            for item in results['top_risks'][:3]:
                st.markdown(f"""
                <div class="risk-item">
                    <b>[{item['dept']}]</b> {item['issue']}<br>
                    <small>Severity: High</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No major risks identified.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c3:
        st.markdown('<div class="exec-card"><h4>🚀 Top 3 Opportunities</h4>', unsafe_allow_html=True)
        if results['top_opportunities']:
            for item in results['top_opportunities'][:3]:
                st.markdown(f"""
                <div class="opp-item">
                    <b>[{item['dept']}]</b> {item['issue']}<br>
                    <small>Potential: High</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No major opportunities identified.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. Market Intelligence (Visual Analysis)
    st.markdown('<div class="section-header">2. Market Intelligence (Visual Analysis)</div>', unsafe_allow_html=True)
    
    col_trend, col_radar, col_pie = st.columns([2, 1, 1])
    
    with col_trend:
         st.markdown("##### 📈 聲量趨勢分析 (Volume Trend)")
         time_data = results['time_series']
         if time_data['dates']:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=time_data['dates'], y=time_data['volumes'],
                                mode='lines+markers',
                                name='以日',
                                line=dict(color='#2563EB', width=3, shape='spline')))
            fig_line.update_layout(
                template="plotly_white",
                margin=dict(l=20, r=20, t=10, b=20),
                height=250,
                hovermode="x unified"
            )
            st.plotly_chart(fig_line, use_container_width=True)
         else:
            st.info("無足夠時間數據")

    with col_radar:
        st.markdown("##### 🕸️ 議題競爭雷達 (Capabilities)")
        radar_d = results.get('radar_data', {})
        if radar_d.get('dimensions'):
            fig_radar = go.Figure(data=go.Scatterpolar(
              r=radar_d['scores'],
              theta=radar_d['dimensions'],
              fill='toself',
              line_color='#F4CE14'
            ))
            fig_radar.update_layout(
              template="plotly_white",
              polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
              showlegend=False,
              height=250,
              margin=dict(l=30, r=30, t=20, b=20)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("無雷達數據")

    with col_pie:
        st.markdown("##### ❤️ 品牌好感度 (Brand Health)")
        sent_counts = results['sentiment_counts']
        if sent_counts:
             fig_pie = px.pie(
                values=list(sent_counts.values()), 
                names=list(sent_counts.keys()),
                hole=0.6,
                color_discrete_map={'Positive': '#10B981', 'Negative': '#EF4444', 'Neutral': '#D1D5DB'}
            )
             fig_pie.update_layout(showlegend=False, height=250, margin=dict(l=10, r=10, t=10, b=10))
             # Add detailed legend or info inside hole? keeping simple
             st.plotly_chart(fig_pie, use_container_width=True)
        else:
             st.info("無情緒數據")


    # 3. Departmental Action Plans
    st.markdown('<div class="section-header">3. Departmental Action Plans</div>', unsafe_allow_html=True)
    
    # Load Static AI Insights (Agent Generated)
    static_insights = {}
    static_path = os.path.join("outputs", "reports", "ai_insights.json")
    if os.path.exists(static_path):
        try:
            with open(static_path, 'r', encoding='utf-8') as f:
                static_insights = json.load(f)
        except Exception as e:
            print(f"Error loading static insights: {e}")

    # Display Issues Cards
    analysis_data = results['dept_issues'] 
    
    # Custom CSS for cleaner cards
    st.markdown("""
    <style>
        .issue-card {
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.2s;
        }
        .issue-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        .issue-title {
            font-size: 1.15rem;
            font-weight: 600;
            color: #1f2937;
            margin: 0;
            flex-grow: 1;
            padding-right: 10px;
        }
        .status-badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            color: white;
            white-space: nowrap;
        }
        .fact-box {
            background-color: #f3f4f6;
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 12px;
            font-size: 0.9rem;
            color: #4b5563;
        }
        .evidence-quote {
            font-style: italic;
            color: #6b7280;
            font-size: 0.85rem;
            border-left: 3px solid #e5e7eb;
            padding-left: 10px;
            margin: 10px 0;
        }
        .ai-analysis-box {
            background-color: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 6px;
            padding: 12px;
            margin-top: 15px;
        }
        .ai-title {
            display: flex;
            align-items: center;
            font-weight: 600;
            color: #1e3a8a;
            font-size: 0.95rem;
            margin-bottom: 5px;
        }
        .action-box {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #dbeafe;
            color: #1e40af;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)

    for dept, issues in analysis_data.items():
        if not issues:
            continue
            
        st.markdown(f"### 📂 {dept}")
        
        # Grid layout for cards
        cols = st.columns(2)
        
        for idx, issue in enumerate(issues[:10]): # Limit to top 10 per dept
            with cols[idx % 2]:
                
                # Logic: 1. Try Static Insight 2. Try Dynamic AI (if Key) 3. Simulation
                ai_result = None
                
                # 1. Check Static Insight (Agent Generated)
                if dept in static_insights and issue['issue'] in static_insights[dept]:
                    ai_result = static_insights[dept][issue['issue']]
                
                # 2. If no static, check Dynamic Key
                elif api_key_input: 
                    cache_key = f"ai_res_{dept}_{issue['issue']}_{api_key_input}"
                    if cache_key not in st.session_state:
                         st.session_state[cache_key] = generate_strategic_insight(
                            brand_name, 
                            dept, 
                            issue, 
                            api_key=api_key_input, 
                            reference_context=param_ref_content
                        )
                    ai_result = st.session_state[cache_key]
                
                # 3. No Analysis Available
                else:
                    ai_result = {
                        "analysis": "⚠️ 尚未生成 AI 分析",
                        "action": "請確認相關報告檔案 (ai_insights.json) 是否包含此議題。"
                    }

                # Prepare Data
                status = issue.get('status', 'Info')
                raw_factors = issue.get('factors', [])
                cleaned_factors = [str(f) for f in raw_factors if f and str(f).lower() != 'nan']
                factors_str = ', '.join(cleaned_factors[:3]) if cleaned_factors else '無數據'
                
                evidence_str = ''
                if issue.get('examples'):
                    evidence_str = str(issue['examples'][0]) if issue['examples'][0] else ''
                
                analysis_text = ai_result.get('analysis', '分析生成中...')
                action_text = ai_result.get('action', '行動方案生成中...')

                # === Native Streamlit Card Rendering ===
                with st.container(border=True):
                    # Header with status
                    col_title, col_badge = st.columns([4, 1])
                    with col_title:
                        st.markdown(f"**{issue['issue']}**")
                    with col_badge:
                        if status == "Critical":
                            st.error(status)
                        elif status == "Warning":
                            st.warning(status)
                        elif status == "Opportunity":
                            st.success(status)
                        else:
                            st.info(status)
                    
                    # Fact Section
                    st.caption(f"📋 **現象 (Fact):** {factors_str}")
                    
                    # Evidence (if exists)
                    if evidence_str:
                        st.caption(f"💬 _{evidence_str}_")
                    
                    st.divider()
                    
                    # AI Analysis Section
                    st.markdown("🤖 **AI Analysis:**")
                    st.write(analysis_text)
                    
                    st.markdown("👉 **Action:**")
                    st.write(action_text)

    # 4. Appendix
    with st.expander("4. Appendix: Selected Voice of Customer (Raw Data)"):
        st.dataframe(pd.DataFrame(results['raw_rows']))

if __name__ == "__main__":
    main()
