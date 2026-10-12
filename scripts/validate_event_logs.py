
import csv
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "hospital_event_logs.csv"

REQUIRED_COLUMNS = {
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
}


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Dataset not found. Run generate_event_logs.py first."
        )

    with INPUT_FILE.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        actual_columns = set(reader.fieldnames or [])

        missing_columns = REQUIRED_COLUMNS - actual_columns

        if missing_columns:
            raise ValueError(
                f"Missing columns: {sorted(missing_columns)}"
            )

        rows = list(reader)

    if not rows:
        raise ValueError("Dataset is empty.")

    required_values = ["Case_ID", "Activity_Name", "Timestamp"]
    seen_events = set()
    previous_timestamp = {}

    for line_number, row in enumerate(rows, start=2):
        for column in required_values:
            if not row[column].strip():
                raise ValueError(
                    f"Empty {column} at CSV line {line_number}"
                )

        timestamp = datetime.fromisoformat(row["Timestamp"])
        case_id = row["Case_ID"]

        # Validate chronology within each patient visit.
        if (
            case_id in previous_timestamp
            and timestamp < previous_timestamp[case_id]
        ):
            raise ValueError(
                f"Events out of order for {case_id}"
            )

        previous_timestamp[case_id] = timestamp

        event_key = (
            case_id,
            row["Activity_Name"],
            row["Timestamp"],
        )

        if event_key in seen_events:
            raise ValueError(
                f"Duplicate event found: {event_key}"
            )

        seen_events.add(event_key)

    case_count = len({row["Case_ID"] for row in rows})

    print("VALIDATION PASSED")
    print(f"Rows checked: {len(rows)}")
    print(f"Unique visits: {case_count}")
    print(f"Columns found: {len(actual_columns)}")


if __name__ == "__main__":
    main()
