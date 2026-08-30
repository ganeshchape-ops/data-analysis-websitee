"""
Visualization Engine Module
Generates high-resolution Matplotlib/Seaborn static chart assets (PNG/base64)
and pre-formats JSON datasets for interactive Chart.js web components.
"""

import os
import io
import base64
from typing import Dict, List, Any, Optional
import matplotlib
matplotlib.use("Agg")  # Headless backend for web server safety
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


# Palette & Styling Constants
PRIMARY_COLOR = "#3B82F6"
SUCCESS_COLOR = "#10B981"
WARNING_COLOR = "#F59E0B"
DANGER_COLOR = "#EF4444"
PURPLE_COLOR = "#8B5CF6"
DARK_NAVY = "#1E293B"
GRID_COLOR = "#E2E8F0"

PALETTE_SECTIONS = ["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#06B6D4", "#64748B"]
PALETTE_GRADES = {
    "A+": "#10B981",
    "A":  "#34D399",
    "B":  "#3B82F6",
    "C":  "#60A5FA",
    "D":  "#F59E0B",
    "E":  "#FB923C",
    "F":  "#EF4444"
}


def _setup_figure(figsize=(9, 5.5)):
    """Initializes a standardized figure with styling."""
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#F8FAFC")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CBD5E1")
    ax.spines["bottom"].set_color("#CBD5E1")
    ax.yaxis.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    return fig, ax


