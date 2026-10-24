import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from publication_recovery import checkpoint_path, load_checkpoint, save_checkpoint, run_with_retries


class PublicationRecoveryTests(unittest.TestCase):
    def test_checkpoint_revalidated_and_identity_checked(self):
        with tempfile.TemporaryDirectory() as root:
            data = {'slug': 'example', 'category': 'Productivity', 'intro': 'Validated copy'}
            save_checkpoint(root, 'example', 'Productivity', data)
            self.assertEqual(load_checkpoint(root, 'example', 'Productivity', lambda d: []), data)
            self.assertIsNone(load_checkpoint(root, 'example', 'Productivity', lambda d: ['invalid']))
            self.assertIsNone(load_checkpoint(root, 'other', 'Productivity', lambda d: []))
            path = checkpoint_path(root, 'example', 'Productivity')
            record = json.loads(path.read_text(encoding='utf-8'))
            record['category'] = 'Other'
            path.write_text(json.dumps(record), encoding='utf-8')
            self.assertIsNone(load_checkpoint(root, 'example', 'Productivity', lambda d: []))
            path.write_text('{incomplete', encoding='utf-8')
            self.assertIsNone(load_checkpoint(root, 'example', 'Productivity', lambda d: []))

    def test_retry_pins_same_command_and_stops_on_success(self):
        calls, delays = [], []
        def run(command, **kwargs):
            calls.append(list(command))
            return SimpleNamespace(returncode=1 if len(calls) < 2 else 0)
        command = ['python', 'batch_24weeks.py', '--day', '25']
        self.assertEqual(run_with_retries(command, run=run, sleep=delays.append), 0)
        self.assertEqual(calls, [command, command])
        self.assertEqual(delays, [30])

    def test_timeouts_and_exhausted_failures_remain_failures(self):
        calls, delays = [], []
        def run(command, **kwargs):
            calls.append(command)
            if len(calls) == 1:
                raise subprocess.TimeoutExpired(command, kwargs['timeout'])
            return SimpleNamespace(returncode=1)
        self.assertEqual(run_with_retries(['publish'], run=run, sleep=delays.append), 1)
        self.assertEqual(len(calls), 3)
        self.assertEqual(delays, [30, 60])


if __name__ == '__main__':
    unittest.main()
