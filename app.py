import streamlit as st
import pandas as pd
import numpy as np
import io

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="EduMetrics Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at top left, #172554 0%, transparent 35%),
        radial-gradient(circle at bottom right, #1e1b4b 0%, transparent 35%),
        #070b18;
    color: white;
}

.block-container {
    max-width: 1250px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}

/* HEADER */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 5px 20px 5px;
    border-bottom: 1px solid rgba(255,255,255,0.10);
}

.brand {
    font-size: 25px;
    font-weight: 800;
    color: white;
}

.brand-sub {
    font-size: 12px;
    color: #8d96b8;
}

/* HERO */
.hero {
    text-align: center;
    padding: 70px 15px 35px 15px;
}

.hero h1 {
    font-size: 48px;
    font-weight: 800;
    margin-bottom: 15px;
    background: linear-gradient(90deg,#ffffff,#9ca3ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    font-size: 17px;
    line-height: 1.7;
    color: #aeb7d5;
    max-width: 850px;
    margin: auto;
}

/* UPLOAD */
.upload-card {
    border: 2px dashed #3949ab;
    border-radius: 24px;
    padding: 40px;
    text-align: center;
    background: rgba(30,41,90,0.30);
    margin: 20px auto;
}

.upload-icon {
    font-size: 48px;
}

.upload-title {
    font-size: 22px;
    font-weight: 700;
    margin-top: 10px;
}

.badge {
    display: inline-block;
    padding: 6px 13px;
    margin: 12px 4px;
    border-radius: 8px;
    background: rgba(70,90,200,0.25);
    border: 1px solid rgba(120,140,255,0.3);
    color: #dce2ff;
    font-size: 13px;
}

/* CARDS */
.feature-card {
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 24px;
    min-height: 190px;
}

.feature-icon {
    font-size: 28px;
    margin-bottom: 10px;
}

.feature-title {
    font-size: 18px;
    font-weight: 700;
    color: white;
    margin-bottom: 10px;
}

.feature-text {
    color: #aeb7d5;
    font-size: 14px;
    line-height: 1.6;
}

/* METRIC */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    padding: 18px;
    border-radius: 16px;
}

/* BUTTON */
.stButton > button {
    border-radius: 10px;
    font-weight: 700;
}

/* FOOTER */
.footer {
    text-align: center;
    margin-top: 50px;
    padding-top: 25px;
    border-top: 1px solid rgba(255,255,255,0.10);
    color: #8d96b8;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="header">

    <div>
        <div class="brand">🎓 EduMetrics Pro</div>
        <div class="brand-sub">
            Section & 6-Subject Analytics
        </div>
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero">

<h1>Student Performance Analytics Engine</h1>

<p>
Upload student records in Excel or CSV format.
Analyze student performance, subject-wise averages,
section-wise performance, top students and individual results
with a clean interactive dashboard.
</p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# UPLOAD CARD
# =========================================================
st.markdown("""
<div class="upload-card">

<div class="upload-icon">☁️</div>

<div class="upload-title">
Drag and drop your student dataset here
</div>

<p style="color:#9da7c7;">
or click below to browse files from your computer
</p>

<span class="badge">.XLSX</span>
<span class="badge">.CSV</span>
<span class="badge">.XLS</span>

</div>
""", unsafe_allow_html=True)


# =========================================================
# FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader(
    "Upload Student Dataset",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed"
)


# =========================================================
# SUBJECT DETECTION
# =========================================================
SUBJECT_ALIASES = {
    "Mathematics": [
        "Mathematics",
        "Math",
        "Maths",
        "Mathematics Marks"
    ],

    "Science": [
        "Science",
        "Science Marks"
    ],

    "English": [
        "English",
        "English Marks"
    ],

    "Hindi": [
        "Hindi",
        "Hindi Marks"
    ],

    "Social Science": [
        "Social Science",
        "SocialScience",
        "Social_Science",
        "SST",
        "Social Studies"
    ],

    "Computer": [
        "Computer",
        "Computer Science",
        "Computer Marks"
    ]
}