def _fig_to_base64(fig) -> str:
    """Converts a Matplotlib figure into a base64 encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150, facecolor=fig.get_facecolor())
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close(fig)
    return img_b64


def generate_section_avg_chart(sec_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """1. Section-wise Average Marks Bar Chart"""
    fig, ax = _setup_figure((8, 5))
    bars = ax.bar(
        sec_df["section"].astype(str),
        sec_df["average_percentage"],
        color=PALETTE_SECTIONS[:len(sec_df)],
        width=0.55,
        edgecolor="#1E293B",
        linewidth=0.8,
        zorder=3
    )
    ax.set_title("Section-Wise Average Performance (%)", fontsize=13, fontweight="bold", pad=15, color=DARK_NAVY)
    ax.set_xlabel("Section", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylabel("Average Score (%)", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylim(0, 105)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=DARK_NAVY
        )

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=200)

    return _fig_to_base64(fig)


def generate_subject_avg_chart(sub_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """2. Subject-wise Average Marks Bar Chart"""
    fig, ax = _setup_figure((9, 5))
    palette = sns.color_palette("viridis", len(sub_df))
    bars = ax.bar(
        sub_df["subject_name"].astype(str),
        sub_df["average_marks"],
        color=palette,
        width=0.55,
        edgecolor="#1E293B",
        linewidth=0.8,
        zorder=3
    )
    ax.set_title("Subject-Wise Average Marks", fontsize=13, fontweight="bold", pad=15, color=DARK_NAVY)
    ax.set_xlabel("Subject", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylabel("Average Marks (out of 100)", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylim(0, 105)
    plt.xticks(rotation=20, ha="right", fontsize=9.5)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=DARK_NAVY
        )

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=200)

    return _fig_to_base64(fig)


def generate_section_pass_chart(sec_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """3. Section-wise Pass Percentage Bar Chart"""
    fig, ax = _setup_figure((8, 5))
    bars = ax.bar(
        sec_df["section"].astype(str),
        sec_df["pass_percentage"],
        color=SUCCESS_COLOR,
        width=0.55,
        edgecolor="#065F46",
        linewidth=0.8,
        zorder=3
    )
    ax.set_title("Section-Wise Pass Rate (%)", fontsize=13, fontweight="bold", pad=15, color=DARK_NAVY)
    ax.set_xlabel("Section", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylabel("Pass Rate (%)", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylim(0, 105)
    ax.axhline(100, color="#94A3B8", linestyle=":", alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=DARK_NAVY
        )

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=200)

    return _fig_to_base64(fig)


def generate_subject_pass_chart(sub_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """4. Subject-wise Pass Percentage Bar Chart"""
    fig, ax = _setup_figure((9, 5))
    bars = ax.bar(
        sub_df["subject_name"].astype(str),
        sub_df["pass_percentage"],
        color=PURPLE_COLOR,
        width=0.55,
        edgecolor="#4C1D95",
        linewidth=0.8,
        zorder=3
    )
    ax.set_title("Subject-Wise Pass Rate (%)", fontsize=13, fontweight="bold", pad=15, color=DARK_NAVY)
    ax.set_xlabel("Subject", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylabel("Pass Rate (%)", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylim(0, 105)
    plt.xticks(rotation=20, ha="right", fontsize=9.5)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=DARK_NAVY
        )

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=200)

    return _fig_to_base64(fig)


def generate_section_subject_heatmap(avg_matrix_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """5. Section vs Subject Performance Heatmap"""
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    fig.patch.set_facecolor("#FFFFFF")
    
    matrix_data = avg_matrix_df.set_index("section")
    
    sns.heatmap(
        matrix_data,
        annot=True,
        fmt=".1f",
        cmap="YlGnBu",
        linewidths=1.2,
        linecolor="#FFFFFF",
        cbar_kws={"label": "Average Score", "shrink": 0.8},
        ax=ax,
        vmin=40,
        vmax=100
    )
    ax.set_title("Section × Subject Average Performance Heatmap", fontsize=13, fontweight="bold", pad=15, color=DARK_NAVY)
    ax.set_xlabel("Subject", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylabel("Section", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    plt.xticks(rotation=20, ha="right", fontsize=9.5)
    plt.yticks(rotation=0, fontsize=10)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=200)

    return _fig_to_base64(fig)


def generate_score_distribution_chart(student_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """6. Student Performance Score Distribution Histogram + KDE"""
    fig, ax = _setup_figure((8.5, 5))
    scores = student_df["percentage"].dropna()
    
    sns.histplot(
        scores,
        kde=True,
        bins=10,
        color=PRIMARY_COLOR,
        edgecolor="#1E3A8A",
        linewidth=1,
        ax=ax,
        stat="count",
        alpha=0.7
    )
    
    # Add vertical mean line
    mean_val = scores.mean()
    ax.axvline(mean_val, color=DANGER_COLOR, linestyle="--", linewidth=1.5, label=f"Cohort Mean: {mean_val:.1f}%")
    
    ax.set_title("Student Score Distribution (Overall %)", fontsize=13, fontweight="bold", pad=15, color=DARK_NAVY)
    ax.set_xlabel("Percentage (%)", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylabel("Student Count", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.legend(frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1")

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=200)

    return _fig_to_base64(fig)


def generate_grade_distribution_chart(student_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """7. Grade Distribution Donut/Bar Chart"""
    fig, ax = _setup_figure((7.5, 5))
    grade_order = ["A+", "A", "B", "C", "D", "E", "F"]
    grade_counts = student_df["grade"].value_counts().reindex(grade_order, fill_value=0)
    
    colors = [PALETTE_GRADES.get(g, "#64748B") for g in grade_counts.index]
    
    bars = ax.bar(
        grade_counts.index,
        grade_counts.values,
        color=colors,
        width=0.55,
        edgecolor="#1E293B",
        linewidth=0.8,
        zorder=3
    )
    ax.set_title("Cohort Grade Distribution", fontsize=13, fontweight="bold", pad=15, color=DARK_NAVY)
    ax.set_xlabel("Grade", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_ylabel("Student Count", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.annotate(
                f"{int(height)}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=DARK_NAVY
            )

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=200)

    return _fig_to_base64(fig)


def generate_top_students_chart(top_10_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """8. Top 10 Students Horizontal Bar Chart"""
    fig, ax = _setup_figure((9, 5.5))
    
    # Invert to have Rank 1 at top
    df_sorted = top_10_df.sort_values(by="percentage", ascending=True)
    
    labels = [f"#{row['rank']} {row['student_name']} ({row['section']})" for _, row in df_sorted.iterrows()]
    y_pos = np.arange(len(df_sorted))
    
    palette = sns.color_palette("crest", len(df_sorted))
    bars = ax.barh(
        y_pos,
        df_sorted["percentage"],
        color=palette,
        height=0.6,
        edgecolor="#1E293B",
        linewidth=0.8,
        zorder=3
    )
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9.5, fontweight="normal", color=DARK_NAVY)
    ax.set_title("Top 10 High Achievers (Overall %)", fontsize=13, fontweight="bold", pad=15, color=DARK_NAVY)
    ax.set_xlabel("Percentage (%)", fontsize=11, fontweight="bold", color=DARK_NAVY, labelpad=8)
    ax.set_xlim(0, 105)
    ax.xaxis.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)
    ax.yaxis.grid(False)

    for bar in bars:
        width = bar.get_width()
        ax.annotate(
            f"{width:.1f}%",
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left", va="center",
            fontsize=9.5, fontweight="bold", color=DARK_NAVY
        )

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=200)

    return _fig_to_base64(fig)


def generate_all_visualizations(
    analysis_results: Dict[str, Any],
    output_dir: Optional[str] = None
) -> Dict[str, str]:
    """
    Renders all 8 publication-grade charts and returns a dictionary of base64 PNG strings.
    If output_dir is provided, also saves them to disk.
    """
    sec_df = analysis_results["section_summary_df"]
    sub_df = analysis_results["subject_summary_df"]
    avg_matrix_df = analysis_results["average_matrix_df"]
    student_df = analysis_results["student_df"]
    top_10_df = analysis_results["top_10_df"]

    charts_b64 = {}

    def get_path(name: str) -> Optional[str]:
        return os.path.join(output_dir, f"{name}.png") if output_dir else None

    charts_b64["section_avg"] = generate_section_avg_chart(sec_df, get_path("1_section_avg"))
    charts_b64["subject_avg"] = generate_subject_avg_chart(sub_df, get_path("2_subject_avg"))
    charts_b64["section_pass"] = generate_section_pass_chart(sec_df, get_path("3_section_pass"))
    charts_b64["subject_pass"] = generate_subject_pass_chart(sub_df, get_path("4_subject_pass"))
    charts_b64["section_subject_heatmap"] = generate_section_subject_heatmap(avg_matrix_df, get_path("5_section_subject_heatmap"))
    charts_b64["score_dist"] = generate_score_distribution_chart(student_df, get_path("6_score_distribution"))
    charts_b64["grade_dist"] = generate_grade_distribution_chart(student_df, get_path("7_grade_distribution"))
    charts_b64["top_students"] = generate_top_students_chart(top_10_df, get_path("8_top_students"))

    return charts_b64


def prepare_chartjs_data(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pre-formats data into clean JSON structures ready for Chart.js rendering on the web dashboard.
    """
    sec_df = analysis_results["section_summary_df"]
    sub_df = analysis_results["subject_summary_df"]
    student_df = analysis_results["student_df"]
    top_10_df = analysis_results["top_10_df"]

    # Grade distribution
    grade_order = ["A+", "A", "B", "C", "D", "E", "F"]
    grade_counts = student_df["grade"].value_counts().reindex(grade_order, fill_value=0)

    # Top 10
    top_sorted = top_10_df.sort_values(by="percentage", ascending=False)

    return {
        "section_labels": sec_df["section"].astype(str).tolist(),
        "section_avg": sec_df["average_percentage"].tolist(),
        "section_pass": sec_df["pass_percentage"].tolist(),
        "subject_labels": sub_df["subject_name"].tolist(),
        "subject_avg": sub_df["average_marks"].tolist(),
        "subject_pass": sub_df["pass_percentage"].tolist(),
        "grade_labels": grade_order,
        "grade_counts": [int(v) for v in grade_counts.values],
        "top_labels": [f"#{r['rank']} {r['student_name']} ({r['section']})" for _, r in top_sorted.iterrows()],
        "top_percentages": top_sorted["percentage"].tolist()
    }
