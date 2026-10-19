"""Offline regression tests. Never import publisher credentials or call APIs."""
import ast
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
tree = ast.parse((ROOT / 'publisher_v2.py').read_text(encoding='utf-8'))
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'repair_section_headings')
ns = {'json': json}
exec(compile(ast.Module(body=[fn], type_ignores=[]), '<repair>', 'exec'), ns)
repair = ns['repair_section_headings']


class HeadingRepair(unittest.TestCase):
    def setUp(self):
        self.data = {'title': 'Original', 'sections': [{'h2': 'Old?', 'content': 'Unchanged body'} for _ in range(5)]}
        self.errors = ['section 5 must follow the required definition/signs/why/action/daily order']
        self.calls = 0

    def client(self, answer):
        def create(**kwargs):
            self.calls += 1
            if isinstance(answer, Exception):
                raise answer
            return SimpleNamespace(content=[SimpleNamespace(text=answer)])
        return SimpleNamespace(messages=SimpleNamespace(create=create))

    def test_only_headings_change_and_original_is_preserved(self):
        before = copy.deepcopy(self.data)
        headings = ['What is focus?', 'What are the signs?', 'Why does it happen?', 'How can you act?', 'How can you manage focus daily?']
        result = repair(self.client(json.dumps({'headings': headings})), self.data, self.errors, 'focus')
        self.assertEqual(self.calls, 1)
        self.assertEqual(self.data, before)
        self.assertEqual(result['title'], before['title'])
        self.assertEqual([s['content'] for s in result['sections']], [s['content'] for s in before['sections']])
        self.assertEqual([s['h2'] for s in result['sections']], headings)

    def test_other_quality_errors_do_not_trigger_repair(self):
        result = repair(self.client('{}'), self.data, self.errors + ['unsafe claim'], 'focus')
        self.assertIs(result, self.data)
        self.assertEqual(self.calls, 0)

    def test_invalid_or_unrepairable_response_fails_closed(self):
        for answer in ['not json', '{"cannot_repair":true}', '{"headings":["one"]}', '[]', RuntimeError('offline')]:
            with self.subTest(answer=str(answer)):
                self.assertIs(repair(self.client(answer), self.data, self.errors, 'focus'), self.data)

    def test_full_validation_follows_repair_before_saving(self):
        generator = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'generate_article')
        code = ast.unparse(generator)
        after = code.split('data = repair_section_headings', 1)[1]
        self.assertLess(after.index('validate_article_quality'), after.index('return save_editorial_draft'))
        self.assertIn('if quality_errors:', after)
        self.assertIn('return None', after)


if __name__ == '__main__':
    unittest.main()
