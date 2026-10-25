# Pantry Priority

**EGN 310 — Data Structures | Module 8, Assignment 8.2**  
Prepared for Renato Jacinto

A Python command-line application that helps one household decide which pantry or refrigerator item to use next. It replaces manually reviewing and sorting a food list. No specific original workbook was available for verification in this delivery.

Reminder dates are entered by the user and are planning reminders, not food safety determinations. Costs are estimates, not measured savings.

## Features

1. Add a named item with a date and estimated purchase cost.
2. View the earliest item without removing it.
3. Mark the next item used or wasted and remove it from the queue.
4. Show pending, used, and wasted counts and estimated used/wasted costs.

Also includes an ordered pending list, stable arrival order for tied dates, input validation, and automatic JSON persistence.

## Setup and run

Requires **Python 3.10+** on Windows, macOS, or Linux. No third-party packages are required.

1. Extract the ZIP.
2. Open a terminal inside `Pantry_Priority`, beside `app.py`.
3. Run:

```text
python --version
python app.py
```

On Windows use `py` if `python` is unavailable. On macOS/Linux use `python3` if needed. No pip installation is necessary.

The default data file is `data/pantry.json` beside `app.py`. It is created when the first change is saved. The program prints the data path at startup. Exit with `0` or Ctrl+C; previous saved changes remain.

## Menu

| Option | Action |
|---|---|
| 1 | Add item: name, YYYY-MM-DD date, cost such as 3.80 |
| 2 | Show earliest item |
| 3 | Mark next used after typing `yes` |
| 4 | Mark next wasted after typing `yes` |
| 5 | Show summary |
| 6 | List pending items in priority order |
| 0 | Exit |

Do not type a dollar sign with the cost. Blank names, impossible dates, negative costs, non-finite values, and fractions of a cent are rejected. Zero cost and past dates are allowed. Maximum cost is $999,999,999.99 per item.

## Reproducible demonstration

Copy the sample to a working file so the original remains available.

Windows PowerShell:

```powershell
Copy-Item examples/sample_pantry.json demo.json
python app.py --data demo.json
```

macOS/Linux:

```sh
cp examples/sample_pantry.json demo.json
python3 app.py --data demo.json
```

The sample is synthetic classroom data with fixed dates; its priority order remains reproducible after those dates pass.

1. Choose `2`: Milk is first (2026-10-27, $3.80).
2. Choose `3`, then `yes`: mark Milk used.
3. Choose `2`: Yogurt is next. It has the same date but arrived later.
4. Choose `4`, then `yes`: mark Yogurt wasted.
5. Choose `5`: Pending 1, Used 1, Wasted 1; used cost $3.80 and wasted cost $2.20.
6. Choose `6`: Rice remains (2026-11-02, $4.50).
7. Exit and restart with the same command. The saved summary remains.

Exit and recopy the sample to reset the demo. This overwrites only `demo.json`.

## Data structure justification

The central structure is a **min-heap priority queue** using `heapq`. Each immutable `Item` stores `(reminder_date, sequence, name, cost_cents)`. Validated ISO dates sort chronologically as strings. Unique increasing sequence numbers resolve ties in arrival order, so names and costs never determine priority.

The heap invariant is that each parent is no greater than its children. Therefore the root is always the next item. `heappush` restores the invariant after insertion and `heappop` restores it after root removal. The internal array is not globally sorted; the optional full listing sorts a copy.

| Operation | In-memory complexity | Reason |
|---|---|---|
| Add item | O(log n) | Heap insertion |
| View next | O(1) | Read heap root |
| Mark next used/wasted | O(log n) amortized | Heap removal and amortized history append |
| Summary | O(1) | Counts and totals maintained incrementally |
| List all pending | O(n log n) | Sort a copy |
| Rebuild heap | O(n) | `heapify` |
| Full load/save | O(n + h) | Read/write pending items and history |

`n` is pending items and `h` is completed records. Storage is O(n + h). These bounds assume ordinary bounded-size fields and integer operations.

An unsorted list inserts cheaply but scans O(n) to find the next item. A sorted list allows immediate access at one end but requires O(n) shifting for insertion. A FIFO queue follows arrival time rather than date; a stack selects the newest item. A heap fits repeated insertion and earliest-date selection.

**Persistence tradeoff:** Menu mutations reload and save the entire JSON state. End-to-end add/remove operations include O(n + h) I/O work, so the complete menu operation is not O(log n). The heap bounds describe core priority operations. JSON makes this small single-user project portable and inspectable; a larger system needs different persistence.

A list stores completed records for append and load-time scanning. A dictionary stores summary totals for direct access. Money uses integer cents to avoid floating-point accumulation errors.

## Data, backups, and errors

The JSON format contains `version`, `pending`, and `history`. Each item has date, sequence, name, and integer cents. Totals and next ID are reconstructed on load.

Saving writes a temporary file beside the destination before replacing it. A failed save does not adopt the candidate change in the running application. This is not a substitute for a backup.

- Back up by exiting and copying your JSON state file elsewhere.
- Invalid existing data produces an error and is not automatically overwritten. Restore a valid backup or select a new file with `--data`.
- Missing data starts empty.
- Unwritable storage produces an operation-not-saved message. Choose a writable path.
- Use only one process per state file. File locking, accounts, simultaneous users, and editing arbitrary pending items are outside scope.

## Tests

From the project folder:

```text
python -m unittest discover -s tests -v
```

Tests cover independent reference ordering, stable ties, exact costs, empty queues, invalid inputs, persistence, duplicate IDs, failed saving, sample outputs, and the menu flow. See `VALIDATION.md` for actual results.

## Files

| File | Purpose |
|---|---|
| `app.py` | Menu, confirmations, and error handling |
| `pantry.py` | Heap, validation, totals, and persistence |
| `tests/test_pantry.py` | Automated tests |
| `examples/sample_pantry.json` | Synthetic demo input |
| `README.md` | Setup and structure justification |
| `AI_LOG.md` | AI assistance disclosure |
| `PRESENTATION_GUIDE.md` | Demonstration and change practice |
| `SUBMISSION_CHECKLIST.md` | Publishing and history steps |
| `VALIDATION.md` | Recorded verification |
| `requirements.txt` | Standard library only |
| `.gitignore` | Excludes runtime data and caches |

## Repository, history, and AI use

Public repository: https://github.com/RenatoAU/EGN310-Jacinto_M8.2

Clone and run:

```text
git clone https://github.com/RenatoAU/EGN310-Jacinto_M8.2.git
cd EGN310-Jacinto_M8.2
python app.py
```
