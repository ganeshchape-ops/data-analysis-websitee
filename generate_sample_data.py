"""
Sample Data Generator
Creates realistic clean and edge-case student datasets for demonstration and testing.
"""

import os
import random
import pandas as pd
import numpy as np


def generate_sample_datasets():
    os.makedirs("data", exist_ok=True)
    random.seed(42)
    np.random.seed(42)

    first_names_m = ["James", "John", "Robert", "Michael", "David", "William", "Richard", "Joseph", "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kevin"]
    first_names_f = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]

    sections = ["Section A", "Section B", "Section C", "Section D"]
    
    # 1. Clean Dataset (120 students)
    records = []
    student_id_counter = 101

    for sec in sections:
        # Base section performance offset
        if sec == "Section A":
            sec_offset = 6.0
        elif sec == "Section B":
            sec_offset = 2.0
        elif sec == "Section C":
            sec_offset = -3.0
        else:
            sec_offset = -6.0

        for _ in range(30):
            gender = "Male" if random.random() > 0.5 else "Female"
            fname = random.choice(first_names_m if gender == "Male" else first_names_f)
            lname = random.choice(last_names)
            name = f"{fname} {lname}"
            stu_id = f"STU-{student_id_counter}"
            student_id_counter += 1

            # Base capability
            student_tier = np.random.choice(["top", "mid", "low"], p=[0.25, 0.60, 0.15])
            if student_tier == "top":
                base_score = np.random.normal(86, 5)
            elif student_tier == "mid":
                base_score = np.random.normal(68, 8)
            else:
                base_score = np.random.normal(44, 7)

            base_score += sec_offset

            # Subject marks (6 subjects)
            # Subject specific difficulties:
            # Math (harder), Physics (moderate), Chemistry (moderate), English (higher), Computer Science (higher), Biology (moderate)
            math = int(np.clip(base_score + np.random.normal(-4, 6), 25, 99))
            physics = int(np.clip(base_score + np.random.normal(-2, 5), 28, 98))
            chemistry = int(np.clip(base_score + np.random.normal(0, 5), 30, 97))
            english = int(np.clip(base_score + np.random.normal(5, 4), 35, 100))
            comp_sci = int(np.clip(base_score + np.random.normal(6, 6), 32, 100))
            biology = int(np.clip(base_score + np.random.normal(1, 5), 30, 98))

            attendance = int(np.clip(base_score * 0.8 + np.random.normal(20, 5), 60, 100))

            records.append({
                "Student ID": stu_id,
                "Student Name": name,
                "Section": sec,
                "Gender": gender,
                "Attendance %": attendance,
                "Mathematics": math,
                "Physics": physics,
                "Chemistry": chemistry,
                "English": english,
                "Computer Science": comp_sci,
                "Biology": biology
            })

    clean_df = pd.DataFrame(records)
    clean_df.to_excel("data/sample_students_data.xlsx", index=False)
    clean_df.to_csv("data/sample_students_data.csv", index=False)
    print(f"Generated clean dataset: {len(clean_df)} records.")

    # 2. Dirty / Edge-case Dataset (50 records with noise, missing, duplicates, non-numerics)
    dirty_records = []
    for i in range(40):
        r = records[i].copy()
        dirty_records.append(r)

    # Add duplicate rows
    dirty_records.append(records[0].copy())
    dirty_records.append(records[5].copy())

    # Add duplicate ID with different marks
    dup_id_r = records[10].copy()
    dup_id_r["Student Name"] = "Duplicate ID Student"
    dirty_records.append(dup_id_r)

    # Add non-numeric marks
    dirty_records[2]["Mathematics"] = "Absent"
    dirty_records[7]["Physics"] = "AB"
    dirty_records[12]["Chemistry"] = "N/A"
    dirty_records[18]["Biology"] = "-"

    # Add missing marks (None)
    dirty_records[3]["English"] = None
    dirty_records[15]["Computer Science"] = np.nan

    # Add out-of-range marks
    dirty_records[4]["Mathematics"] = 125  # > 100
    dirty_records[9]["Physics"] = -10      # < 0

    # Add messy section names
    dirty_records[6]["Section"] = "sec a "
    dirty_records[11]["Section"] = "SECTION B"
    dirty_records[16]["Section"] = "  Section c  "

    dirty_df = pd.DataFrame(dirty_records)
    dirty_df.to_excel("data/dirty_sample_students.xlsx", index=False)
    print(f"Generated dirty edge-case dataset: {len(dirty_df)} records.")


if __name__ == "__main__":
    generate_sample_datasets()
