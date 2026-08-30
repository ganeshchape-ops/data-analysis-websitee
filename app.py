"""
Student Data Analysis Web Application
Flask backend providing file upload, data cleaning, 6-subject section analysis,
interactive dashboard, chart rendering, and 11-sheet Excel generation.
"""
import streamlit as st 
import os
import io
import uuid
from typing import Dict, Any
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import pandas as pd

from utils.data_loader import load_raw_data, detect_column_mapping, apply_column_mapping
from utils.data_cleaning import clean_student_data
from utils.analysis import perform_full_analysis
from utils.insights import generate_automated_insights
from utils.visualization import generate_all_visualizations, prepare_chartjs_data
from utils.excel_report import generate_excel_report


app = Flask(__name__)
app.secret_key = "student_analytics_executive_key_2026"

# Configure directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# In-memory store for active session analysis
ACTIVE_ANALYSIS_STORE: Dict[str, Any] = {}


def run_pipeline(file_path: str, filename: str, pass_mark: float = 40.0, max_subject_mark: float = 100.0, remove_duplicates: bool = True) -> Dict[str, Any]:
    """
    Executes the end-to-end analytical pipeline:
    Loader -> Fuzzy Mapping -> Cleaning & Audit -> Math Engine -> Visualizations -> Excel Report.
    """
    # 1. Load raw dataset
    raw_df = load_raw_data(file_path, filename)
    
    # 2. Detect column mapping
    mapping_info = detect_column_mapping(raw_df)
    if not mapping_info["is_valid"]:
        missing_str = ", ".join(mapping_info["missing_required"])
        raise ValueError(f"Required columns could not be identified: {missing_str}. Please verify file headers.")

    # 3. Apply column mapping
    std_df, display_names = apply_column_mapping(raw_df, mapping_info["mapping"])
    subject_keys = display_names["_subject_keys"]

    # 4. Clean data & generate quality audit
    cleaned_df, quality_summary = clean_student_data(
        df=std_df,
        subject_keys=subject_keys,
        display_names=display_names,
        min_mark=0.0,
        max_mark=max_subject_mark,
        remove_duplicates=remove_duplicates
    )

    # 5. Perform mathematical analysis
    analysis_results = perform_full_analysis(
        df=cleaned_df,
        subject_keys=subject_keys,
        display_names=display_names,
        pass_mark=pass_mark,
        max_subject_mark=max_subject_mark
    )

    # 6. Generate 100% data-driven automated insights
    insights = generate_automated_insights(analysis_results, quality_summary)

    # 7. Generate publication charts & Chart.js payloads
    charts_dir = os.path.join(OUTPUT_FOLDER, "charts")
    charts_b64 = generate_all_visualizations(analysis_results, output_dir=charts_dir)
    chartjs_data = prepare_chartjs_data(analysis_results)

    # 8. Generate 11-Sheet Excel Report
    report_filename = f"Student_Analysis_Report_{uuid.uuid4().hex[:8]}.xlsx"
    excel_report_path = os.path.join(OUTPUT_FOLDER, report_filename)
    generate_excel_report(
        raw_df=raw_df,
        analysis_results=analysis_results,
        quality_summary=quality_summary,
        insights=insights,
        output_path=excel_report_path
    )

    # Save to active store
    ACTIVE_ANALYSIS_STORE["current"] = {
        "raw_df": raw_df,
        "filename": filename,
        "analysis_results": analysis_results,
        "quality_summary": quality_summary,
        "insights": insights,
        "charts_b64": charts_b64,
        "chartjs_data": chartjs_data,
        "excel_report_path": excel_report_path,
        "report_filename": report_filename
    }

    return ACTIVE_ANALYSIS_STORE["current"]


