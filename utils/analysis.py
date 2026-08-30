"""
Statistical Analysis Module
Computes mathematical metrics across Overall Cohort, Section-wise, Subject-wise (6 Subjects),
Section x Subject Matrix, and Student-level Performance with dynamic grading and ranking.
"""

from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from scipy import stats


# Default Grading Thresholds
DEFAULT_GRADE_SCALE = [
    {"grade": "A+", "min": 90.0, "max": 100.0, "label": "Outstanding"},
    {"grade": "A",  "min": 80.0, "max": 89.99, "label": "Excellent"},
    {"grade": "B",  "min": 70.0, "max": 79.99, "label": "Very Good"},
    {"grade": "C",  "min": 60.0, "max": 69.99, "label": "Good"},
    {"grade": "D",  "min": 50.0, "max": 59.99, "label": "Satisfactory"},
    {"grade": "E",  "min": 40.0, "max": 49.99, "label": "Pass"},
    {"grade": "F",  "min": 0.0,  "max": 39.99, "label": "Fail"}
]

DEFAULT_PASS_MARK = 40.0
DEFAULT_MAX_SUBJECT_MARK = 100.0


def calculate_grade(percentage: float, grade_scale: Optional[List[Dict[str, Any]]] = None) -> str:
    """Assigns letter grade based on percentage score and configurable thresholds."""
    if pd.isna(percentage):
        return "N/A"
    scale = grade_scale or DEFAULT_GRADE_SCALE
    for bracket in scale:
        if percentage >= bracket["min"] and percentage <= bracket["max"] + 0.001:
            return bracket["grade"]
    if percentage >= 90.0:
        return "A+"
    return "F"


def perform_student_level_analysis(
    df: pd.DataFrame,
    subject_keys: List[str],
    display_names: Dict[str, str],
    pass_mark: float = DEFAULT_PASS_MARK,
    max_subject_mark: float = DEFAULT_MAX_SUBJECT_MARK,
    grade_scale: Optional[List[Dict[str, Any]]] = None
) -> pd.DataFrame:
    """
    Computes student-level metrics:
    - total_marks: Sum of non-missing subject marks
    - valid_subjects_count: Count of non-missing marks
    - average_marks: total_marks / valid_subjects_count
    - percentage: (average_marks / max_subject_mark) * 100
    - failed_subjects_count: Count of subject marks strictly below pass_mark
    - pass_status: 'Pass' if failed_subjects_count == 0 else 'Fail'
    - grade: Assigned letter grade
    - rank: Standard competition rank (1, 2, 2, 4...) based on percentage descending
    """
    analyzed_df = df.copy()

    # Subject scores sub-frame
    sub_df = analyzed_df[subject_keys]

    # Calculate student aggregations strictly without assuming missing == 0
    valid_sub_counts = sub_df.notna().sum(axis=1)
    totals = sub_df.sum(axis=1, min_count=1)
    averages = totals / valid_sub_counts.replace(0, np.nan)
    percentages = (averages / max_subject_mark) * 100.0

    # Count subject failures
    subject_failures = (sub_df < pass_mark).sum(axis=1)
    pass_status = np.where(subject_failures == 0, "Pass", "Fail")

    analyzed_df["valid_subjects"] = valid_sub_counts
    analyzed_df["total_marks"] = totals.round(2)
    analyzed_df["average_marks"] = averages.round(2)
    analyzed_df["percentage"] = percentages.round(2)
    analyzed_df["failed_subjects_count"] = subject_failures
    analyzed_df["pass_status"] = pass_status

    # Assign grades
    analyzed_df["grade"] = analyzed_df["percentage"].apply(lambda p: calculate_grade(p, grade_scale))

    # Calculate Rank (Min ranking, highest percentage gets 1)
    analyzed_df["rank"] = (
        analyzed_df["percentage"]
        .rank(ascending=False, method="min")
        .fillna(len(analyzed_df))
        .astype(int)
    )

    return analyzed_df