def detect_subject_columns(df):

    detected = {}

    # Case-insensitive column lookup
    column_map = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for subject, aliases in SUBJECT_ALIASES.items():

        found = None

        for alias in aliases:

            key = alias.strip().lower()

            if key in column_map:
                found = column_map[key]
                break

        if found is not None:
            detected[subject] = found

    return detected


# =========================================================
# READ FILE
# =========================================================
def read_uploaded_file(file):

    try:

        filename = file.name.lower()

        if filename.endswith(".csv"):

            # Try UTF-8 first
            try:
                data = pd.read_csv(file)
            except UnicodeDecodeError:
                file.seek(0)
                data = pd.read_csv(
                    file,
                    encoding="latin1"
                )

        elif filename.endswith(".xlsx"):

            data = pd.read_excel(
                file,
                engine="openpyxl"
            )

        elif filename.endswith(".xls"):

            data = pd.read_excel(
                file
            )

        else:
            st.error("Unsupported file format.")
            return None

        return data

    except Exception as e:

        st.error(
            f"❌ Could not read the file: {e}"
        )

        return None


# =========================================================
# MAIN ANALYSIS
# =========================================================
if uploaded_file is not None:

    # -----------------------------------------------------
    # Read Data
    # -----------------------------------------------------
    df = read_uploaded_file(uploaded_file)

    if df is not None and not df.empty:

        # Remove completely empty columns
        df = df.dropna(
            axis=1,
            how="all"
        )

        # Remove completely empty rows
        df = df.dropna(
            axis=0,
            how="all"
        )

        # Clean column names
        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        # -------------------------------------------------
        # Detect subjects
        # -------------------------------------------------
        detected_subjects = detect_subject_columns(df)

        subject_cols = list(
            detected_subjects.values()
        )

        subject_names = list(
            detected_subjects.keys()
        )

        # -------------------------------------------------
        # DATASET
        # -------------------------------------------------
        st.subheader("📋 Dataset Preview")

        st.caption(
            f"File: {uploaded_file.name}  |  "
            f"Rows: {len(df)}  |  "
            f"Columns: {len(df.columns)}"
        )

        st.dataframe(
            df,
            use_container_width=True,
            height=350
        )

        # -------------------------------------------------
        # SUBJECT CHECK
        # -------------------------------------------------
        if len(subject_cols) == 0:

            st.error(
                "❌ No subject columns found."
            )

            st.info(
                "Expected subjects: Mathematics, Science, "
                "English, Hindi, Social Science, Computer"
            )

        else:

            st.success(
                f"✅ Detected {len(subject_cols)} subject(s): "
                + ", ".join(subject_names)
            )

            # -------------------------------------------------
            # Convert subject columns to numeric
            # -------------------------------------------------
            for col in subject_cols:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

            # -------------------------------------------------
            # Total
            # -------------------------------------------------
            df["Total"] = df[
                subject_cols
            ].sum(
                axis=1,
                skipna=True
            )

            # -------------------------------------------------
            # Average
            # -------------------------------------------------
            df["Average"] = df[
                subject_cols
            ].mean(
                axis=1,
                skipna=True
            )

            # =================================================
            # PERFORMANCE SUMMARY
            # =================================================
            st.subheader("📊 Performance Overview")

            c1, c2, c3, c4 = st.columns(4)

            # Total students
            with c1:

                st.metric(
                    "👨‍🎓 Total Students",
                    len(df)
                )

            # Average
            with c2:

                overall_average = df[
                    "Average"
                ].mean()

                st.metric(
                    "📈 Overall Average",
                    f"{overall_average:.2f}"
                )

            # Highest total
            with c3:

                highest_total = df[
                    "Total"
                ].max()

                st.metric(
                    "🏆 Highest Total",
                    f"{highest_total:.2f}"
                )

            # Subjects
            with c4:

                st.metric(
                    "📚 Subjects Found",
                    len(subject_cols)
                )

            # =================================================
            # SUBJECT-WISE AVERAGE
            # =================================================
            st.subheader("📈 Subject-wise Average")

            subject_average = (
                df[subject_cols]
                .mean()
                .sort_values(
                    ascending=False
                )
            )

            # Rename for display
            display_subject_average = (
                subject_average.rename(
                    {
                        detected_subjects[s]: s
                        for s in subject_names
                    }
                )
            )

            st.bar_chart(
                display_subject_average
            )

            # =================================================
            # SUBJECT STATISTICS
            # =================================================
            st.subheader("📚 Subject Statistics")

            stats_data = []

            for subject in subject_names:

                col = detected_subjects[subject]

                values = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

                stats_data.append({

                    "Subject": subject,

                    "Average":
                        round(values.mean(), 2),

                    "Highest":
                        round(values.max(), 2),

                    "Lowest":
                        round(values.min(), 2),

                    "Pass Count":
                        int((values >= 40).sum()),

                    "Fail Count":
                        int((values < 40).sum())

                })

            stats_df = pd.DataFrame(
                stats_data
            )

            st.dataframe(
                stats_df,
                use_container_width=True,
                hide_index=True
            )

            # =================================================
            # TOP STUDENTS
            # =================================================
            st.subheader("🏆 Top 5 Students")

            name_column = None

            possible_names = [
                "Student Name",
                "Name",
                "Student",
                "Student_Name",
                "student_name"
            ]

            for name in possible_names:

                if name in df.columns:

                    name_column = name
                    break

            if name_column is not None:

                top5 = (
                    df.sort_values(
                        "Total",
                        ascending=False
                    )
                    .head(5)
                )

                st.dataframe(
                    top5[
                        [
                            name_column,
                            "Total",
                            "Average"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning(
                    "Student name column not found."
                )

            # =================================================
            # SECTION ANALYSIS
            # =================================================
            if "Section" in df.columns:

                st.subheader(
                    "📚 Section-wise Analysis"
                )

                section_avg = (
                    df.groupby("Section")[
                        subject_cols
                    ]
                    .mean()
                    .mean(axis=1)
                    .sort_values(
                        ascending=False
                    )
                )

                st.bar_chart(
                    section_avg
                )

                section_table = (
                    df.groupby("Section")[
                        subject_cols
                    ]
                    .mean()
                    .round(2)
                )

                st.dataframe(
                    section_table,
                    use_container_width=True
                )

            # =================================================
            # INDIVIDUAL STUDENT
            # =================================================
            if name_column is not None:

                st.subheader(
                    "👨‍🎓 Individual Student Analysis"
                )

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

                    student_rows = df[
                        df[name_column].astype(str)
                        == selected_student
                    ]

                    if not student_rows.empty:

                        student = (
                            student_rows.iloc[0]
                        )

                        c1, c2, c3 = st.columns(3)

                        with c1:

                            st.metric(
                                "Student",
                                selected_student
                            )

                        with c2:

                            st.metric(
                                "Total Marks",
                                f"{student['Total']:.2f}"
                            )

                        with c3:

                            st.metric(
                                "Average",
                                f"{student['Average']:.2f}"
                            )

                        # -------------------------------------
                        # Individual chart
                        # -------------------------------------
                        student_marks = pd.Series(
                            {
                                subject:
                                student[
                                    detected_subjects[
                                        subject
                                    ]
                                ]
                                for subject in subject_names
                            }
                        )

                        st.subheader(
                            "📊 Subject-wise Marks"
                        )

                        st.bar_chart(
                            student_marks
                        )

                        # -------------------------------------
                        # Student table
                        # -------------------------------------
                        individual_table = pd.DataFrame({

                            "Subject":
                                subject_names,

                            "Marks": [
                                student[
                                    detected_subjects[
                                        subject
                                    ]
                                ]
                                for subject in subject_names
                            ]

                        })

                        st.dataframe(
                            individual_table,
                            use_container_width=True,
                            hide_index=True
                        )

            # =================================================
            # COMPLETE ANALYSIS
            # =================================================
            st.subheader(
                "📋 Complete Analysis"
            )

            st.dataframe(
                df,
                use_container_width=True,
                height=400
            )

            # =================================================
            # DOWNLOAD CSV
            # =================================================
            st.subheader(
                "⬇️ Export Analysis"
            )

            csv_data = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="📥 Download Analysis CSV",
                data=csv_data,
                file_name="Student_Performance_Analysis.csv",
                mime="text/csv"
            )


# =========================================================
# FEATURE CARDS
# =========================================================
else:

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown("""
        <d
