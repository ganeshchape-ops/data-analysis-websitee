"""
Student Data Analysis Utilities Package
"""

from .data_loader import load_raw_data, detect_column_mapping, apply_column_mapping
from .data_cleaning import clean_student_data
from .analysis import perform_full_analysis
from .insights import generate_automated_insights
from .visualization import generate_all_visualizations, prepare_chartjs_data
from .excel_report import generate_excel_report

__all__ = [
    "load_raw_data",
    "detect_column_mapping",
    "apply_column_mapping",
    "clean_student_data",
    "perform_full_analysis",
    "generate_automated_insights",
    "generate_all_visualizations",
    "prepare_chartjs_data",
    "generate_excel_report",
]
