# Validation Record

Date: October 25, 2026. Checks performed by the AI assistant in its execution environment, not a claimed student local run.

Environment: Python 3.12.14 on Linux. Windows execution was not directly tested.

## Automated tests

Command: `python -m unittest discover -s tests -v`

Result: **14 tests passed**. Coverage includes independent priority ordering across 200 records, FIFO ties, exact cent totals, empty queues, invalid inputs and statuses, reload, duplicate IDs, invalid JSON, failed-save preservation, sample output, and CLI flow.

## Scripted CLI demonstration

The sample was copied to a temporary file. Milk was marked used, Yogurt wasted, and Rice remained. The summary matched Pending 1, Used 1, Wasted 1; estimated used cost $3.80 and wasted cost $2.20. Restarting preserved the summary. Both process exits returned zero.

```text
PANTRY PRIORITY
Dates are planning reminders, not food safety decisions.
Data file: <temporary demo file>

1 Add item  2 View next  3 Mark next used  4 Mark next wasted
5 Summary   6 List pending   0 Exit
Choose: #2 | Milk | reminder: 2026-10-27 | $3.80

1 Add item  2 View next  3 Mark next used  4 Mark next wasted
5 Summary   6 List pending   0 Exit
Choose: #2 | Milk | reminder: 2026-10-27 | $3.80
Confirm (yes/no): Saved:
#2 | Milk | reminder: 2026-10-27 | $3.80

1 Add item  2 View next  3 Mark next used  4 Mark next wasted
5 Summary   6 List pending   0 Exit
Choose: #3 | Yogurt | reminder: 2026-10-27 | $2.20

1 Add item  2 View next  3 Mark next used  4 Mark next wasted
5 Summary   6 List pending   0 Exit
Choose: #3 | Yogurt | reminder: 2026-10-27 | $2.20
Confirm (yes/no): Saved:
#3 | Yogurt | reminder: 2026-10-27 | $2.20

1 Add item  2 View next  3 Mark next used  4 Mark next wasted
5 Summary   6 List pending   0 Exit
Choose: Pending: 1 | Used: 1 | Wasted: 1
Estimated used cost: $3.80
Estimated wasted cost: $2.20

1 Add item  2 View next  3 Mark next used  4 Mark next wasted
5 Summary   6 List pending   0 Exit
Choose: #1 | Rice | reminder: 2026-11-02 | $4.50

1 Add item  2 View next  3 Mark next used  4 Mark next wasted
5 Summary   6 List pending   0 Exit
Choose: Goodbye.
```

## Remaining verification

Student local execution and the live presentation remain unverified. During subsequent repository integration, the connected GitHub metadata confirmed public visibility. The pre-delivery history contained one initial README-only commit dated October 25, 2026; no Modules 4–8 history was present. The 14 automated tests passed again before publication.
