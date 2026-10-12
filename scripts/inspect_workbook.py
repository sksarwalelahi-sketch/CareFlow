
from pathlib import Path
from collections import Counter
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "data" / "raw" / "careflow_synthetic_events 1.xlsx"

if not FILE.exists():
    raise FileNotFoundError(f"Workbook not found: {FILE}")

workbook = load_workbook(FILE, read_only=True, data_only=True)
sheet = workbook.active

rows = sheet.iter_rows(values_only=True)
headers = next(rows)
headers = [str(h).strip() if h is not None else "" for h in headers]

print("WORKSHEET:", sheet.title)
print("COLUMNS:", len(headers))
print("COLUMN NAMES:")
for index, name in enumerate(headers, start=1):
    print(f"  {index}. {name}")

records = []
for row in rows:
    if any(value is not None for value in row):
        records.append(dict(zip(headers, row)))

print("\nTOTAL NON-EMPTY DATA ROWS:", len(records))

required = {"Case_ID", "Activity", "Timestamp"}
missing_columns = required - set(headers)
print("MISSING CORE COLUMNS:", sorted(missing_columns) or "None")

print("\nMISSING VALUES BY COLUMN:")
for column in headers:
    missing = sum(
        record.get(column) is None
        or str(record.get(column)).strip() == ""
        for record in records
    )
    print(f"  {column}: {missing}")

if "Case_ID" in headers:
    print("\nUNIQUE CASES:", len({
        record["Case_ID"]
        for record in records
        if record.get("Case_ID") is not None
    }))

if "Activity" in headers:
    print("\nTOP ACTIVITIES:")
    counts = Counter(
        record["Activity"]
        for record in records
        if record.get("Activity") is not None
    )
    for activity, count in counts.most_common(15):
        print(f"  {activity}: {count}")

if "Timestamp" in headers:
    invalid = [
        index for index, record in enumerate(records, start=2)
        if not hasattr(record.get("Timestamp"), "year")
        and not isinstance(record.get("Timestamp"), str)
    ]
    print("\nNON-DATETIME TIMESTAMP VALUES:", len(invalid))

workbook.close()
