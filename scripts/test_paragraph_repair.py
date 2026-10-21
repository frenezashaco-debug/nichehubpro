"""Offline tests, no credentials or API calls."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paragraph_repair import repair_paragraphs, split_paragraph, words


class ParagraphRepairTests(unittest.TestCase):
    def test_lossless_split(self):
        sentence = ' '.join(['word'] * 24) + '.'
        original = ' '.join([sentence] * 4)
        fixed = split_paragraph(original, '\n')
        self.assertEqual(' '.join(fixed.split()), ' '.join(original.split()))
        self.assertTrue(all(words(p) <= 60 for p in fixed.splitlines()))

    def test_link_and_emphasis_preserved(self):
        sentence = ' '.join(['word'] * 20) + '.'
        content = '<p>' + sentence + ' <a href="/articles/test.html"><strong>Link. Label</strong></a> ' + sentence + ' ' + sentence + '</p>'
        data = {'sections': [{'content': content}], 'intro': content}
        fixed = repair_paragraphs(data)
        self.assertIn('<a href="/articles/test.html"><strong>Link. Label</strong></a>', fixed['sections'][0]['content'])
        self.assertGreater(fixed['sections'][0]['content'].count('<p>'), 1)
        self.assertEqual(data['sections'][0]['content'], content)
        self.assertEqual(fixed['intro'], content)

    def test_unsplittable_sentence_not_truncated(self):
        text = ' '.join(['word'] * 70)
        self.assertEqual(split_paragraph(text, '\n'), text)

    def test_short_unchanged(self):
        self.assertEqual(split_paragraph('Short paragraph.', '\n'), 'Short paragraph.')


if __name__ == '__main__':
    unittest.main()
