import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from distribution_payload import build_pinterest_payload, campaign_url
from site_listing import render_listing_pages


class DistributionChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'articles').mkdir()
        (self.root / 'images').mkdir()
        for name in ('new-cover-v3.webp', 'specific-section-a.webp', 'specific-section-b.webp'):
            (self.root / 'images' / name).write_bytes(b'fixture')
        self.markup = ''.join(f'<img src="../images/{name}" alt="Specific scene {i}" width="800" height="450">' for i, name in enumerate(('new-cover-v3.webp', 'specific-section-a.webp', 'specific-section-b.webp')))
        (self.root / 'articles' / 'focus.html').write_text(self.markup, encoding='utf-8')
        self.article = {'slug': 'focus', 'title': 'Focus: 5 Checks', 'category': 'Productivity', 'cat_slug': 'productivity', 'excerpt': 'Useful & specific advice.', 'pins': [{'title': 'Focus', 'description': 'Plan one task.'}] * 3}

    def test_uses_actual_versioned_images_not_guessed_filenames(self):
        result = build_pinterest_payload(self.article, self.root)
        self.assertEqual(result['pins'][0]['image_url'], 'https://nichehubpro.com/images/new-cover-v3.webp')
        self.assertTrue(result['pins'][1]['image_url'].endswith('specific-section-a.webp'))
        self.assertEqual(result['canonical_url'], 'https://nichehubpro.com/articles/focus.html')
        self.assertEqual(parse_qs(urlsplit(result['article_url']).query)['utm_source'], ['pinterest'])
        self.assertEqual(len({p['article_url'] for p in result['pins']}), 3)
        self.assertEqual(result['pins'][0]['alt_text'], 'Specific scene 0')

    def test_rejects_missing_external_and_out_of_root_images(self):
        file = self.root / 'articles' / 'focus.html'
        for src in ('../images/absent.webp', 'https://example.com/cover.webp', 'http://nichehubpro.com/images/new-cover-v3.webp', '../../outside.webp'):
            file.write_text(f'<img src="{src}">' * 3, encoding='utf-8')
            with self.assertRaises(ValueError):
                build_pinterest_payload(self.article, self.root)

    def test_rejects_unsafe_copy_and_unknown_board(self):
        self.article['pins'] = [{'title': 'Focus &mdash; now', 'description': ''}]
        with self.assertRaises(ValueError):
            build_pinterest_payload(self.article, self.root)
        self.article['category'] = 'Unknown'
        with self.assertRaises(ValueError):
            build_pinterest_payload(self.article, self.root)

    def test_campaign_requires_clean_canonical(self):
        for url in ('https://evil.example/a', 'https://nichehubpro.com/a?secret=1', 'https://nichehubpro.com/a#fragment'):
            with self.assertRaises(ValueError):
                campaign_url(url, 'medium', 'referral', 'launch', 'guide')

    def test_static_hub_cards_are_escaped_and_idempotent(self):
        # One category fixture per hub, without real image processing or network.
        rows = []
        for cat, category in [('mental-wellness', 'Mental Wellness'), ('productivity', 'Productivity'), ('healthy-lifestyle', 'Healthy Lifestyle')]:
            rows.append({**self.article, 'cat_slug': cat, 'category': category, 'title': '<Focus & review>'})
        for hub in ('all-articles', 'mental-wellness', 'productivity', 'healthy-lifestyle'):
            (self.root / hub).mkdir()
            (self.root / hub / 'index.html').write_text('<div class="grid" id="article-grid"></div><div id="empty-state"></div>', encoding='utf-8')
        counts = render_listing_pages(rows, self.root)
        self.assertEqual(counts['all-articles'], 3)
        first = (self.root / 'all-articles' / 'index.html').read_text(encoding='utf-8')
        self.assertIn('&lt;Focus &amp; review&gt;', first)
        self.assertIn('/images/new-cover-v3.webp', first)
        render_listing_pages(rows, self.root)
        self.assertEqual(first, (self.root / 'all-articles' / 'index.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
