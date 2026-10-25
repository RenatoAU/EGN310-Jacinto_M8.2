"""Run with python app.py. No third-party packages required."""
import argparse
from pathlib import Path
from pantry import Pantry


def show_item(item):
    if item is None:
        print('The pantry is empty.')
    else:
        print(f'#{item.sequence} | {item.name} | reminder: {item.reminder_date} | ${item.cost_cents / 100:.2f}')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Prioritize household pantry items by reminder date.')
    parser.add_argument('--data', type=Path, default=Path(__file__).resolve().parent / 'data' / 'pantry.json',
                        help='JSON state file; defaults to data/pantry.json beside app.py')
    args = parser.parse_args(argv)
    try:
        pantry = Pantry.load(args.data)
    except (OSError, ValueError) as exc:
        print(f'Cannot open data: {exc}\nExisting data was not changed. Check the path or restore a backup.')
        return 1
    print('PANTRY PRIORITY\nDates are planning reminders, not food safety decisions.')
    print(f'Data file: {args.data.resolve()}')
    try:
        while True:
            print('\n1 Add item  2 View next  3 Mark next used  4 Mark next wasted')
            print('5 Summary   6 List pending   0 Exit')
            choice = input('Choose: ').strip()
            try:
                if choice == '0':
                    print('Goodbye.')
                    return 0
                if choice in ('1', '3', '4'):
                    # Mutate a candidate; publish it only after a successful disk save.
                    candidate = Pantry.load(args.data)
                    if choice == '1':
                        name = input('Item name: ')
                        reminder = input('Reminder date (YYYY-MM-DD): ')
                        cost = input('Estimated purchase cost ($): ')
                        item = candidate.add(name, reminder, cost)
                    else:
                        show_item(candidate.peek())
                        if candidate.peek() is None:
                            continue
                        if input('Confirm (yes/no): ').strip().lower() != 'yes':
                            print('Cancelled.')
                            continue
                        item = candidate.complete('used' if choice == '3' else 'wasted')
                    candidate.save(args.data)
                    pantry = candidate
                    print('Saved:')
                    show_item(item)
                elif choice == '2':
                    show_item(pantry.peek())
                elif choice == '5':
                    s = pantry.summary()
                    print(f"Pending: {s['pending_count']} | Used: {s['used_count']} | Wasted: {s['wasted_count']}")
                    print(f"Estimated used cost: ${s['used_cost_cents']/100:.2f}")
                    print(f"Estimated wasted cost: ${s['wasted_cost_cents']/100:.2f}")
                elif choice == '6':
                    for item in pantry.ordered_items():
                        show_item(item)
                    if not pantry:
                        print('The pantry is empty.')
                else:
                    print('Choose a number from 0 to 6.')
            except (ValueError, OSError) as exc:
                print(f'Operation not saved: {exc}')
    except (EOFError, KeyboardInterrupt):
        print('\nGoodbye. Previously saved changes are retained.')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
