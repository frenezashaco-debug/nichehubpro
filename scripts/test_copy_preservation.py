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


if __name__ == '__main__':
    unittest.main()
