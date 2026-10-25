"""Pantry Priority domain model: stable min-heap and exact cent totals."""
from dataclasses import dataclass, asdict
from datetime import date
from decimal import Decimal, InvalidOperation
import heapq
import json
from pathlib import Path
import re
import tempfile
import os


def parse_date(text):
    if not isinstance(text, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', text):
        raise ValueError('Date must use YYYY-MM-DD.')
    return date.fromisoformat(text).isoformat()


def parse_cost(text):
    try:
        amount = Decimal(str(text))
        if not amount.is_finite() or amount < 0 or amount > Decimal('999999999.99'):
            raise ValueError('Cost must be between 0 and 999999999.99.')
        cents = amount * 100
        if cents != cents.to_integral_value():
            raise ValueError('Cost must have at most two decimal places.')
        return int(cents)
    except (InvalidOperation, TypeError):
        raise ValueError('Enter a valid cost, such as 4.50.') from None


@dataclass(frozen=True, order=True)
class Item:
    # Ordering uses date first, then unique arrival number (FIFO for ties).
    reminder_date: str
    sequence: int
    name: str
    cost_cents: int


class Pantry:
    def __init__(self):
        self._heap = []
        self._history = []
        self._next_sequence = 1
        self._totals = {'used_count': 0, 'wasted_count': 0,
                        'used_cost_cents': 0, 'wasted_cost_cents': 0}

    def __len__(self):
        return len(self._heap)

    def add(self, name, reminder_date, cost):
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Item name cannot be empty.')
        item = Item(parse_date(reminder_date), self._next_sequence,
                    name.strip(), parse_cost(cost))
        heapq.heappush(self._heap, item)
        self._next_sequence += 1
        return item

    def peek(self):
        return self._heap[0] if self._heap else None

    def complete(self, status):
        if status not in ('used', 'wasted'):
            raise ValueError('Status must be used or wasted.')
        if not self._heap:
            raise ValueError('The pantry is empty.')
        item = heapq.heappop(self._heap)
        self._history.append({'item': asdict(item), 'status': status})
        self._totals[status + '_count'] += 1
        self._totals[status + '_cost_cents'] += item.cost_cents
        return item

    def ordered_items(self):
        # A heap guarantees only its root is smallest; it is not fully sorted.
        return sorted(self._heap)

    def summary(self):
        return dict(self._totals, pending_count=len(self))

    def to_dict(self):
        return {'version': 1, 'pending': [asdict(i) for i in self._heap],
                'history': list(self._history)}

    @classmethod
    def load(cls, path):
        path = Path(path)
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1:
                raise ValueError('Unsupported data version.')
            if not isinstance(data.get('pending'), list) or not isinstance(data.get('history'), list):
                raise ValueError('Pending and history must be lists.')
            pantry = cls()
            seen = set()

            def decode(row):
                if not isinstance(row, dict) or set(row) != {'reminder_date', 'sequence', 'name', 'cost_cents'}:
                    raise ValueError('Invalid item fields.')
                seq, cents = row['sequence'], row['cost_cents']
                if type(seq) is not int or seq < 1 or seq in seen:
                    raise ValueError('Item IDs must be unique positive integers.')
                if type(cents) is not int or not 0 <= cents <= 99999999999:
                    raise ValueError('Invalid cost in cents.')
                if not isinstance(row['name'], str) or not row['name'].strip():
                    raise ValueError('Invalid item name.')
                seen.add(seq)
                return Item(parse_date(row['reminder_date']), seq, row['name'].strip(), cents)

            pantry._heap = [decode(row) for row in data['pending']]
            heapq.heapify(pantry._heap)
            for entry in data['history']:
                if not isinstance(entry, dict) or set(entry) != {'item', 'status'} or entry['status'] not in ('used', 'wasted'):
                    raise ValueError('Invalid history entry.')
                item = decode(entry['item'])
                status = entry['status']
                pantry._history.append({'item': asdict(item), 'status': status})
                pantry._totals[status + '_count'] += 1
                pantry._totals[status + '_cost_cents'] += item.cost_cents
            pantry._next_sequence = max(seen, default=0) + 1
            return pantry
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError(f'Invalid pantry data: {exc}') from exc

    def save(self, path):
        """Write beside the destination, then replace; never truncate the old file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                             dir=path.parent, delete=False) as out:
                temporary = Path(out.name)
                json.dump(self.to_dict(), out, indent=2)
                out.write('\n')
                out.flush()
                os.fsync(out.fileno())
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
