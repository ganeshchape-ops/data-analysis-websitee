import streamlit as st
import pandas as pd
import numpy as np

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
    background: linear-gradient(135deg, #080b24, #11183d, #18245a);
    color: white;
}

.block-container {
    max-width: 1200px;
    padding-top: 1rem;
}

/* Header */
.brand {
    font-size: 27px;
    font-weight: 800;
    color: white;
}

/* Hero */
.hero {
    text-align: center;
    padding: 55px 20px 30px 20px;
}

.hero h1 {
    font-size: 46px;
    font-weight: 800;
    margin-bottom: 15px;
}

.hero p {
    font-size: 17px;
    color: #d5d9f5;
    max-width: 850px;
    margin: auto;
    line-height: 1.7;
}

/* Upload box */
.upload-box {
    border: 2px dashed #6574e8;
    border-radius: 25px;
    padding: 35px;
    text-align: center;
    background: rgba(90,105,220,0.12);
    margin: 20px 0;
}

.upload-title {
    font-size: 22px;
    font-weight: 700;
}

.badge {
    display: inline-block;
    padding: 7px 15px;
    margin: 8px 4px;
    border-radius: 10px;
    background: rgba(100,120,255,0.25);
    font-weight: 600;
}

/* Cards */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    padding: 18px;
    border-radius: 18px;
}

/* Developer */
.developer {
    text-align: center;
    color: #bfc6ed;
    padding: 35px;
    font-size: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
col1, col2, col3 = st.columns([4, 1, 1])

with col1:
    st.markdown(
        '<div class="brand">🎓 EduMetrics Pro</div>',
        unsafe_allow_html=True
    )

with col2:
    st.write("🏠 Home")

with col3:
    st.write("📊 Analytics")

# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero">

<h1>Student Performance Analytics Engine</h1>

<p>
Upload your student dataset and instantly analyze marks,
student performance, subject averages, section performance
and top-performing students.
</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# UPLOAD BOX
# =========================================================
st.markdown("""
<div class="upload-box">

<div style="font-size:50px;">☁️</div>

<div class="upload-title">
Drag and drop your student dataset
</div>

<p>Upload CSV or Excel file for instant analysis</p>

<span class="badge">CSV</span>
<span class="badge">XLSX</span>
<span class="badge">XLS</span>

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
# READ FILE
# =========================================================
def read_file(file):

    try:

        if file.name.lower().endswith(".csv"):
            return pd.read_csv(file)

        elif file.name.lower().endswith((".xlsx", ".xls")):
            return pd.read_excel(file)

    except Exception as e:
        st.error(f"❌ File reading error: {e}")
        return None

    return None


# =========================================================
# MAIN ANALYSIS
# =========================================================
if uploaded_file is not None:

    df = read_file(uploaded_file)

    if df is not None:

        # -------------------------------------------------
        # DATASET
        # -------------------------------------------------
        st.subheader("📋 Dataset")

        st.dataframe(
            df,
            use_container_width=True,
            height=350
        )

        # -------------------------------------------------
        # SUBJECTS
        # -------------------------------------------------
        subjects = [
            "Mathematics",
            "Science",
            "English",
            "Hindi",
            "Social Science",
            "Computer"
        ]

        # Only existing columns
        subject_cols = [
            col for col in subjects
            if col in df.columns
        ]

        # -------------------------------------------------
        # NUMERIC CONVERSION
        # -------------------------------------------------
        for col in subject_cols:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        # -------------------------------------------------
        # CHECK SUBJECTS
        # -------------------------------------------------
        if len(subject_cols) == 0:

            st.error(
                "❌ Subject columns not found."
            )

            st.info(
                "Required subjects: Mathematics, Science, "
                "English, Hindi, Social Science, Computer"
            )

        else:

            # -------------------------------------------------
            # TOTAL AND AVERAGE
            # -------------------------------------------------
            df["Total"] = df[subject_cols].sum(
                axis=1,
                skipna=True
            )

            df["Average"] = df[subject_cols].mean(
                axis=1,
                skipna=True
            )

            # =================================================
            # DASHBOARD
            # =================================================
            st.subheader("📊 Student Performance Dashboard")

            c1, c2, c3, c4 = st.columns(4)

            # Total Students
            with c1:
                st.metric(
                    "👨‍🎓 Total Students",
                    len(df)
                )

            # Overall Average
            with c2:
                overall_average = df["Average"].mean()

                st.metric(
                    "📈 Overall Average",
                    f"{overall_average:.2f}"
                )

            # Highest Marks
            with c3:

                highest_marks = df["Total"].max()

                st.metric(
                    "🏆 Highest Total",
                    f"{highest_marks:.0f}"
                )

            # Top Student
            with c4:

                if "Student Name" in df.columns:

                    top_index = df["Total"].idxmax()

                    top_student = df.loc[
                        top_index,
                        "Student Name"
                    ]

                    st.metric(
                        "🥇 Top Student",
                        top_student
                    )

                else:

                    st.metric(
                        "🥇 Top Student",
                        "N/A"
                    )

            # =================================================
            # SUBJECT-WISE ANALYSIS
            # =================================================
            st.subheader("📚 Subject-wise Average")

            subject_average = (
                df[subject_cols]
                .mean()
                .sort_values(ascending=False)
            )

            st.bar_chart(
                subject_average,
                use_container_width=True
            )

            # =================================================
            # TOP 5 STUDENTS
            # =================================================
            st.subheader("🏆 Top 5 Students")

            if "Student Name" in df.columns:

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
                            "Student Name",
                            "Total",
                            "Average"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

            # =================================================
            # SECTION ANALYSIS
            # =================================================
            if "Section" in df.columns:

                st.subheader("📚 Section-wise Analysis")

                section_average = (
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
                    section_average,
                    use_container_width=True
                )

            # =================================================
            # INDIVIDUAL STUDENT
            # =================================================
            if "Student Name" in df.columns:

                st.subheader(
                    "👨‍🎓 Individual Student Performance"
                )

                student_list = (
                    df["Student Name"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                if student_list:

                    selected_student = st.selectbox(
                        "Select Student",
                        student_list
                    )

                    student_data = df[
                        df["Student Name"]
                        == selected_student
                    ].iloc[0]

                    c1, c2 = st.columns(2)

                    with c1:

                        st.metric(
                            "Total Marks",
                            f"{student_data['Total']:.0f}"
                        )

                    with c2:

                        st.metric(
                            "Average",
                            f"{student_data['Average']:.2f}"
                        )

                    # -------------------------------------------------
                    # SELECTED STUDENT SUBJECT MARKS
                    # -------------------------------------------------
                    st.write(
                        "### 📊 Subject-wise Marks"
                    )

                    student_marks = (
                        student_data[subject_cols]
                        .dropna()
                    )

                    st.bar_chart(
                        student_marks,
                        use_container_width=True
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
            csv_data = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Download Analysis CSV",
                data=csv_data,
                file_name="student_analysis.csv",
                mime="text/csv"
            )

else:

    st.info(
        "👆 Please upload a CSV or Excel file to start analysis."
    )


# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class="developer">
<hr>
🎓 EduMetrics Pro<br>
Student Performance Analytics System<br><br>
Developed by <b>Your Name</b>
</div>
""", unsafe_allow_html=True)
