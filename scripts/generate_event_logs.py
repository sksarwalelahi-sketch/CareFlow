
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Project root is the parent of the scripts directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "hospital_event_logs.csv"

random.seed(42)

COLUMNS = [
    "Case_ID",
    "Activity_Name",
    "Timestamp",
    "Patient_ID",
    "Department",
    "Doctor_ID",
    "Age_Group",
    "Gender",
    "Event_Status",
    "Outcome",
]

AGE_GROUPS = ["0-17", "18-30", "31-45", "46-60", "60+"]
GENDERS = ["Female", "Male", "Other"]


def generate_patient_journey(case_number):
    """Generate one synthetic hospital visit."""
    case_id = f"C{case_number:04d}"
    patient_id = f"P{case_number:04d}"

    age_group = random.choice(AGE_GROUPS)
    gender = random.choice(GENDERS)

    # Each visit starts at a different time.
    current_time = datetime(2026, 10, 10, 8, 0) + timedelta(
        minutes=case_number * 7
    )

    doctor_id = f"DR{random.randint(1, 5):03d}"

    events = [
        ("Registration", "Reception"),
        ("Triage", "Emergency"),
        ("Doctor Consultation", "Emergency"),
    ]

    # Deliberately simulate a process loop-back in selected cases.
    if case_number % 4 == 0:
        events.extend([
            ("X-Ray", "Radiology"),
            ("Triage", "Emergency"),
            ("Doctor Consultation", "Emergency"),
        ])
    elif case_number % 3 == 0:
        events.append(("Blood Test", "Laboratory"))

    outcome = random.choice(["Discharged", "Admitted"])

    if outcome == "Admitted":
        events.append(("Admission", "Inpatient"))
    else:
        events.append(("Discharge", "Emergency"))

    rows = []

    for activity, department in events:
        current_time += timedelta(minutes=random.randint(5, 25))

        rows.append({
            "Case_ID": case_id,
            "Activity_Name": activity,
            "Timestamp": current_time.isoformat(
                sep=" ", timespec="seconds"
            ),
            "Patient_ID": patient_id,
            "Department": department,
            "Doctor_ID": (
                doctor_id if department != "Reception" else ""
            ),
            "Age_Group": age_group,
            "Gender": gender,
            "Event_Status": "Completed",
            "Outcome": outcome,
        })

    return rows


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_events = []

    for case_number in range(1, 31):
        all_events.extend(generate_patient_journey(case_number))

    # Sort globally by timestamp while preserving each case's sequence.
    all_events.sort(key=lambda row: row["Timestamp"])

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(all_events)

    print(f"Dataset created: {OUTPUT_FILE}")
    print(f"Total visits: 30")
    print(f"Total events: {len(all_events)}")


if __name__ == "__main__":
    main()
