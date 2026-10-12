
# CareFlow Event Log Data Dictionary

## Purpose
Synthetic hospital event logs for clinical pathway process mining.

## Core process-mining fields

| Column | Type | Description |
|---|---|---|
| Case_ID | STRING | Unique patient-visit/process identifier |
| Activity_Name | STRING | Hospital activity performed |
| Timestamp | DATETIME | Date and time of the activity |

## Additional analytical fields

| Column | Type | Description |
|---|---|---|
| Patient_ID | STRING | Synthetic patient identifier |
| Department | STRING | Hospital department |
| Doctor_ID | STRING | Synthetic doctor identifier |
| Age_Group | STRING | Synthetic age category |
| Gender | STRING | Synthetic demographic category |
| Event_Status | STRING | Event completion status |
| Outcome | STRING | Visit outcome, when known |

## Data rules

- Each row represents one event in a patient journey.
- Case_ID groups events belonging to the same visit.
- Events within each case must be chronologically ordered.
- Timestamps use ISO 8601 format.
- Patient and doctor identifiers must be synthetic.
- Do not include real patient names or medical records.
- The process-mining export must contain at least the three core fields.
