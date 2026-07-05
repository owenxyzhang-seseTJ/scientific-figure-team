# Method Search And Preprocessing Gate

Use this before preprocessing any quantitative data.

## Hard Gate

Do not preprocess or plot quantitative data until one of these is true:

- Live literature / method search has been completed for the figure type and material class.
- The user supplied a clear method section, instrument export protocol, or processing reference.

If neither is available, stop and ask for method references or permission/context to search. Do not silently choose a preprocessing method from memory.

## Method Search Packet

Create a `method_search_packet` with these fields:

```text
Status: READY_FOR_PREPROCESSING or BLOCKED
Search date:
Figure type:
Material/system:
Sources searched:
Chosen preprocessing method:
Rationale:
Rejected alternatives:
Assumptions and limits:
Fields required from raw data:
Fields produced after preprocessing:
```

Use current web/literature search when available. Prefer peer-reviewed papers, instrument/software documentation, database documentation, or the user's own Methods/SI. For each source, record a short citation or URL plus what processing rule it supports.

## Preprocessing Rules

- Save processed files separately from raw files.
- Never overwrite raw data.
- Preserve units and state whether values are normalized, offset, baseline-corrected, fitted, or computed.
- Keep a log of dropped rows, missing values, unit conversions, and branch/state normalization.
- If preprocessing requires subjective choices, include them in the English pre-plot plan and wait for confirmation.

## Confirmation Rule

After method search and before final plotting, write an English plan with:

- Figure objective.
- Raw files and expected columns.
- Preprocessing steps.
- Visual mapping and labels.
- Export formats.
- Limitations.
- `Status: WAITING_FOR_USER_CONFIRMATION`.

Only proceed to final plots when the status is updated to `CONFIRMED`.