@app.route("/")
def index():
    """Landing page with file upload and demo controls."""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles dataset upload and initiates analysis."""
    if "file" not in request.files:
        flash("No file selected for upload.", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    # Configurable parameters
    pass_mark = float(request.form.get("pass_mark", 40.0))
    max_subject_mark = float(request.form.get("max_subject_mark", 100.0))
    remove_duplicates = request.form.get("remove_duplicates") == "true"

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    try:
        run_pipeline(
            file_path=save_path,
            filename=filename,
            pass_mark=pass_mark,
            max_subject_mark=max_subject_mark,
            remove_duplicates=remove_duplicates
        )
        return redirect(url_for("dashboard"))
    except Exception as e:
        flash(f"Analysis failed: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/demo/<demo_type>")
def load_demo(demo_type: str):
    """Loads pre-generated demo datasets for instant testing."""
    if demo_type == "dirty":
        demo_file = os.path.join(DATA_FOLDER, "dirty_sample_students.xlsx")
        filename = "dirty_sample_students.xlsx"
    else:
        demo_file = os.path.join(DATA_FOLDER, "sample_students_data.xlsx")
        filename = "sample_students_data.xlsx"

    if not os.path.exists(demo_file):
        # Auto generate if not found
        from generate_sample_data import generate_sample_datasets
        generate_sample_datasets()

    try:
        run_pipeline(demo_file, filename)
        flash(f"Loaded demo dataset '{filename}' successfully!", "success")
        return redirect(url_for("dashboard"))
    except Exception as e:
        flash(f"Failed to load demo: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    """Renders the executive analytical dashboard."""
    if "current" not in ACTIVE_ANALYSIS_STORE:
        # Load clean demo as default if user visits /dashboard directly
        return redirect(url_for("load_demo", demo_type="clean"))

    data = ACTIVE_ANALYSIS_STORE["current"]
    res = data["analysis_results"]

    return render_template(
        "dashboard.html",
        filename=data["filename"],
        overall_stats=res["overall_stats"],
        section_summary_df=res["section_summary_df"],
        section_highlights=res["section_highlights"],
        subject_summary_df=res["subject_summary_df"],
        subject_highlights=res["subject_highlights"],
        average_matrix_df=res["average_matrix_df"],
        pass_matrix_df=res["pass_matrix_df"],
        student_df=res["student_df"],
        top_10_df=res["top_10_df"],
        at_risk_df=res["at_risk_df"],
        quality_summary=data["quality_summary"],
        insights=data["insights"],
        charts_b64=data["charts_b64"],
        chartjs_data=data["chartjs_data"],
        subject_keys=res["subject_keys"],
        display_names=res["display_names"]
    )


@app.route("/export/excel")
def export_excel():
    """Downloads the generated 11-sheet Excel report."""
    if "current" not in ACTIVE_ANALYSIS_STORE:
        flash("No active analysis to export. Please upload a file first.", "error")
        return redirect(url_for("index"))

    path = ACTIVE_ANALYSIS_STORE["current"]["excel_report_path"]
    filename = ACTIVE_ANALYSIS_STORE["current"]["report_filename"]
    return send_file(path, as_attachment=True, download_name=filename)


@app.route("/export/csv")
def export_csv():
    """Exports cleaned and analyzed student performance roster as CSV."""
    if "current" not in ACTIVE_ANALYSIS_STORE:
        flash("No active analysis to export.", "error")
        return redirect(url_for("index"))

    student_df = ACTIVE_ANALYSIS_STORE["current"]["analysis_results"]["student_df"]
    csv_buffer = io.StringIO()
    student_df.to_csv(csv_buffer, index=False)
    csv_bytes = io.BytesIO(csv_buffer.getvalue().encode("utf-8"))

    return send_file(
        csv_bytes,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"Student_Performance_Roster_{uuid.uuid4().hex[:6]}.csv"
    )


@app.route("/api/analysis")
def api_analysis():
    """REST API endpoint returning complete analytical JSON dataset."""
    if "current" not in ACTIVE_ANALYSIS_STORE:
        return jsonify({"error": "No active dataset loaded"}), 400

    data = ACTIVE_ANALYSIS_STORE["current"]
    res = data["analysis_results"]

    payload = {
        "filename": data["filename"],
        "overall_stats": res["overall_stats"],
        "section_summary": res["section_summary_df"].to_dict(orient="records"),
        "subject_summary": res["subject_summary_df"].to_dict(orient="records"),
        "average_matrix": res["average_matrix_df"].to_dict(orient="records"),
        "pass_matrix": res["pass_matrix_df"].to_dict(orient="records"),
        "top_10": res["top_10_df"].to_dict(orient="records"),
        "at_risk_count": len(res["at_risk_df"]),
        "quality_summary": {
            "health_score": data["quality_summary"]["quality_score"],
            "total_records": data["quality_summary"]["valid_records"],
            "duplicates_purged": data["quality_summary"]["duplicate_rows"] + data["quality_summary"]["duplicate_ids"],
            "missing_marks": data["quality_summary"]["missing_marks_count"],
            "invalid_marks": data["quality_summary"]["invalid_marks_count"]
        },
        "insights": data["insights"]
    }
    return jsonify(payload)

import streamlit as st
import pandas as pd

# -----------------------------
# Page Settings
# -----------------------------
st.set_page_config(
    page_title="Data Analysis Website",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------
st.title("📊 Data Analysis Website")
st.write("Upload your student CSV file to analyze the data.")

# -----------------------------
# Upload CSV
# -----------------------------
uploaded_file = st.file_uploader(
    "📁 Upload CSV File",
    type=["csv"]
)

# -----------------------------
# Main Program
# -----------------------------
if uploaded_file is not None:

    # Read CSV
    df = pd.read_csv(uploaded_file)

    # -----------------------------
    # Dataset
    # -----------------------------
    st.subheader("📋 Dataset")

    st.dataframe(
        df,
        use_container_width=True
    )

    # -----------------------------
    # Subject Columns
    # -----------------------------
    subjects = [
        "Mathematics",
        "Science",
        "English",
        "Hindi",
        "Social Science",
        "Computer"
    ]

    subject_cols = [
        col for col in subjects
        if col in df.columns
    ]

    # -----------------------------
    # Check Subject Columns
    # -----------------------------
    if len(subject_cols) == 0:

        st.error(
            "❌ No subject columns found in the CSV file."
        )

    else:

        # -----------------------------
        # Total & Average
        # -----------------------------
        df["Total"] = df[subject_cols].sum(axis=1)

        df["Average"] = df[subject_cols].mean(axis=1)

        # -----------------------------
        # Student Performance
        # -----------------------------
        st.subheader("📊 Student Performance")

        col1, col2, col3 = st.columns(3)

        # Total Students
        with col1:
            st.metric(
                "👨‍🎓 Total Students",
                len(df)
            )

        # Overall Average
        with col2:
            overall_average = df["Average"].mean()

            st.metric(
                "📈 Overall Average",
                round(overall_average, 2)
            )

        # Top Student
        with col3:

            if "Student Name" in df.columns:

                top_index = df["Total"].idxmax()

                top_student = df.loc[
                    top_index,
                    "Student Name"
                ]

                st.metric(
                    "🏆 Top Student",
                    top_student
                )

        # -----------------------------
        # Subject-wise Average
        # -----------------------------
        st.subheader("📈 Subject-wise Average")

        subject_average = df[subject_cols].mean()

        st.bar_chart(
            subject_average
        )

        # -----------------------------
        # Top 5 Students
        # -----------------------------
        st.subheader("🏆 Top 5 Students")

        if "Student Name" in df.columns:

            top5 = df.sort_values(
                "Total",
                ascending=False
            ).head(5)

            st.dataframe(
                top5[
                    [
                        "Student Name",
                        "Total",
                        "Average"
                    ]
                ],
                use_container_width=True
            )

        # -----------------------------
        # Section-wise Analysis
        # -----------------------------
        if "Section" in df.columns:

            st.subheader("📚 Section-wise Analysis")

            section_average = (
                df.groupby("Section")[subject_cols]
                .mean()
            )

            section_average = section_average.mean(
                axis=1
            )

            st.bar_chart(
                section_average
            )

        # -----------------------------
        # Individual Student Analysis
        # -----------------------------
        if "Student Name" in df.columns:

            st.subheader("👨‍🎓 Individual Student Performance")

            student_name = st.selectbox(
                "Select Student",
                df["Student Name"].unique()
            )

            student_data = df[
                df["Student Name"] == student_name
            ].iloc[0]

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Total Marks",
                    round(
                        student_data["Total"],
                        2
                    )
                )

            with col2:

                st.metric(
                    "Average",
                    round(
                        student_data["Average"],
                        2
                    )
                )

            # -----------------------------
            # Selected Student Chart
            # -----------------------------
            st.subheader("📊 Subject-wise Marks")

            student_marks = student_data[
                subject_cols
            ]

            st.bar_chart(
                student_marks
            )

        # -----------------------------
        # Complete Analysis Table
        # -----------------------------
        st.subheader("📋 Complete Analysis")

        st.dataframe(
            df,
            use_container_width=True
        )

else:

    st.info(
        "👆 Please upload a CSV file to start analysis."
    )

st.subheader("📊 Subject-wise Marks")

file = st.file_uploader("Upload CSV File", type=["csv"])

if file is not None:
    df = pd.read_csv(file)

    st.subheader("📊 Subject-wise Marks")

    subjects = [
        "Mathematics",
        "Science",
        "English",
        "Hindi",
        "Social Science",
        "Computer"
    ]

    subject_cols = [col for col in subjects if col in df.columns]

    if subject_cols:
        subject_average = df[subject_cols].mean()
        st.bar_chart(subject_average)
    else:
        st.warning("Subject columns not found in CSV.")
else:
    st.info("👆 Please upload a CSV file to start analysis.")
import streamlit as st
import pandas as pd
import numpy as np
import io

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="EduMetrics Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# CSS - MODERN DARK UI
# -------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #080b24, #11183d, #18245a);
        color: white;
    }

    .block-container {
        padding-top: 1rem;
        max-width: 1200px;
    }

    .brand {
        font-size: 25px;
        font-weight: 800;
        color: white;
        padding: 10px 0;
    }

    .hero {
        text-align: center;
        padding: 70px 20px 35px 20px;
    }

    .hero h1 {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 15px;
    }

    .hero p {
        font-size: 18px;
        color: #d5d9f5;
        max-width: 800px;
        margin: auto;
    }

    .upload-box {
        border: 2px dashed #6574e8;
        border-radius: 25px;
        padding: 45px;
        text-align: center;
        background: rgba(90, 105, 220, 0.12);
        margin: 20px 0;
    }

    .upload-title {
        font-size: 22px;
        font-weight: 700;
    }

    .badge {
        display: inline-block;
        padding: 7px 14px;
        margin: 10px 4px;
        border-radius: 8px;
        background: rgba(100,120,255,0.25);
        font-weight: 600;
    }

    .card {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .developer {
        text-align: center;
        color: #bfc6ed;
        padding: 35px;
        font-size: 15px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.07);
        padding: 15px;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
c1, c2, c3, c4 = st.columns([3, 1, 1, 1])

with c1:
    st.markdown(
        '<div class="brand">🎓 EduMetrics Pro</div>',
        unsafe_allow_html=True
    )

with c2:
    st.markdown("🏠 New Upload")

with c3:
    st.markdown("⚡ Clean Demo")

with c4:
    st.markdown("🧪 Anomaly Test")

# -------------------------------------------------
# HERO SECTION
# -------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>Student Performance Analytics Engine</h1>

    <p>
        Upload student records in Excel (.xlsx, .xls) or CSV (.csv) format.
        Automatically performs section-wise benchmarking,
        subject-wise statistical analysis, anomaly checks,
        and generates useful performance reports.
    </p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# UPLOAD SECTION
# -------------------------------------------------
st.markdown("""
<div class="upload-box">
    <div style="font-size:50px;">☁️</div>
    <div class="upload-title">
        Drag and drop your student dataset here
    </div>
    <p>or click below to browse files from your computer</p>

    <span class="badge">XLSX</span>
    <span class="badge">CSV</span>
    <span class="badge">XLS</span>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Student Dataset",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed"
)