def perform_overall_analysis(
    analyzed_df: pd.DataFrame,
    subject_keys: List[str]
) -> Dict[str, Any]:
    """
    Calculates statistical parameters for the whole student cohort.
    """
    pct_series = analyzed_df["percentage"].dropna()
    total_students = len(analyzed_df)
    
    if pct_series.empty or total_students == 0:
        return {}

    pass_count = int((analyzed_df["pass_status"] == "Pass").sum())
    fail_count = total_students - pass_count
    pass_pct = round((pass_count / total_students) * 100.0, 2)
    fail_pct = round((fail_count / total_students) * 100.0, 2)

    # Compute mode
    try:
        mode_res = stats.mode(pct_series, keepdims=False)
        mode_val = round(float(getattr(mode_res, "mode", mode_res[0])), 2)
    except Exception:
        mode_val = round(float(pct_series.mode().iloc[0]), 2) if not pct_series.mode().empty else None

    # Grade distribution
    grade_dist = analyzed_df["grade"].value_counts().to_dict()

    overall_stats = {
        "total_students": total_students,
        "valid_students_count": int(pct_series.count()),
        "average_marks": round(float(analyzed_df["average_marks"].mean()), 2),
        "overall_percentage": round(float(pct_series.mean()), 2),
        "median_percentage": round(float(pct_series.median()), 2),
        "mode_percentage": mode_val,
        "highest_percentage": round(float(pct_series.max()), 2),
        "lowest_percentage": round(float(pct_series.min()), 2),
        "highest_total_marks": round(float(analyzed_df["total_marks"].max()), 2),
        "lowest_total_marks": round(float(analyzed_df["total_marks"].min()), 2),
        "std_dev": round(float(pct_series.std(ddof=1) if len(pct_series) > 1 else 0.0), 2),
        "variance": round(float(pct_series.var(ddof=1) if len(pct_series) > 1 else 0.0), 2),
        "range": round(float(pct_series.max() - pct_series.min()), 2),
        "iqr": round(float(pct_series.quantile(0.75) - pct_series.quantile(0.25)), 2),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_percentage": pass_pct,
        "fail_percentage": fail_pct,
        "grade_distribution": grade_dist,
    }

    return overall_stats


