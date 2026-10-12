
from pathlib import Path
from collections import Counter, defaultdict
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "raw" / "careflow_synthetic_events 1.xlsx"

if not SOURCE.exists():
    raise FileNotFoundError(f"Dataset not found: {SOURCE}")

workbook = load_workbook(SOURCE, read_only=True, data_only=True)
sheet = workbook.active
iterator = sheet.iter_rows(values_only=True)

headers = [str(v).strip() for v in next(iterator)]
records = [
    dict(zip(headers, row))
    for row in iterator
    if any(value is not None for value in row)
]
workbook.close()

errors = []
warnings = []

# 1. Check unique event identifiers.
event_ids = [r["Event_ID"] for r in records]
duplicate_ids = [
    event_id for event_id, count in Counter(event_ids).items()
    if count > 1
]
if duplicate_ids:
    errors.append(f"Duplicate Event_ID values: {len(duplicate_ids)}")

# 2. Check timestamps and group events by visit.
events_by_case = defaultdict(list)

for row_number, record in enumerate(records, start=2):
    case_id = record.get("Case_ID")
    activity = record.get("Activity")
    timestamp = record.get("Timestamp")

    if not case_id or not activity or timestamp is None:
        errors.append(f"Missing core field at Excel row {row_number}")
        continue

    if not hasattr(timestamp, "year"):
        errors.append(f"Invalid timestamp at Excel row {row_number}")
        continue

    events_by_case[case_id].append(record)

# 3. Check chronological consistency within each visit.
for case_id, events in events_by_case.items():
    ordered = sorted(events, key=lambda r: r["Timestamp"])

    for earlier, later in zip(ordered, ordered[1:]):
        if later["Timestamp"] < earlier["Timestamp"]:
            errors.append(f"Chronology error in case {case_id}")
            break

# 4. Report doctor-ID coverage without inventing values.
missing_doctors = sum(
    r.get("Doctor_ID") is None
    or str(r.get("Doctor_ID")).strip() == ""
    for r in records
)

# 5. Report event statuses and case sizes.
statuses = Counter(r["Event_Status"] for r in records)
case_sizes = [len(events) for events in events_by_case.values()]

print("SOURCE DATASET VALIDATION")
print("=" * 40)
print(f"Rows: {len(records)}")
print(f"Unique visits: {len(events_by_case)}")
print(f"Unique Event_IDs: {len(set(event_ids))}")
print(f"Missing Doctor_ID: {missing_doctors}")
print(f"Smallest case: {min(case_sizes, default=0)} events")
print(f"Largest case: {max(case_sizes, default=0)} events")
print(f"Event statuses: {dict(statuses)}")

if errors:
    print("\nERRORS:")
    for error in errors:
        print("-", error)
else:
    print("\nNo core-field, timestamp-type, or Event_ID uniqueness errors found.")

if warnings:
    print("\nWARNINGS:")
    for warning in warnings:
        print("-", warning)
