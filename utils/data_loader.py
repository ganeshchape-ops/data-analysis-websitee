"""
Data Loader Module
Handles ingestion of .xlsx, .xls, and .csv files with intelligent column detection,
fuzzy mapping, and format normalization.
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np


# Common aliases for column auto-detection
COMMON_ALIASES = {
    "student_id": [
        r"^id$", r"^student_?id$", r"^roll_?(no|num|number)?$", r"^reg_?(no|num|number)?$",
        r"^admission_?(no|num)?$", r"^adm_?no$", r"^usn$", r"^enrollment_?(no|num)?$"
    ],
    "student_name": [
        r"^name$", r"^student_?name$", r"^full_?name$", r"^candidate_?name$",
        r"^pupil_?name$", r"^first_?name$"
    ],
    "section": [
        r"^section$", r"^sec$", r"^division$", r"^div$", r"^class_?sec$",
        r"^batch$", r"^group$"
    ],
    "gender": [
        r"^gender$", r"^sex$"
    ],
    "attendance": [
        r"^attendance$", r"^attendance_?pct$", r"^attendance_?percentage$",
        r"^att_?%$", r"^presence_?%$"
    ]
}

KNOWN_SUBJECT_PATTERNS = [
    r"math(s|ematics)?", r"phy(sics)?", r"chem(istry)?", r"bio(logy)?",
    r"eng(lish)?", r"comp(uter)?_?(sci|science|app)?", r"cs", r"it",
    r"social_?(sci|studies|science)?", r"hist(ory)?", r"geo(graphy)?",
    r"sci(ence)?", r"acc(ounts|ountancy)?", r"econ(omics)?", r"business_?(studies)?",
    r"sub(ject)?_?[0-9]+", r"paper_?[0-9]+", r"course_?[0-9]+"
]


def load_raw_data(file_path_or_buffer: Any, filename: str) -> pd.DataFrame:
    """
    Loads raw tabular data from .xlsx, .xls, or .csv.
    Handles encoding differences and strip initial whitespace.
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in [".xlsx", ".xlsm"]:
        df = pd.read_excel(file_path_or_buffer, engine="openpyxl")
    elif ext == ".xls":
        try:
            df = pd.read_excel(file_path_or_buffer, engine="xlrd")
        except Exception:
            # Fallback for older or disguised xls files
            df = pd.read_excel(file_path_or_buffer)
    elif ext == ".csv":
        encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252", "iso-8859-1"]
        df = None
        for enc in encodings:
            try:
                if hasattr(file_path_or_buffer, "seek"):
                    file_path_or_buffer.seek(0)
                df = pd.read_csv(file_path_or_buffer, encoding=enc)
                break
            except (UnicodeDecodeError, Exception):
                continue
        if df is None:
            raise ValueError(f"Could not decode CSV file '{filename}' with standard encodings.")
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Please upload an Excel (.xlsx, .xls) or CSV (.csv) file.")

    if df.empty:
        raise ValueError("The uploaded file is empty. Please provide a file with student records.")

    # Drop completely blank rows and columns
    df = df.dropna(how="all").dropna(axis=1, how="all")
    
    # Strip whitespace from column names
    df.columns = [str(c).strip() for c in df.columns]
    
    return df


def _fuzzy_match_column(columns: List[str], regex_patterns: List[str]) -> Optional[str]:
    """Matches a column name against a list of regular expression patterns."""
    for col in columns:
        col_clean = re.sub(r"[_\s\-]+", "_", col.lower().strip())
        for pat in regex_patterns:
            if re.search(pat, col_clean, re.IGNORECASE):
                return col
    return None


def detect_column_mapping(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Intelligently inspects DataFrame headers and data types to suggest
    column mappings for Student ID, Name, Section, Gender, Attendance, and 6 Subjects.
    """
    cols = list(df.columns)
    mapping = {
        "student_id": None,
        "student_name": None,
        "section": None,
        "gender": None,
        "attendance": None,
        "subjects": []
    }
    
    used_cols = set()

    # 1. Match core metadata columns
    for field, patterns in COMMON_ALIASES.items():
        match = _fuzzy_match_column([c for c in cols if c not in used_cols], patterns)
        if match:
            mapping[field] = match
            used_cols.add(match)

    # 2. Detect Subject columns
    # First pass: check for known subject name patterns among remaining columns
    subject_candidates = []
    for col in cols:
        if col in used_cols:
            continue
        col_clean = re.sub(r"[_\s\-]+", "_", col.lower().strip())
        is_subject = any(re.search(pat, col_clean, re.IGNORECASE) for pat in KNOWN_SUBJECT_PATTERNS)
        if is_subject:
            subject_candidates.append(col)
            used_cols.add(col)

    # Second pass: if we have fewer than 6 subjects, inspect remaining numeric-convertible columns
    if len(subject_candidates) < 6:
        for col in cols:
            if col in used_cols:
                continue
            # Check if column is mostly numeric
            numeric_series = pd.to_numeric(df[col], errors="coerce")
            valid_numeric_ratio = numeric_series.notna().sum() / max(len(df), 1)
            # If at least 40% are numeric or convertible, and not a primary text ID
            if valid_numeric_ratio >= 0.40:
                subject_candidates.append(col)
                used_cols.add(col)
            if len(subject_candidates) == 6:
                break

    mapping["subjects"] = subject_candidates

    # Validation checks
    missing_required = []
    if not mapping["student_name"] and not mapping["student_id"]:
        missing_required.append("Student Name or Student ID")
    if not mapping["section"]:
        missing_required.append("Section")
    if len(mapping["subjects"]) == 0:
        missing_required.append("At least 1 Subject column (6 expected)")

    is_valid = len(missing_required) == 0

    return {
        "mapping": mapping,
        "is_valid": is_valid,
        "missing_required": missing_required,
        "detected_subjects_count": len(mapping["subjects"]),
        "all_columns": cols
    }


def apply_column_mapping(df: pd.DataFrame, mapping: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Applies the validated column mapping to produce a standardized DataFrame
    while preserving human-readable subject display names.
    """
    renamed_df = df.copy()
    display_names = {}
    
    rename_dict = {}
    if mapping.get("student_id") and mapping["student_id"] in renamed_df.columns:
        rename_dict[mapping["student_id"]] = "student_id"
    else:
        # Generate synthetic student_id if absent
        renamed_df["student_id"] = [f"STU_{i+1:03d}" for i in range(len(renamed_df))]

    if mapping.get("student_name") and mapping["student_name"] in renamed_df.columns:
        rename_dict[mapping["student_name"]] = "student_name"
    else:
        renamed_df["student_name"] = renamed_df["student_id"]

    if mapping.get("section") and mapping["section"] in renamed_df.columns:
        rename_dict[mapping["section"]] = "section"
    else:
        renamed_df["section"] = "ALL"

    if mapping.get("gender") and mapping["gender"] in renamed_df.columns:
        rename_dict[mapping["gender"]] = "gender"

    if mapping.get("attendance") and mapping["attendance"] in renamed_df.columns:
        rename_dict[mapping["attendance"]] = "attendance"

    # Map subjects
    subjects = mapping.get("subjects", [])
    subject_keys = []
    for i, orig_col in enumerate(subjects):
        std_key = f"subject_{i+1}"
        rename_dict[orig_col] = std_key
        display_names[std_key] = orig_col
        subject_keys.append(std_key)

    renamed_df = renamed_df.rename(columns=rename_dict)
    
    # Store subject metadata in display_names
    display_names["_subject_keys"] = subject_keys
    
    return renamed_df, display_names
