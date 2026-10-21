import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from article_auto_repair import repair_article


class RepairTests(unittest.TestCase):
    def run_repair(self, answers, errors=None):
        self.calls = []
        def create(**kwargs):
            self.calls.append(kwargs)
            answer = answers[min(len(self.calls)-1, len(answers)-1)]
            if isinstance(answer, Exception):
                raise answer
            return NS(stop_reason=answer[0], content=[NS(type='text', text=answer[1])])
        self.original = {'slug': 'topic', 'title': 'old', 'references': []}
        before = copy.deepcopy(self.original)
        result = repair_article(NS(messages=NS(create=create)), self.original,
            ['bad title'] if errors is None else errors,
            lambda d: [] if d['title'] == 'fixed' else ['bad title'], lambda d: d, 'rules')
        self.assertEqual(before, self.original)
        return result

    def test_validated_repair(self):
        d, errors = self.run_repair([('end_turn', json.dumps({'slug':'topic','title':'fixed','references':[]}))])
        self.assertEqual(errors, [])
        self.assertEqual(len(self.calls), 1)

    def test_errors_are_not_bypassed(self):
        _, errors = self.run_repair([('end_turn', '{"slug":"topic","title":"bad","references":[]}')])
        self.assertTrue(errors)
        self.assertEqual(len(self.calls), 2)

    def test_invalid_truncated_or_changed_references_rejected(self):
        for answer in [('max_tokens', '{}'), ('end_turn', 'garbage'), ('end_turn', '[]'),
                       ('end_turn', '{"slug":"topic","title":"fixed","references":[1]}'), RuntimeError('offline')]:
            with self.subTest(answer=answer):
                d, errors = self.run_repair([answer])
                self.assertEqual(d, self.original)
                self.assertTrue(errors)

    def test_no_call_when_valid(self):
        self.run_repair([], errors=[])
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
