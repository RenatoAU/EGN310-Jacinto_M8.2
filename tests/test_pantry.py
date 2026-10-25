import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch
from pantry import Pantry
from app import main


class PantryTests(unittest.TestCase):
    def test_priority_and_peek(self):
        p = Pantry()
        for name, day in [('Rice', '2026-11-02'), ('Milk', '2026-10-27'), ('Yogurt', '2026-10-28')]:
            p.add(name, day, '2')
        self.assertEqual(p.peek().name, 'Milk')
        self.assertEqual(len(p), 3)
        self.assertEqual(p.complete('used').name, 'Milk')
        self.assertEqual(p.peek().name, 'Yogurt')

    def test_stable_ties(self):
        p = Pantry()
        for name in ['Zucchini', 'Apple', 'Zucchini']:
            p.add(name, '2026-10-27', '1')
        self.assertEqual([p.complete('used').sequence for _ in range(3)], [1, 2, 3])

    def test_matches_sorted_reference(self):
        p = Pantry()
        rng = random.Random(310)
        dates = [f'2026-11-{rng.randint(1, 28):02d}' for _ in range(200)]
        for i, day in enumerate(dates):
            p.add(str(i), day, '0')
        actual = []
        while p:
            item = p.complete('used')
            actual.append((item.reminder_date, item.sequence))
        self.assertEqual(actual, sorted((day, i+1) for i, day in enumerate(dates)))

    def test_exact_totals(self):
        p = Pantry()
        for i, cost in enumerate(['0.10', '0.20', '5.50']):
            p.add(str(i), f'2026-10-{25+i}', cost)
        p.complete('wasted')
        p.complete('wasted')
        p.complete('used')
        self.assertEqual(p.summary(), {'pending_count': 0, 'used_count': 1,
                         'wasted_count': 2, 'used_cost_cents': 550, 'wasted_cost_cents': 30})

    def test_empty(self):
        p = Pantry()
        self.assertIsNone(p.peek())
        with self.assertRaises(ValueError):
            p.complete('used')

    def test_invalid_inputs(self):
        p = Pantry()
        cases = [('', '2026-10-25', '1'), ('A', '2026-02-30', '1'),
                 ('A', '10/25/2026', '1'), ('A', '2026-10-25', '-1'),
                 ('A', '2026-10-25', 'NaN'), ('A', '2026-10-25', 'Infinity'),
                 ('A', '2026-10-25', '1.001'), ('A', '2026-10-25', 'abc')]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                p.add(*args)
        self.assertEqual(len(p), 0)

    def test_bad_status_preserves_item(self):
        p = Pantry()
        p.add('A', '2026-10-25', '0')
        with self.assertRaises(ValueError):
            p.complete('lost')
        self.assertEqual(len(p), 1)

    def test_reload(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'state.json'
            p = Pantry()
            p.add('A', '2026-10-25', '1.25')
            p.add('B', '2026-10-26', '2')
            p.complete('wasted')
            p.save(path)
            q = Pantry.load(path)
            self.assertEqual(p.to_dict(), q.to_dict())
            self.assertEqual(p.summary(), q.summary())
            self.assertEqual(q.add('C', '2026-10-27', '0').sequence, 3)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(len(Pantry.load(Path(d) / 'missing.json')), 0)

    def test_corrupt_file_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'state.json'
            for text in ['broken json', '{"version": 9}', '[]']:
                path.write_text(text)
                with self.assertRaises(ValueError):
                    Pantry.load(path)
                self.assertEqual(path.read_text(), text)

    def test_duplicate_ids(self):
        p = Pantry()
        p.add('A', '2026-10-25', '1')
        data = p.to_dict()
        data['pending'].append(data['pending'][0])
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'state.json'
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                Pantry.load(path)

    def test_failed_save_preserves_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'state.json'
            p = Pantry()
            p.save(path)
            previous = path.read_bytes()
            p.add('A', '2026-10-25', '1')
            with patch('pantry.os.replace', side_effect=OSError('simulated failure')):
                with self.assertRaises(OSError):
                    p.save(path)
            self.assertEqual(path.read_bytes(), previous)
            self.assertEqual(list(Path(d).iterdir()), [path])

    def test_cli_flow(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'state.json'
            answers = ['1', 'Milk', '2026-10-27', '3.80', '2', '3', 'yes', '5', '0']
            with patch('builtins.input', side_effect=answers), patch('builtins.print') as output:
                self.assertEqual(main(['--data', str(path)]), 0)
            self.assertIn('Estimated used cost: $3.80', [str(c.args[0]) for c in output.call_args_list if c.args])
            self.assertEqual(Pantry.load(path).summary()['used_count'], 1)

    def test_sample(self):
        p = Pantry.load(Path(__file__).resolve().parents[1] / 'examples' / 'sample_pantry.json')
        self.assertEqual(p.complete('used').name, 'Milk')
        self.assertEqual(p.complete('wasted').name, 'Yogurt')
        self.assertEqual(p.peek().name, 'Rice')
        self.assertEqual(p.summary()['wasted_cost_cents'], 220)


if __name__ == '__main__':
    unittest.main()