# -------------------------------------------------
# FUNCTION TO READ FILE
# -------------------------------------------------
def read_file(file):

    try:
        if file.name.lower().endswith(".csv"):
            return pd.read_csv(file)

        elif file.name.lower().endswith((".xlsx", ".xls")):
            return pd.read_excel(file)

    except Exception as e:
        st.error("Unable to read this file.")
        st.error(str(e))
        return None

    return None


# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
if uploaded_file is not None:

    # IMPORTANT: df is created here
    df = read_file(uploaded_file)

    if df is None:
        st.stop()

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Remove completely empty columns
    df = df.dropna(axis=1, how="all")

    st.success(
        f"✅ File uploaded successfully: {uploaded_file.name}"
    )

    # -------------------------------------------------
    # DATASET
    # -------------------------------------------------
    st.header("📊 Dataset")

    st.dataframe(
        df,
        use_container_width=True,
        height=350
    )

    # -------------------------------------------------
    # FIND SUBJECT COLUMNS AUTOMATICALLY
    # -------------------------------------------------

    excluded_columns = [
        "Student Name",
        "Student",
        "Name",
        "Section",
        "Roll No",
        "Roll Number",
        "ID",
        "Gender"
    ]

    subjects = []

    for col in df.columns:

        if col not in excluded_columns:

            # Convert to numeric
            numeric_values = pd.to_numeric(
                df[col],
                errors="coerce"
            )

            # Consider it a subject if it has numeric values
            if numeric_values.notna().sum() > 0:
                subjects.append(col)

    # This prevents subject_cols NameError
    subject_cols = [
        col for col in subjects
        if col in df.columns
    ]

    # Convert subject columns to numbers
    for col in subject_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # -------------------------------------------------
    # TOTAL AND AVERAGE
    # -------------------------------------------------

    if len(subject_cols) > 0:

        df["Total"] = df[subject_cols].sum(
            axis=1,
            skipna=True
        )

        df["Average"] = df[subject_cols].mean(
            axis=1,
            skipna=True
        )

    else:
        st.warning(
            "⚠️ No numeric subject columns found in the dataset."
        )
        st.stop()

    # -------------------------------------------------
    # DASHBOARD
    # -------------------------------------------------

    st.header("📈 Student Performance")

    total_students = len(df)

    overall_average = round(
        df["Average"].mean(),
        2
    )

    top_index = df["Average"].idxmax()

    # Safely find student name
    name_column = None

    for possible in [
        "Student Name",
        "Student",
        "Name"
    ]:
        if possible in df.columns:
            name_column = possible
            break

    if name_column:
        top_student = df.loc[
            top_index,
            name_column
        ]
    else:
        top_student = f"Student {top_index + 1}"

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            "👨‍🎓 Total Students",
            total_students
        )

    with m2:
        st.metric(
            "📊 Overall Average",
            overall_average
        )

    with m3:
        st.metric(
            "🏆 Top Student",
            str(top_student)
        )

    # -------------------------------------------------
    # SUBJECT-WISE AVERAGE
    # -------------------------------------------------

    st.subheader("📊 Subject-wise Average")

    subject_average = df[subject_cols].mean()

    st.bar_chart(subject_average)

    # -------------------------------------------------
    # SECTION-WISE ANALYSIS
    # -------------------------------------------------

    if "Section" in df.columns:

        st.subheader("📚 Section-wise Analysis")

        section_average = (
            df.groupby("Section")["Average"]
            .mean()
            .sort_values(ascending=False)
        )

        st.bar_chart(section_average)

        st.dataframe(
            section_average.reset_index(
                name="Average"
            ),
            use_container_width=True
        )

    # -------------------------------------------------
    # STUDENT SELECTOR
    # -------------------------------------------------

    st.subheader("👨‍🎓 Student Performance")

    if name_column:

        student_list = (
            df[name_column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if student_list:

            selected_student = st.selectbox(
                "Select Student",
                student_list
            )

            student_data = df[
                df[name_column].astype(str)
                == selected_student
            ].iloc[0]

            st.markdown(
                f"### Selected Student: {selected_student}"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Total Marks",
                    round(
                        float(student_data["Total"]),
                        2
                    )
                )

            with col2:
                st.metric(
                    "Average",
                    round(
                        float(student_data["Average"]),
                        2
                    )
                )

            # Student subject marks
            marks = student_data[
                subject_cols
            ].astype(float)

            st.subheader("📊 Subject-wise Marks")

            # IMPORTANT:
            # marks is defined before st.bar_chart
            st.bar_chart(marks)

            st.dataframe(
                marks.reset_index(
                    name="Marks"
                ),
                use_container_width=True
            )

    # -------------------------------------------------
    # TOP STUDENTS
    # -------------------------------------------------

    st.subheader("🏆 Top Students")

    top_columns = []

    if name_column:
        top_columns.append(name_column)

    top_columns += [
        "Total",
        "Average"
    ]

    top_students = (
        df[top_columns]
        .sort_values(
            "Average",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_students,
        use_container_width=True
    )

    # -------------------------------------------------
    # DOWNLOAD REPORT
    # -------------------------------------------------

    st.subheader("📥 Download Analysis")

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Student Data",
            index=False
        )

        subject_average.reset_index(
            name="Average"
        ).to_excel(
            writer,
            sheet_name="Subject Average",
            index=False
        )

        if "Section" in df.columns:

            section_average.reset_index(
                name="Average"
            ).to_excel(
                writer,
                sheet_name="Section Average",
                index=False
            )

        top_students.to_excel(
            writer,
            sheet_name="Top Students",
            index=False
        )

    st.download_button(
        label="📥 Download Excel Report",
        data=output.getvalue(),
        file_name="Student_Performance_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:

    st.info(
        "👆 Please upload a CSV or Excel file to start analysis."
    )


# -------------------------------------------------
# DEVELOPER
# -------------------------------------------------
st.markdown("""
<div class="developer">
    <hr>
    <b>Developed by Ganesh</b><br>
    Student Performance Analytics Project<br>
    © 2026 EduMetrics Pro
</div>
""", unsafe_allow_html=True)
st.title("📊 Data Analysis Website")
st.write("👨‍💻 Developed by: Ganesh chape and saurabh misal ")
st.write("Welcome to my Data Analysis Website!")
