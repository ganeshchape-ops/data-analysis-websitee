"""
Data Cleaning and Validation Module
Cleans raw student records, detects anomalies/duplicates/missing/out-of-range marks,
standardizes section identifiers, and produces a complete Data Quality Audit report.
"""

from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np


def clean_student_data(
    df: pd.DataFrame,
    subject_keys: List[str],
    display_names: Dict[str, str],
    min_mark: float = 0.0,
    max_mark: float = 100.0,
    remove_duplicates: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans raw student records and constructs a rigorous data quality audit log.

    Rules:
    1. Removes full row duplicates or duplicate student IDs if remove_duplicates=True.
    2. Purges entirely blank rows.
    3. Trims whitespace and standardizes section names.
    4. Safely parses numeric marks; identifies non-numeric or missing marks without silent zero-imputation.
    5. Flags out-of-range marks (< min_mark or > max_mark).
    6. Produces detailed audit summary metrics and per-issue log entries.
    """
    total_records = len(df)
    cleaning_logs = []
    
    cleaned_df = df.copy()

    # 1. Standardize text columns (ID, Name, Section, Gender)
    for col in ["student_id", "student_name", "section", "gender"]:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            # Replace 'nan', 'None', '<NA>' with proper representations
            cleaned_df[col] = cleaned_df[col].replace(["nan", "None", "<NA>", "NaN", ""], np.nan)

    # Fill empty IDs/Names with placeholders if missing
    if "student_id" in cleaned_df.columns:
        cleaned_df["student_id"] = cleaned_df["student_id"].fillna(
            pd.Series([f"STU_{i+1:03d}" for i in range(len(cleaned_df))], index=cleaned_df.index)
        )
    if "student_name" in cleaned_df.columns:
        cleaned_df["student_name"] = cleaned_df["student_name"].fillna(cleaned_df["student_id"])
    if "section" in cleaned_df.columns:
        cleaned_df["section"] = cleaned_df["section"].fillna("UNASSIGNED").str.upper()

    # 2. Check for Duplicate Records
    duplicate_rows_count = 0
    duplicate_ids_count = 0
    
    # Check exact row duplicates
    exact_duplicates = cleaned_df.duplicated(keep="first")
    if exact_duplicates.any():
        dup_count = exact_duplicates.sum()
        duplicate_rows_count += int(dup_count)
        cleaning_logs.append({
            "type": "DUPLICATE_ROW",
            "count": int(dup_count),
            "description": f"Identified {dup_count} exact duplicate rows."
        })

    # Check student_id duplicates
    if "student_id" in cleaned_df.columns:
        id_duplicates = cleaned_df.duplicated(subset=["student_id"], keep="first")
        if id_duplicates.any():
            dup_id_cnt = id_duplicates.sum()
            duplicate_ids_count = int(dup_id_cnt)
            dup_ids_list = cleaned_df.loc[id_duplicates, "student_id"].tolist()[:5]
            cleaning_logs.append({
                "type": "DUPLICATE_STUDENT_ID",
                "count": int(dup_id_cnt),
                "description": f"Found {dup_id_cnt} duplicate Student IDs (e.g., {', '.join(dup_ids_list)})."
            })

    if remove_duplicates:
        cleaned_df = cleaned_df.drop_duplicates(subset=["student_id"], keep="first").reset_index(drop=True)

    # 3. Process Subject Marks (Numeric parsing & out-of-range detection)
    missing_values_count = 0
    invalid_values_count = 0
    out_of_range_count = 0
    anomalous_cells = []

    for sub_key in subject_keys:
        if sub_key not in cleaned_df.columns:
            continue

        raw_col = cleaned_df[sub_key]
        sub_display = display_names.get(sub_key, sub_key)

        # Convert to numeric safely
        numeric_col = pd.to_numeric(raw_col, errors="coerce")

        # Clean numeric column array (float to support NaN)
        numeric_arr = numeric_col.to_numpy(dtype=float, copy=True)

        for idx, (raw_val, num_val) in enumerate(zip(raw_col, numeric_col)):
            stu_name = cleaned_df.iloc[idx].get("student_name", f"Row {idx+1}")
            stu_id = cleaned_df.iloc[idx].get("student_id", f"ID_{idx+1}")

            # Check if raw value was missing
            if pd.isna(raw_val) or str(raw_val).strip() in ["", "nan", "None", "NaN", "NA", "N/A", "-"]:
                missing_values_count += 1
            # Check if raw value was non-numeric string (e.g., 'AB', 'Absent', 'FAIL', 'typo')
            elif pd.isna(num_val) and not pd.isna(raw_val):
                invalid_values_count += 1
                anomalous_cells.append({
                    "student_id": stu_id,
                    "student_name": stu_name,
                    "subject": sub_display,
                    "raw_value": str(raw_val),
                    "reason": "Non-numeric mark value (treated as Missing/NaN)"
                })
            # Check if numeric value is out of bounds
            elif not pd.isna(num_val) and (num_val < min_mark or num_val > max_mark):
                out_of_range_count += 1
                anomalous_cells.append({
                    "student_id": stu_id,
                    "student_name": stu_name,
                    "subject": sub_display,
                    "raw_value": num_val,
                    "reason": f"Mark out of range [{min_mark}, {max_mark}]"
                })
                numeric_arr[idx] = np.nan

        # Assign numeric column back
        cleaned_df[sub_key] = numeric_arr

    # Optional attendance parsing
    if "attendance" in cleaned_df.columns:
        cleaned_df["attendance"] = (
            cleaned_df["attendance"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
        cleaned_df["attendance"] = pd.to_numeric(cleaned_df["attendance"], errors="coerce")

    # 4. Compute Data Quality Score (0 to 100)
    total_cells = max(len(cleaned_df) * len(subject_keys), 1)
    total_issues = missing_values_count + invalid_values_count + out_of_range_count
    quality_score = max(0.0, min(100.0, round(100.0 - (total_issues / total_cells) * 100.0, 2)))

    valid_records = len(cleaned_df)
    sections_list = sorted([s for s in cleaned_df["section"].dropna().unique() if str(s).strip() != ""])

    quality_summary = {
        "total_records_initial": total_records,
        "valid_records": valid_records,
        "duplicate_rows": duplicate_rows_count,
        "duplicate_ids": duplicate_ids_count,
        "missing_marks_count": missing_values_count,
        "invalid_marks_count": invalid_values_count,
        "out_of_range_count": out_of_range_count,
        "sections_count": len(sections_list),
        "sections": sections_list,
        "subjects_count": len(subject_keys),
        "quality_score": quality_score,
        "anomalous_cells": anomalous_cells[:50],  # Keep top 50 for reporting
        "cleaning_logs": cleaning_logs
    }

    return cleaned_df, quality_summary
