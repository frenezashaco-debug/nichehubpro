import ast
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clean_ai_text import clean_ai_text


class CopyPreservation(unittest.TestCase):
    def test_medical_and_statistical_meaning_preserved(self):
        text = '<p>Elevated blood pressure is not improved blood pressure. A statistically significant result does not establish a large effect.</p>'
        self.assertEqual(clean_ai_text(text), text)

    def test_code_links_and_schema_preserved(self):
        text = '<a href="/articles/elevated-risk.html">Elevated risk</a><script type="application/ld+json">{"name":"significantly elevated"}</script>'
        self.assertEqual(clean_ai_text(text), text)

    def test_dash_variants_and_explicit_bans(self):
        for dash in ['\u2014', '&mdash;', '&#8212;', '&#x2014;', '&#X2014;']:
            self.assertEqual(clean_ai_text('<p>A' + dash + 'B</p>'), '<p>A-B</p>')
        self.assertNotIn('delve', clean_ai_text('<p>We delve into the plan.</p>'))

    def test_publisher_sanitizer_preserves_guarantee_for_rejection(self):
        # Extract only the pure sanitizer; never import publisher/config/secrets.
        tree = ast.parse((ROOT / 'publisher_v2.py').read_text(encoding='utf-8'))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'sanitize_generated_copy')
        namespace = {'re': re, 'EM_DASH_PATTERN': re.compile(r'[\u2013\u2014\u2015]|&(?:mdash|ndash);|&#(?:8211|8212|8213);|&#x(?:2013|2014|2015);', re.I)}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<sanitizer>', 'exec'), namespace)
        sanitize = namespace['sanitize_generated_copy']
        self.assertEqual(sanitize({'intro': 'A&#x2014;B'}), {'intro': 'A-B'})
        self.assertEqual(sanitize('guaranteed recovery'), 'guaranteed recovery')

    def test_generator_requires_number_and_heading_order(self):
        tree = ast.parse((ROOT / 'publisher_v2.py').read_text(encoding='utf-8'))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_article_quality')
        namespace = {
            're': re, 'BASE_DIR': ROOT, 'publication_blockers': lambda *_: [],
            '_visible_word_count': lambda _: 4000,
            '_prompt_has_no_text_safeguards': lambda _: True,
            'QUALITY_BLOCKLIST': r'(?!)', 'EM_DASH_PATTERN': re.compile(r'\u2014'),
            'AI_CLICHE_PATTERN': re.compile(r'(?!)'),
        }
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<quality-validator>', 'exec'), namespace)
        data = {'title': 'Focus: 5 Practical Checks', 'meta_description': 'Focus ' + 'a' * 149,
                'sections': [{'h2': h, 'content': 'Practical copy.'} for h in [
                    'What is focus?', 'What are the signs?', 'Why does it vary?',
                    'How can you adjust?', 'How can you manage focus daily?']]}
        validate = namespace['validate_article_quality']
        self.assertFalse(any('heading' in e or 'order' in e or 'title must' in e for e in validate(data, 'Focus')))
        for heading in [
            "How can you work with your brain's need for routine every day?",
            'How can you manage focus each day?',
            'How can you manage focus day-to-day?',
            'How can you manage focus day to day?',
            'How can you manage focus daily?',
        ]:
            with self.subTest(heading=heading):
                data['sections'][4]['h2'] = heading
                self.assertFalse(any('section 5 must follow' in e for e in validate(data, 'Focus')))
        for heading in ['How can you manage focus?', 'How can you manage focus weekly?',
                        'Why does focus change every day?', 'How can you manage everydayness?']:
            with self.subTest(heading=heading):
                data['sections'][4]['h2'] = heading
                self.assertTrue(any('section 5 must follow' in e for e in validate(data, 'Focus')))
        data['sections'][4]['h2'] = 'How can you manage focus daily?'
        data['title'] = 'Focus without a number'
        self.assertIn('title must include a number', validate(data, 'Focus'))
        data['sections'][1]['h2'] = 'How can you change focus?'
        self.assertTrue(any('section 2 must follow' in e for e in validate(data, 'Focus')))


if __name__ == '__main__':
    unittest.main()
