import ast
import html
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
            're': re, 'html': html, 'BASE_DIR': ROOT, 'publication_blockers': lambda *_: [],
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
        namespace['QUALITY_BLOCKLIST'] = r'\b(?:cure(?:s|d)?|guaranteed)\b'
        for sentence in ['This is not a cure.', '<p>This routine is not a cure.</p>',
                         'This is not a guaranteed outcome.',
                         'This is an example of how modest structural changes may support mental steadiness, not a guaranteed clinical outcome.',
                         'This is not a guaranteed medical result.',
                         'This is not a guaranteed long-term health outcome.',
                         '<p>This is not a guaranteed <strong>clinical</strong> outcome.</p>',
                         'This is one possible pattern, not a guaranteed outcome, and what helps one person may need to be adapted by another.',
                         '<p>This is not a <strong>guaranteed</strong> outcome.</p>',
                         'Results are not guaranteed.', 'Improvement is not guaranteed.']:
            data['intro'] = sentence
            self.assertFalse(any('prohibited absolute' in e for e in validate(data, 'Focus')))
        for sentence in ['This cures anxiety.', 'This is not a cure, but it cures anxiety.',
                         'This is not a cure. It cures anxiety.', 'It is guaranteed.',
                         'This is not a cure for anxiety.', 'This cured anxiety.',
                         'This is a guaranteed outcome.',
                         'This is a guaranteed clinical outcome.',
                         'This is not a guaranteed clinical outcome, but it cures anxiety.',
                         'This is not a guaranteed clinical outcome, but recovery is guaranteed.',
                         'This is not a guaranteed clinical outcome unless you follow the plan.',
                         'This is not a guaranteed clinical outcome until you follow the plan.',
                         'This is not a guaranteed clinical outcome except when used daily.',
                         'This is not a guaranteed cure outcome.',
                         'This is not a guaranteed outcome, but it cures anxiety.',
                         'This is one pattern, not a guaranteed outcome, but a guaranteed cure.',
                         'This is not a guaranteed outcome unless you follow the plan.',
                         'This is not a guaranteed outcome. It cures anxiety.',
                         'Results are not guaranteed unless you follow every step.',
                         'Results are guaranteed.']:
            with self.subTest(sentence=sentence):
                data['intro'] = sentence
                errors = validate(data, 'Focus')
                self.assertTrue(any('prohibited absolute' in e and 'context:' in e for e in errors))
        namespace['QUALITY_BLOCKLIST'] = r'(?!)'
        data['title'] = 'Focus without a number'
        self.assertIn('title must include a number', validate(data, 'Focus'))
        data['sections'][1]['h2'] = 'How can you change focus?'
        self.assertTrue(any('section 2 must follow' in e for e in validate(data, 'Focus')))


if __name__ == '__main__':
    unittest.main()
