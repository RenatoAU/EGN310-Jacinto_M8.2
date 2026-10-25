# Pantry Priority — Presentation Practice

Prepared for Renato Jacinto. Rehearse this outline and explain the implementation in your own words.

## Suggested 4–5 minute demonstration

1. **Problem (30 seconds):** Forgotten pantry items may go unused. The application prioritizes user-entered reminder dates and tracks used/wasted items. It does not determine food safety.
2. **Run (90 seconds):** Copy the sample as shown in README. Show Milk first, mark it used, mark Yogurt wasted, and show $2.20 wasted cost and Rice remaining. Exit and restart to verify persistence. Add an earlier-date item and show that it becomes next. Try a negative cost to show validation.
3. **Structure (60 seconds):** Open `pantry.py`: show `Item`, `add`, `peek`, and `complete`. Explain date/sequence ordering, the heap invariant, and why the heap array is not fully sorted. State core O(log n) add/remove, O(1) peek, plus linear JSON persistence work.
4. **Verification (30 seconds):** Run `python -m unittest discover -s tests -v`. Explain the independent sorted-reference and failed-save tests.
5. **Modification (60 seconds or as requested):** Change the requested behavior, run relevant checks, and demonstrate the result.

## Code map

| Location | Responsibility |
|---|---|
| `pantry.py: Item` | Immutable fields and comparison order |
| `parse_date`, `parse_cost` | Validate inputs and convert dollars to cents |
| `Pantry.add` | Push to heap and advance sequence |
| `Pantry.peek` | Read root without removal |
| `Pantry.complete` | Remove root, append history, update totals |
| `Pantry.summary` | Return counts and costs |
| `Pantry.load` | Validate data, heapify, rebuild totals and next ID |
| `Pantry.save` | Temporary write and destination replacement |
| `app.py: main` | Menu, confirmation, save-before-adopting behavior |
| `tests/test_pantry.py` | Automated behavior checks |

## Practice modifications

- **Show pending count beside the menu:** Add `print(f'Pending items: {len(pantry)}')` inside the `main` loop. Add an item and verify the count changes.
- **Reject names shorter than two characters:** Update `Pantry.add`, add a test, and decide how existing one-character names should behave on load before changing its validation too.
- **Display average wasted cost:** In option 5, divide wasted cents by wasted count, then convert to dollars for display. Guard against zero wasted count. Keep stored totals in integer cents.
- **Change date ties to alphabetical order:** Moving `name` ahead of `sequence` in the dataclass changes comparison order. Positional constructor calls must also be updated. Update tie tests to match the intended new behavior.

## Questions to answer

- Why not a queue? Arrival order is not the required date priority.
- Why sequence IDs? Equal dates should remain deterministic and FIFO.
- Why not sort after every add? A heap maintains the next item without continuously sorting everything.
- Why integer cents? Exact accumulated money totals.
- Is the complete menu action O(log n)? No. Loading and saving all JSON adds O(n + h) work.
- What happens when empty? Peek returns `None`; completing is rejected.
- What happens with invalid JSON? Startup reports an error and leaves it unchanged.
- What would scale better? Transactional persistence and concurrency control, with a design for arbitrary updates.

This guide does not establish personal mastery or a completed presentation. Practice locally and present actual development dates.
