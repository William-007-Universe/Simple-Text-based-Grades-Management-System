import json
import random
from typing import Dict, Any, List, Tuple, Optional

# ----------------------------
# Sample Data Generator (given)
# ----------------------------
random.seed(0)

def generate_sample_data() -> Dict[str, Dict[str, Any]]:
    """
    Generate a sample dictionary of students with a random number of subjects and grades.
    """
    student_names = ["Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Hannah"]
    subjects = ["Math", "English", "Science", "History", "Art"]
    students: Dict[str, Dict[str, Any]] = {}

    for name in student_names:
        number_of_subjects = random.randint(2, len(subjects))  # Random number of subjects
        selected_subjects = random.sample(subjects, number_of_subjects)
        grades = {subject: random.randint(50, 100) for subject in selected_subjects}
        students[name] = {"grades": grades}

    return students

# ----------------------------
# Validation Helpers
# ----------------------------
def _is_valid_grades_dict(grades: Any) -> bool:
    """
    Valid if: dict[str, int] and each grade is 0..100
    """
    if not isinstance(grades, dict) or not grades:
        return False
    for k, v in grades.items():
        if not isinstance(k, str) or not k.strip():
            return False
        if not isinstance(v, int) or not (0 <= v <= 100):
            return False
    return True

def _ensure_student_struct(students: Dict[str, Dict[str, Any]], name: str) -> bool:
    """
    Ensures the internal structure is as expected for a student record.
    """
    rec = students.get(name)
    return isinstance(rec, dict) and "grades" in rec and isinstance(rec["grades"], dict)

# ----------------------------
# 1) Add a Student Record
# ----------------------------
def add_student(students: Dict[str, Dict[str, Any]], name: str, grades: Dict[str, int]) -> bool:
    """
    Adds a new student record with their grades for various subjects.

    Returns False if:
      - the student already exists
      - grades are not in the correct format (dict[str, int] with 0..100)
    """
    if not isinstance(name, str) or not name.strip():
        return False
    if name in students:
        return False
    if not _is_valid_grades_dict(grades):
        return False

    students[name] = {"grades": dict(grades)}  # copy
    return True

# ----------------------------
# 2) Update a Student’s Grade
# ----------------------------
def update_grade(students: Dict[str, Dict[str, Any]], name: str, subject: str, new_grade: int) -> bool:
    """
    Updates a student's grade for a specific subject.

    Returns False if the student or subject is not found, or grade invalid.
    """
    if not isinstance(new_grade, int) or not (0 <= new_grade <= 100):
        return False
    if not _ensure_student_struct(students, name):
        return False
    if subject not in students[name]["grades"]:
        return False

    students[name]["grades"][subject] = new_grade
    return True

# ----------------------------
# 3) Delete a Student Record
# ----------------------------
def delete_student(students: Dict[str, Dict[str, Any]], name: str) -> bool:
    """
    Deletes a student record by name.
    """
    if name in students:
        del students[name]
        return True
    return False

# ----------------------------
# 4) Display Records + Averages
# ----------------------------
def display_records(students: Dict[str, Dict[str, Any]]) -> None:
    """
    Displays all student records with grades and calculates:
      - average grade per student
      - average grade per subject across all students
    """
    if not students:
        print("No records to display.")
        return

    # Gather all subjects (union)
    all_subjects: List[str] = sorted({subj for s in students.values() for subj in s.get("grades", {}).keys()})

    print("=" * 70)
    print("STUDENT RECORDS")
    print("=" * 70)
    # Header row
    header = ["Student"] + all_subjects + ["Average"]
    print(" | ".join(f"{h:>10}" for h in header))
    print("-" * 70)

    # Per-student rows + per-student average
    subject_totals: Dict[str, int] = {s: 0 for s in all_subjects}
    subject_counts: Dict[str, int] = {s: 0 for s in all_subjects}

    for student_name in sorted(students.keys()):
        grades = students[student_name].get("grades", {})
        row = [f"{student_name:>10}"]
        present_grades = []
        for subj in all_subjects:
            if subj in grades:
                g = grades[subj]
                row.append(f"{g:>10}")
                present_grades.append(g)
                subject_totals[subj] += g
                subject_counts[subj] += 1
            else:
                row.append(f"{'-':>10}")
        avg = sum(present_grades) / len(present_grades) if present_grades else 0.0
        row.append(f"{avg:>10.2f}")
        print(" | ".join(row))

    print("-" * 70)
    # Subject averages row
    subject_avgs = []
    for subj in all_subjects:
        if subject_counts[subj] > 0:
            subject_avgs.append(subject_totals[subj] / subject_counts[subj])
        else:
            subject_avgs.append(0.0)

    print(f"{'Subject Avg':>10} | " + " | ".join(f"{avg:>10.2f}" for avg in subject_avgs) + " | " + f"{'-':>10}")
    print("=" * 70)

# ----------------------------
# 5) Save / Load JSON
# ----------------------------
def save_data(students: Dict[str, Dict[str, Any]], filename: str = 'students.json') -> bool:
    """
    Saves the student data to a JSON file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(students, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def load_data(filename: str = 'students.json') -> Dict[str, Dict[str, Any]]:
    """
    Loads student data from a JSON file (returns {} if load fails).
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        # minimal structural sanity check
        if not isinstance(data, dict):
            raise ValueError("Root is not a dict.")
        for name, rec in data.items():
            if not isinstance(name, str):
                raise ValueError("Student name not string.")
            if not isinstance(rec, dict) or "grades" not in rec or not isinstance(rec["grades"], dict):
                raise ValueError("Invalid student record shape.")
            for subj, grade in rec["grades"].items():
                if not isinstance(subj, str) or not isinstance(grade, int):
                    raise ValueError("Invalid grade format.")

        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}# Create sample data

    #

students = generate_sample_data()

# Add student
print("Add Ivy:", add_student(students, "Ivy", {"Math": 85, "Science": 90}))            # True
print("Add Ivy again (should fail):", add_student(students, "Ivy", {"Math": 85}))        # False
print("Add bad format (should fail):", add_student(students, "Jay", [("Math", 80)]))     # False

# Update grade
print("Update Alice Math to 92:", update_grade(students, "Alice", "Math", 92))           # True/False depending on Alice's subjects
print("Update non-existent subject (should fail):", update_grade(students, "Alice", "Biology", 88))  # False

# Delete student
print("Delete Bob:", delete_student(students, "Bob"))                                     # True/False depending on presence

# Display records + averages
display_records(students)

# Save / Load
print("Save:", save_data(students, "students.json"))
loaded = load_data("students.json")
print("Loaded records:", len(loaded))
display_records(loaded)
