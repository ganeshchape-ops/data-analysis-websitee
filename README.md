# Student Data Analysis – Section-Wise Analysis with 6 Subjects

> **Enterprise-Grade Student Performance Analytics & Executive 11-Sheet Excel Reporting Engine**  
> Developed for client-ready deployment on Windows, macOS, and Linux.

---

## 🌟 Executive Overview

This project is a complete **Student Data Analysis & Reporting Solution** built to ingest student academic datasets in **Excel (`.xlsx`, `.xls`)** or **CSV (`.csv`)** format, perform non-destructive cleaning and anomaly audits, and automatically generate comprehensive **section-wise and subject-wise analytics across 6 subjects**.

The solution delivers:
1. **Interactive Web Dashboard**: Executive KPI cards, dynamic Chart.js visualizations, cross-tabulation heatmaps, and live student roster filtering.
2. **Executive 11-Sheet Excel Workbook**: Fully formatted `.xlsx` workbook featuring KPI cards, freeze panes, zebra striping, currency/percentage number formats, and conditional styling.
3. **Data-Driven Insights Engine**: Factual, metric-grounded observations without hallucinations or assumptions.
4. **Resilient Data Quality Auditor**: Detects missing marks, non-numeric strings, duplicates, and out-of-range scores while maintaining data integrity.

---

## 📊 Core Analytical Capabilities

### 1. Overall Cohort Performance
- **Cohort Size**: Total evaluated candidate records.
- **Parametric Measures**: Mean average marks, median marks, mode percentage, standard deviation (dispersion), and sample variance.
- **Spread & Extremes**: Highest percentage, lowest percentage, score range ($Max - Min$), and Interquartile Range (IQR).
- **Pass / Fail Accounting**: Explicit pass count, fail count, pass rate %, and fail rate %.

### 2. Section-Wise Benchmarking
- Multi-section comparative breakdowns: Student count, total marks sum, section mean score, median score, highest/lowest scores, and pass rates.
- **Consistency Index**: Standard deviation per section (identifies most consistent vs most volatile classroom cohorts).
- **Automated Highlighting**: Instant identification of top-performing section, lowest section, highest pass rate section, and lowest pass rate section.

### 3. Six-Subject Deep Dive
- Individual subject evaluation across all 6 subject streams:
  - **Valid Students Count** (strictly ignores missing values).
  - **Subject Mean, Median, Min, and Max**.
  - **Pass Count & Pass Rate %** (calculated against configurable pass mark).
  - **Performance Index %** ($Average / Max \times 100$).
- Identification of strongest subject, weakest subject, and subject difficulty alerts.

### 4. Section × Subject Matrix
- Dual cross-tabulated matrices ($N_{\text{sections}} \times 6$):
  - **Average Marks Matrix**
  - **Subject Pass Rate Matrix**
- Identifies section-specific strengths (e.g., Section A excels in Mathematics) and subjects requiring remedial intervention per section.

### 5. Student-Level Analytics & Honors
- **Calculated Attributes**: Valid subjects count, total marks, average score, percentage, letter grade, cohort rank (min/competition ranking), and pass/fail status.
- **Top 10 High Achievers Honors Board**: Golden medal badges, rank listing, and summary scores.
- **At-Risk Student Support Roster**: Identifies students with failed subjects or overall score $< 50.0\%$ for targeted intervention.

---

## 📐 Mathematical Formulas

| Metric | Mathematical Definition | Note |
| :--- | :--- | :--- |
| **Valid Subjects ($N_v$)** | $N_v = \sum_{i=1}^{6} \mathbb{I}(\text{Subject}_i \neq \text{NaN})$ | Missing marks are **never** assumed to be zero |
| **Total Marks ($T$)** | $T = \sum_{i=1}^{N_v} \text{Mark}_i$ | Sum of all non-missing subject marks |
| **Average Marks ($\mu$)** | $\mu = \frac{T}{N_v}$ | Evaluated strictly over valid subjects |
| **Percentage ($P$)** | $P = \frac{\mu}{\text{Max Subject Mark}} \times 100$ | Default max mark = 100.0 |
| **Standard Deviation ($s$)** | $s = \sqrt{\frac{1}{N-1}\sum_{k=1}^N (x_k - \bar{x})^2}$ | Sample standard deviation ($ddof = 1$) |
| **Pass Rate %** | $\text{Pass Rate} = \frac{\text{Passed Count}}{\text{Total Evaluated}} \times 100$ | Passed = all valid subject marks $\ge \text{Pass Mark}$ |

