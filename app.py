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

st.title("📊 Data Analysis Website")
st.write("👨‍💻 Developed by: Ganesh Chape and saurabh misal")
st.write("Welcome to my Data Analysis Website!")
