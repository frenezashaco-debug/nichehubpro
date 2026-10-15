import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from publication_checks import publication_blockers


class PublicationChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / 'articles').mkdir()
        (self.root / 'articles' / 'focus.html').touch()
        (self.root / 'about').mkdir()
        (self.root / 'about' / 'index.html').touch()

    def check(self, **data):
        return publication_blockers(data, self.root)

    def test_valid_paths(self):
        self.assertEqual(self.check(intro='<a href="../articles/focus.html">Focus</a><a href="/about/">About</a>', internal_links=[{'slug': 'focus'}]), [])

    def test_old_wordpress_url(self):
        for url in ['/focus', 'https://nichehubpro.com/focus', '//www.nichehubpro.com/focus']:
            self.assertTrue(self.check(sections=[{'content': f"<a href='{url}'>Focus</a>"}]))

    def test_missing_related_slug(self):
        self.assertTrue(self.check(related=[{'slug':'missing'}]))
        self.assertTrue(self.check(internal_links=[{'slug':'../config'}]))

    def test_faq_safety(self):
        self.assertTrue(self.check(faq=[{'answer':'Your heart is safe.'}]))

    def test_missing_inline_statistic_source(self):
        self.assertTrue(self.check(intro='<p>Improvement was 42%.</p>'))
        self.assertTrue(self.check(intro='<p>Improvement was 42 percent.</p>'))

    def test_citation_is_not_factual_certification(self):
        url='https://example.org/paper'
        self.assertEqual(self.check(intro=f'<p>42% <a href="{url}">source</a></p>',references=[{'url':url}]), [])
        self.assertTrue(self.check(intro=f'<p>42%</p><p><a href="{url}">source</a></p>',references=[{'url':url}]))

    def test_invented_result(self):
        self.assertTrue(self.check(real_example='Illustrative: Alex scored 14 points higher.'))
        self.assertEqual(self.check(real_example='Illustrative: Alex chooses 2 tasks to review.'), [])

    def test_placeholder_and_dopamine(self):
        self.assertTrue(self.check(conclusion='Remove the unsupported percentage.'))
        self.assertTrue(self.check(tldr='Your dopamine system resets every 24 hours.'))


if __name__ == '__main__':
    unittest.main()