### Configurable Grading Scale
- **A+** : $90\% - 100\%$ (Outstanding)
- **A** : $80\% - 89.99\%$ (Excellent)
- **B** : $70\% - 79.99\%$ (Very Good)
- **C** : $60\% - 69.99\%$ (Good)
- **D** : $50\% - 59.99\%$ (Satisfactory)
- **E** : $40\% - 49.99\%$ (Pass)
- **F** : $< 40\%$ (Fail)

---

## 📑 11-Sheet Excel Workbook Structure

The generated Excel report (`.xlsx`) contains 11 dedicated, styled worksheets:

1. `Dashboard` : Executive summary block with KPI cards, section summary table, and subject summary table.
2. `Raw_Data` : Exact un-modified uploaded source data for audit traceability.
3. `Cleaned_Data` : Standardized dataset with calculated metrics (Valid Subs, Total, Average, %, Grade, Rank, Status).
4. `Data_Quality` : Audit metrics (Health score, duplicate counts, missing values) and issue validation log.
5. `Overall_Summary` : Complete cohort descriptive statistics table.
6. `Section_Analysis` : Section-by-section comparison table with pass rate highlights and consistency metrics.
7. `Subject_Analysis` : Comprehensive 6-subject evaluation table.
8. `Section_Subject` : Average marks matrix and subject pass rate matrix across sections.
9. `Student_Performance` : Complete ranked student master roster with color-coded grades and status.
10. `Top_Students` : Top 10 high-achievers leaderboard.
11. `Insights` : Factual narrative findings and strategic academic recommendations.

---

## 📁 Project Architecture

```
student_data_analysis/
│
├── app.py                      # Flask web application & REST APIs
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation & formulas
├── CLIENT_DEMO_GUIDE.md        # Client demonstration & pitch guide
├── generate_sample_data.py     # Script generating realistic test datasets
│
├── data/
│   ├── sample_students_data.xlsx    # Clean 120-student demo dataset (4 sections, 6 subjects)
│   ├── sample_students_data.csv     # Clean CSV demo dataset
│   └── dirty_sample_students.xlsx   # Anomaly test dataset (duplicates, missing, strings)
│
├── uploads/                    # Directory for user uploaded files
├── outputs/                    # Exported Excel reports and chart images
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py          # Multi-format ingestion & fuzzy column auto-detection
│   ├── data_cleaning.py        # Safe numeric parsing, duplicate removal & quality audit
│   ├── analysis.py             # Math calculations, rankings, grades & matrices
│   ├── insights.py             # Data-driven executive insights generator
│   ├── visualization.py        # Publication Matplotlib charts & Chart.js payloads
│   └── excel_report.py         # 11-sheet OpenPyXL executive workbook builder
│
├── templates/
│   ├── base.html               # Shared HTML layout with modern typography & theme toggle
│   ├── index.html              # Drag-and-drop upload page with demo loaders
│   └── dashboard.html          # Interactive executive analytics dashboard
│
├── static/
│   ├── css/
│   │   └── style.css           # Executive CSS design system (Dark & Light theme support)
│   └── js/
│       └── script.js           # Client-side Chart.js controllers & table filter logic
│
└── tests/
    ├── __init__.py
    ├── test_analysis.py        # Unit tests for math, cleaning, ranking, and Excel generation
    └── test_webapp.py          # Integration tests for Flask routes and endpoints
```

---

## 🚀 Installation & Quick Start

### 1. Prerequisites
- Python 3.9, 3.10, 3.11, 3.12, 3.13, or 3.14 installed on your system.

### 2. Setup Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the Web Application

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests

Run the full automated test suite using `unittest`:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

All tests validate:
- Exact total, average, and percentage calculation formulas.
- Safe missing marks handling (no zero assumption).
- Section and subject reconciliation against student rows.
- Data cleaning resilience on noisy inputs.
- 11-sheet OpenPyXL report generation.
- Flask endpoints and REST API payloads.

---

## 💡 REST API Integration

The application includes a REST API endpoint for integration into external educational software:

### `GET /api/analysis`
Returns a structured JSON payload containing overall stats, section summaries, subject breakdowns, matrices, quality audits, and top student lists.
