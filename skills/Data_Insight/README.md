# Data Insight Orchestrator

數據洞察分析 Skill - 專業級數據分析工作流程。

## 功能特色

- **完整分析流程**：6 個階段（文件識別 → 側重點確認 → 數據分析 → 圖表生成 → 頁面構建 → 交付）
- **專業方法論**：假設驅動分析、驅動因素樹、認知偏差檢驗
- **自動圖表生成**：柱狀圖、折線圖、餅圖、散點圖、面積圖
- **互動式 Dashboard**：Streamlit 報告展示

---

## 快速開始

### 1. 安裝依賴

```bash
cd {skill_path}
pip install -r requirements.txt
```

### 2. 準備數據

將數據文件放入 `uploads/` 目錄：

支援格式：
- Excel（.xlsx, .xls）
- PDF（.pdf）
- Word（.docx）
- CSV（.csv）
- TXT（.txt）

### 3. AI 智能分析（推薦）

直接告訴 AI：

```
分析 uploads/ 裡的數據，找出銷售下滑的原因
```

AI 會自動執行完整分析流程。

### 4. 手動運行

```bash
# Step 1: 處理文件
python scripts/file_processor.py

# Step 2: 生成圖表
python scripts/chart_generator.py

# Step 3: 生成報告
python scripts/report_builder.py

# Step 4: 啟動 Dashboard（可選）
streamlit run app.py
```

---

## 目錄結構

```
Data_Insight/
├── SKILL.md              # 主技能定義（完整方法論）
├── README.md             # 使用指南
├── requirements.txt      # Python 依賴
├── app.py                # Streamlit Dashboard
├── scripts/
│   ├── file_processor.py    # 文件處理
│   ├── chart_generator.py   # 圖表生成
│   ├── report_builder.py    # 報告構建
│   ├── ai_insight.py        # AI 洞察生成
│   ├── analyze_comments.py  # 評論分析
│   └── dump_analysis_data.py
├── references/           # 分析方法論文檔
│   ├── hypothesis-driven-analysis.md  # 假設驅動分析
│   ├── cognitive-biases.md            # 認知偏差檢驗
│   ├── driver-tree-analysis.md        # 驅動因素樹
│   ├── data-storytelling.md           # 數據敘事
│   ├── visualization-rules.md         # 可視化規則
│   ├── general-frameworks.md          # 通用框架
│   ├── data-interpretation.md         # 數據解讀
│   └── personal-methodology.md        # 個人方法論
├── uploads/              # 放置待分析文件
└── outputs/
    ├── charts/           # 生成的圖表
    └── reports/          # 生成的報告
```

---

## 分析方法論

### 核心準則

1. **相關性 ≠ 因果性**
   - 時間順序檢驗
   - 排除第三變量
   - 機制合理性驗證

2. **結論必須指向行動**
   - 具體可執行
   - 可衡量效果
   - 權責清晰

3. **短期突破 + 中長期複利**
   - 短期（1-2週）：快速突破
   - 中期（1-2月）：建立飛輪
   - 長期（3月+）：構建壁壘

### 偏差檢驗

分析時自動檢驗：
- 辛普森悖論
- 倖存者偏差
- 確認偏誤
- 因果謬誤

---

## 報告規範

### 寫作風格

| 要求 | 好例子 | 壞例子 |
|-----|--------|--------|
| 直接說發現 | `Android轉化率是iPhone的3倍` | `被忽視的金礦——Android的驚人表現` |
| 用數字說話 | `抖音ROI比信息流高2.4倍` | `抖音投放的隱藏價值` |
| 不用感歎號 | `這個渠道值得重點投入` | `這是被嚴重低估的金礦！` |

### 輸出格式

報告保存為 `outputs/reports/report.json`，包含：
- 核心結論（3-7 個）
- 數據支撐
- 圖表配置
- 行動建議

---

## 觸發條件

以下情況自動啟動此 Skill：

- 用戶上傳數據文件（.xlsx, .pdf, .docx, .csv, .txt）
- 用戶使用 `/analyze-data` 命令
- 用戶表達「分析數據」「數據洞察」「幫我分析」等意圖

---

## 參考文檔使用

`references/` 目錄的文檔**按需加載**，不要全部讀取：

| 場景 | 讀取文檔 |
|-----|---------|
| 構建分析框架 | `hypothesis-driven-analysis.md` |
| 結論反常識 | `cognitive-biases.md` |
| 拆解 KPI 驅動因素 | `driver-tree-analysis.md` |
| 準備匯報 | `data-storytelling.md` |
| 選擇圖表類型 | `visualization-rules.md` |