def perform_section_analysis(
    analyzed_df: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Computes section-wise metrics and automatically identifies top/bottom benchmarks.
    """
    sections = sorted(analyzed_df["section"].unique())
    sec_records = []

    for sec in sections:
        sec_df = analyzed_df[analyzed_df["section"] == sec]
        sec_size = len(sec_df)
        pct_series = sec_df["percentage"].dropna()

        pass_cnt = int((sec_df["pass_status"] == "Pass").sum())
        fail_cnt = sec_size - pass_cnt
        pass_rate = round((pass_cnt / max(sec_size, 1)) * 100.0, 2)

        sec_records.append({
            "section": sec,
            "students_count": sec_size,
            "total_marks_sum": round(float(sec_df["total_marks"].sum()), 2),
            "average_marks": round(float(sec_df["average_marks"].mean()), 2),
            "median_marks": round(float(sec_df["average_marks"].median()), 2),
            "average_percentage": round(float(pct_series.mean()), 2),
            "highest_marks": round(float(sec_df["total_marks"].max()), 2),
            "lowest_marks": round(float(sec_df["total_marks"].min()), 2),
            "highest_percentage": round(float(pct_series.max()), 2),
            "lowest_percentage": round(float(pct_series.min()), 2),
            "pass_count": pass_cnt,
            "fail_count": fail_cnt,
            "pass_percentage": pass_rate,
            "std_dev": round(float(pct_series.std(ddof=1) if len(pct_series) > 1 else 0.0), 2)
        })

    sec_summary_df = pd.DataFrame(sec_records)

    # Automated Section Benchmarks
    if not sec_summary_df.empty:
        best_perf_sec = sec_summary_df.loc[sec_summary_df["average_percentage"].idxmax()]["section"]
        lowest_perf_sec = sec_summary_df.loc[sec_summary_df["average_percentage"].idxmin()]["section"]
        highest_pass_sec = sec_summary_df.loc[sec_summary_df["pass_percentage"].idxmax()]["section"]
        lowest_pass_sec = sec_summary_df.loc[sec_summary_df["pass_percentage"].idxmin()]["section"]
        most_consistent_sec = sec_summary_df.loc[sec_summary_df["std_dev"].idxmin()]["section"]
        most_volatile_sec = sec_summary_df.loc[sec_summary_df["std_dev"].idxmax()]["section"]

        sec_highlights = {
            "best_performing_section": best_perf_sec,
            "lowest_performing_section": lowest_perf_sec,
            "highest_pass_rate_section": highest_pass_sec,
            "lowest_pass_rate_section": lowest_pass_sec,
            "most_consistent_section": most_consistent_sec,
            "most_volatile_section": most_volatile_sec
        }
    else:
        sec_highlights = {}

    return sec_summary_df, sec_highlights


def perform_subject_analysis(
    analyzed_df: pd.DataFrame,
    subject_keys: List[str],
    display_names: Dict[str, str],
    pass_mark: float = DEFAULT_PASS_MARK,
    max_subject_mark: float = DEFAULT_MAX_SUBJECT_MARK
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Analyzes each of the 6 subjects individually.
    """
    sub_records = []

    for sub_key in subject_keys:
        if sub_key not in analyzed_df.columns:
            continue
        
        series = analyzed_df[sub_key].dropna()
        valid_cnt = int(series.count())
        sub_display = display_names.get(sub_key, sub_key)

        if valid_cnt > 0:
            avg_score = round(float(series.mean()), 2)
            med_score = round(float(series.median()), 2)
            max_score = round(float(series.max()), 2)
            min_score = round(float(series.min()), 2)
            std_score = round(float(series.std(ddof=1) if valid_cnt > 1 else 0.0), 2)
            pass_cnt = int((series >= pass_mark).sum())
            fail_cnt = valid_cnt - pass_cnt
            pass_pct = round((pass_cnt / valid_cnt) * 100.0, 2)
            fail_pct = round((fail_cnt / valid_cnt) * 100.0, 2)
            perf_pct = round((avg_score / max_subject_mark) * 100.0, 2)
        else:
            avg_score = med_score = max_score = min_score = std_score = 0.0
            pass_cnt = fail_cnt = pass_pct = fail_pct = perf_pct = 0.0

        sub_records.append({
            "subject_key": sub_key,
            "subject_name": sub_display,
            "valid_students": valid_cnt,
            "average_marks": avg_score,
            "median_marks": med_score,
            "maximum_marks": max_score,
            "minimum_marks": min_score,
            "std_dev": std_score,
            "pass_count": pass_cnt,
            "fail_count": fail_cnt,
            "pass_percentage": pass_pct,
            "fail_percentage": fail_pct,
            "performance_percentage": perf_pct
        })

    sub_summary_df = pd.DataFrame(sub_records)

    # Highlights
    if not sub_summary_df.empty:
        strongest_sub = sub_summary_df.loc[sub_summary_df["average_marks"].idxmax()]["subject_name"]
        weakest_sub = sub_summary_df.loc[sub_summary_df["average_marks"].idxmin()]["subject_name"]
        highest_pass_sub = sub_summary_df.loc[sub_summary_df["pass_percentage"].idxmax()]["subject_name"]
        lowest_pass_sub = sub_summary_df.loc[sub_summary_df["pass_percentage"].idxmin()]["subject_name"]

        sub_highlights = {
            "strongest_subject": strongest_sub,
            "weakest_subject": weakest_sub,
            "highest_pass_rate_subject": highest_pass_sub,
            "lowest_pass_rate_subject": lowest_pass_sub
        }
    else:
        sub_highlights = {}

    return sub_summary_df, sub_highlights


def perform_section_subject_matrix(
    analyzed_df: pd.DataFrame,
    subject_keys: List[str],
    display_names: Dict[str, str],
    pass_mark: float = DEFAULT_PASS_MARK
) -> Dict[str, Any]:
    """
    Creates a Section x Subject average score matrix, pass rate matrix,
    and identifies section-subject cross insights.
    """
    sections = sorted(analyzed_df["section"].unique())
    
    # 1. Average marks matrix
    avg_matrix_data = []
    pass_matrix_data = []

    for sec in sections:
        sec_df = analyzed_df[analyzed_df["section"] == sec]
        row_avg = {"section": sec}
        row_pass = {"section": sec}
        for sub_key in subject_keys:
            sub_display = display_names.get(sub_key, sub_key)
            series = sec_df[sub_key].dropna()
            if not series.empty:
                row_avg[sub_display] = round(float(series.mean()), 2)
                p_cnt = (series >= pass_mark).sum()
                row_pass[sub_display] = round((p_cnt / len(series)) * 100.0, 2)
            else:
                row_avg[sub_display] = None
                row_pass[sub_display] = None
        avg_matrix_data.append(row_avg)
        pass_matrix_data.append(row_pass)

    avg_matrix_df = pd.DataFrame(avg_matrix_data)
    pass_matrix_df = pd.DataFrame(pass_matrix_data)

    # 2. Derive cross insights
    # Strongest/weakest subject per section
    sec_insights = {}
    for sec in sections:
        sec_row = avg_matrix_df[avg_matrix_df["section"] == sec].drop(columns=["section"]).iloc[0]
        valid_scores = sec_row.dropna()
        if not valid_scores.empty:
            sec_insights[sec] = {
                "strongest_subject": valid_scores.idxmax(),
                "strongest_avg": float(valid_scores.max()),
                "weakest_subject": valid_scores.idxmin(),
                "weakest_avg": float(valid_scores.min())
            }

    # Best/lowest section per subject
    sub_insights = {}
    subject_cols = [display_names.get(sk, sk) for sk in subject_keys]
    for sub_name in subject_cols:
        if sub_name in avg_matrix_df.columns:
            sub_col = avg_matrix_df.set_index("section")[sub_name].dropna()
            if not sub_col.empty:
                sub_insights[sub_name] = {
                    "best_section": sub_col.idxmax(),
                    "best_avg": float(sub_col.max()),
                    "lowest_section": sub_col.idxmin(),
                    "lowest_avg": float(sub_col.min())
                }

    return {
        "average_matrix_df": avg_matrix_df,
        "pass_matrix_df": pass_matrix_df,
        "section_subject_insights": sec_insights,
        "subject_section_insights": sub_insights
    }


def perform_full_analysis(
    df: pd.DataFrame,
    subject_keys: List[str],
    display_names: Dict[str, str],
    pass_mark: float = DEFAULT_PASS_MARK,
    max_subject_mark: float = DEFAULT_MAX_SUBJECT_MARK,
    grade_scale: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Orchestrates the entire analytical pipeline.
    Returns analyzed student roster, overall stats, section breakdown,
    subject breakdown, section x subject matrices, and leaderboards.
    """
    # 1. Student-level calculation
    student_df = perform_student_level_analysis(
        df=df,
        subject_keys=subject_keys,
        display_names=display_names,
        pass_mark=pass_mark,
        max_subject_mark=max_subject_mark,
        grade_scale=grade_scale
    )

    # 2. Overall cohort stats
    overall_stats = perform_overall_analysis(student_df, subject_keys)

    # 3. Section-wise analysis
    section_summary_df, section_highlights = perform_section_analysis(student_df)

    # 4. Subject-wise analysis (6 subjects)
    subject_summary_df, subject_highlights = perform_subject_analysis(
        analyzed_df=student_df,
        subject_keys=subject_keys,
        display_names=display_names,
        pass_mark=pass_mark,
        max_subject_mark=max_subject_mark
    )

    # 5. Section x Subject matrix
    matrix_results = perform_section_subject_matrix(
        analyzed_df=student_df,
        subject_keys=subject_keys,
        display_names=display_names,
        pass_mark=pass_mark
    )

    # 6. Top 10 Students Leaderboard
    top_10_df = (
        student_df.sort_values(by=["percentage", "total_marks"], ascending=[False, False])
        .head(10)[["rank", "student_id", "student_name", "section", "total_marks", "average_marks", "percentage", "grade"]]
        .reset_index(drop=True)
    )

    # 7. Students Requiring Academic Attention / At-Risk
    at_risk_df = (
        student_df[
            (student_df["pass_status"] == "Fail") |
            (student_df["failed_subjects_count"] > 0) |
            (student_df["percentage"] < 50.0)
        ]
        .sort_values(by=["percentage", "failed_subjects_count"], ascending=[True, False])
        [["rank", "student_id", "student_name", "section", "total_marks", "percentage", "failed_subjects_count", "grade", "pass_status"]]
        .reset_index(drop=True)
    )

    return {
        "student_df": student_df,
        "overall_stats": overall_stats,
        "section_summary_df": section_summary_df,
        "section_highlights": section_highlights,
        "subject_summary_df": subject_summary_df,
        "subject_highlights": subject_highlights,
        "average_matrix_df": matrix_results["average_matrix_df"],
        "pass_matrix_df": matrix_results["pass_matrix_df"],
        "section_subject_insights": matrix_results["section_subject_insights"],
        "subject_section_insights": matrix_results["subject_section_insights"],
        "top_10_df": top_10_df,
        "at_risk_df": at_risk_df,
        "subject_keys": subject_keys,
        "display_names": display_names
    }
