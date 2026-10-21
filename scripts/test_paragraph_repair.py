"""Offline tests, no credentials or API calls."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paragraph_repair import repair_paragraphs, split_paragraph, words, rebalance_paragraphs


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

    def test_65_word_example_rebalanced_without_loss(self):
        sentence = lambda n: ' '.join(['word'] * n) + '.'
        original = sentence(35) + ' ' + sentence(30) + '\n\n' + sentence(20)
        result = rebalance_paragraphs(original, 2)
        parts = [p for p in result.splitlines() if p.strip()]
        self.assertEqual([words(p) for p in parts], [35, 50])
        self.assertEqual(original.split(), result.split())
        self.assertEqual(rebalance_paragraphs(result, 2), result)

    def test_impossible_example_not_truncated(self):
        original = ' '.join(['word'] * 121)
        self.assertEqual(rebalance_paragraphs(original, 2), original)

    def test_exact_counts_for_all_fixed_fields(self):
        sentence = ' '.join(['word'] * 25) + '.'
        data = {key: ' '.join([sentence] * count) for key, count in [('intro', 3), ('real_example', 2), ('conclusion', 3)]}
        result = repair_paragraphs(data)
        for key, count in [('intro', 3), ('real_example', 2), ('conclusion', 3)]:
            self.assertEqual(len([p for p in result[key].splitlines() if p]), count)
            self.assertEqual(data[key].split(), result[key].split())

    def test_numbering_moves_from_heading_to_body(self):
        data = {'sections': [{'h2': 'Check 1: What is focus?', 'content': '<p>Original advice.</p>'}]}
        result = repair_paragraphs(data)
        self.assertEqual(result['sections'][0]['h2'], 'What is focus?')
        self.assertIn('Check 1: What is focus?', result['sections'][0]['content'])
        self.assertIn('<p>Original advice.</p>', result['sections'][0]['content'])
        self.assertEqual(repair_paragraphs(result), result)


if __name__ == '__main__':
    unittest.main()
