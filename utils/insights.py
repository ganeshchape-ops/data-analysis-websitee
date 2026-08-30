"""
Automated Insights Generator Module
Produces 100% mathematically grounded, factual insights and executive recommendations
based on actual cohort performance, section variances, and subject-level trends.
"""

from typing import Dict, List, Any
import pandas as pd


def generate_automated_insights(analysis_results: Dict[str, Any], quality_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes analysis outputs into categorized executive insights.
    Categories:
    - Executive Summary
    - Section Performance Benchmarks
    - Subject Performance & Difficulty Trends
    - Cross-Section Subject Findings
    - Student Performance & Risk Alerts
    - Data Quality & Integrity Notice
    - Actionable Academic Recommendations
    """
    overall = analysis_results.get("overall_stats", {})
    sec_highlights = analysis_results.get("section_highlights", {})
    sub_highlights = analysis_results.get("subject_highlights", {})
    sec_df = analysis_results.get("section_summary_df", pd.DataFrame())
    sub_df = analysis_results.get("subject_summary_df", pd.DataFrame())
    sec_sub_insights = analysis_results.get("section_subject_insights", {})
    sub_sec_insights = analysis_results.get("subject_section_insights", {})
    top_10 = analysis_results.get("top_10_df", pd.DataFrame())
    at_risk = analysis_results.get("at_risk_df", pd.DataFrame())

    insights = {
        "executive_summary": [],
        "section_insights": [],
        "subject_insights": [],
        "cross_matrix_insights": [],
        "student_alerts": [],
        "data_quality_insights": [],
        "recommendations": []
    }

    # 1. Executive Summary Points
    total_students = overall.get("total_students", 0)
    avg_pct = overall.get("overall_percentage", 0.0)
    pass_pct = overall.get("pass_percentage", 0.0)
    
    insights["executive_summary"].append(
        f"The cohort consists of {total_students} students evaluated across {len(sub_df)} subjects, "
        f"achieving an overall average score of {avg_pct}% and a cumulative pass rate of {pass_pct}%."
    )
    
    if "best_performing_section" in sec_highlights:
        best_sec = sec_highlights["best_performing_section"]
        best_sec_row = sec_df[sec_df["section"] == best_sec].iloc[0] if not sec_df.empty else None
        if best_sec_row is not None:
            insights["executive_summary"].append(
                f"Section '{best_sec}' ranks as the top-performing cohort with an average score of {best_sec_row['average_percentage']}% "
                f"and a pass rate of {best_sec_row['pass_percentage']}%."
            )

    if "strongest_subject" in sub_highlights and "weakest_subject" in sub_highlights:
        insights["executive_summary"].append(
            f"Cohort subject performance is led by '{sub_highlights['strongest_subject']}', "
            f"while '{sub_highlights['weakest_subject']}' exhibited the lowest average score."
        )

    # 2. Section Performance Insights
    if not sec_df.empty:
        best_sec = sec_highlights.get("best_performing_section")
        low_sec = sec_highlights.get("lowest_performing_section")
        best_pass_sec = sec_highlights.get("highest_pass_rate_section")
        low_pass_sec = sec_highlights.get("lowest_pass_rate_section")
        consistent_sec = sec_highlights.get("most_consistent_section")
        volatile_sec = sec_highlights.get("most_volatile_section")

        insights["section_insights"].append(
            f"Top Section: Section '{best_sec}' achieved the highest average percentage."
        )
        if best_sec != low_sec:
            insights["section_insights"].append(
                f"Lowest Section: Section '{low_sec}' logged the lowest overall mean score."
            )
        insights["section_insights"].append(
            f"Pass Rate Spread: Section '{best_pass_sec}' recorded the highest pass rate, whereas Section '{low_pass_sec}' recorded the lowest."
        )
        if consistent_sec:
            insights["section_insights"].append(
                f"Consistency Index: Section '{consistent_sec}' demonstrated the lowest score dispersion (highest consistency), "
                f"while Section '{volatile_sec}' exhibited the highest score variance."
            )

    # 3. Subject-wise Insights
    if not sub_df.empty:
        for _, row in sub_df.iterrows():
            sub_name = row["subject_name"]
            avg_m = row["average_marks"]
            pass_r = row["pass_percentage"]
            fail_cnt = int(row["fail_count"])
            if pass_r < 75.0:
                insights["subject_insights"].append(
                    f"Subject Alert: '{sub_name}' has a lower pass rate ({pass_r}%) with {fail_cnt} students failing to meet the minimum benchmark."
                )
            elif pass_r >= 90.0:
                insights["subject_insights"].append(
                    f"High Mastery: '{sub_name}' shows strong cohort mastery with a {pass_r}% pass rate (average score: {avg_m})."
                )

    # 4. Cross Section-Subject Matrix Insights
    if sec_sub_insights:
        for sec, data in sec_sub_insights.items():
            insights["cross_matrix_insights"].append(
                f"Section {sec}: Strongest in '{data['strongest_subject']}' (avg {data['strongest_avg']:.1f}), "
                f"needs focus in '{data['weakest_subject']}' (avg {data['weakest_avg']:.1f})."
            )

    # 5. Student Alerts
    at_risk_count = len(at_risk)
    if at_risk_count > 0:
        insights["student_alerts"].append(
            f"Academic Intervention Required: {at_risk_count} student(s) ({at_risk_count/max(total_students, 1)*100:.1f}% of cohort) "
            f"have failed one or more subjects or scored below 50.0% overall."
        )
    else:
        insights["student_alerts"].append("All students successfully met or exceeded baseline academic passing criteria.")

    if not top_10.empty:
        valedictorian = top_10.iloc[0]
        insights["student_alerts"].append(
            f"Top Rank 1: {valedictorian['student_name']} (Section {valedictorian['section']}) "
            f"secured highest honors with a score of {valedictorian['percentage']}% ({valedictorian['grade']})."
        )

    # 6. Data Quality Insights
    dq_score = quality_summary.get("quality_score", 100.0)
    dup_rows = quality_summary.get("duplicate_rows", 0)
    missing_cnt = quality_summary.get("missing_marks_count", 0)
    invalid_cnt = quality_summary.get("invalid_marks_count", 0)
    out_of_range = quality_summary.get("out_of_range_count", 0)

    insights["data_quality_insights"].append(
        f"Data Health Score: {dq_score}/100. Audit processed {quality_summary.get('valid_records', 0)} clean records."
    )
    if dup_rows > 0:
        insights["data_quality_insights"].append(f"Purged {dup_rows} duplicate record(s) during preprocessing.")
    if missing_cnt > 0:
        insights["data_quality_insights"].append(f"Detected {missing_cnt} missing subject mark entry/entries.")
    if invalid_cnt > 0 or out_of_range > 0:
        insights["data_quality_insights"].append(
            f"Flagged {invalid_cnt} non-numeric mark(s) and {out_of_range} out-of-range mark(s)."
        )

    # 7. Actionable Recommendations
    if "weakest_subject" in sub_highlights:
        insights["recommendations"].append(
            f"Conduct targeted review sessions and remedial tutorials for '{sub_highlights['weakest_subject']}'."
        )
    if "lowest_performing_section" in sec_highlights:
        insights["recommendations"].append(
            f"Investigate section-specific learning impediments in Section '{sec_highlights['lowest_performing_section']}' and align curriculum delivery with Section '{sec_highlights.get('best_performing_section')}'."
        )
    if at_risk_count > 0:
        insights["recommendations"].append(
            "Schedule personalized 1-on-1 academic mentorship for the identified At-Risk student roster."
        )
    insights["recommendations"].append(
        "Recognize and reward Top 10 high-achieving students to foster academic motivation across sections."
    )

    return insights
