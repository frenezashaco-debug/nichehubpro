import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from image_publication_checks import screen_publication_images


class ImagePublicationChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.paths = []
        for index in range(4):
            file = Path(self.directory.name) / f'image-{index}.png'
            Image.new('RGB', (16, 16), (index * 40, 20, 30)).save(file)
            self.paths.append(file)

    def client(self, data):
        def create(**kwargs):
            self.assertEqual(sum(item['type'] == 'image' for item in kwargs['messages'][0]['content']), 4)
            return SimpleNamespace(content=[SimpleNamespace(type='text', text=json.dumps(data))])
        return SimpleNamespace(messages=SimpleNamespace(create=create))

    def approved(self):
        return {'images': [{'index': i, 'approved': True, 'issues': []} for i in range(4)]}

    def test_four_visual_results_required(self):
        self.assertEqual(screen_publication_images(self.client(self.approved()), self.paths, 'worry'), self.approved())
        with self.assertRaises(ValueError):
            screen_publication_images(self.client({'images': []}), self.paths, 'worry')

    def test_visible_watermark_blocks_publication(self):
        data = self.approved()
        data['images'][2] = {'index': 2, 'approved': False, 'issues': ['visible watermark']}
        with self.assertRaisesRegex(ValueError, 'watermark'):
            screen_publication_images(self.client(data), self.paths, 'worry')

    def test_contradictory_approval_and_duplicate_indices_rejected(self):
        data = self.approved()
        data['images'][0]['issues'] = ['logo']
        with self.assertRaises(ValueError):
            screen_publication_images(self.client(data), self.paths, 'worry')
        data = self.approved()
        data['images'][0]['index'] = 1
        with self.assertRaises(ValueError):
            screen_publication_images(self.client(data), self.paths, 'worry')

    def test_duplicate_files_rejected_before_api_call(self):
        with self.assertRaisesRegex(ValueError, 'distinct'):
            screen_publication_images(None, [self.paths[0]] * 4, 'worry')

    def test_missing_results_do_not_approve(self):
        with self.assertRaises(ValueError):
            screen_publication_images(self.client({}), self.paths, 'worry')


if __name__ == '__main__':
    unittest.main()
