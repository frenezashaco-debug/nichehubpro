import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clean_ai_text import clean_ai_text, visible_word_hyphens


class CleanArticleTextTests(unittest.TestCase):
    def test_rewrites_visible_hyphenated_words_without_touching_urls(self):
        markup = (
            '<p>A five-step, time-blocking plan.</p>'
            '<a href="/articles/time-blocking-for-beginners.html">Related guide</a>'
            '<script>const route = "time-blocking-for-beginners";</script>'
        )
        cleaned = clean_ai_text(markup)
        self.assertIn('five step, time blocking plan', cleaned)
        self.assertIn('/articles/time-blocking-for-beginners.html', cleaned)
        self.assertIn('"time-blocking-for-beginners"', cleaned)
        self.assertEqual(visible_word_hyphens(cleaned), 0)

    def test_rewrites_unicode_dashes_in_visible_copy(self):
        cleaned = clean_ai_text('<p>A low‑pressure choice—with room to adapt.</p>')
        self.assertEqual(cleaned, '<p>A low pressure choice with room to adapt.</p>')


if __name__ == '__main__':
    unittest.main()
