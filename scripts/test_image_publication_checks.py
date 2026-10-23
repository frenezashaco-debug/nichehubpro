import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from image_publication_checks import screen_publication_images, screen_with_regeneration, VisualRejection


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

    def raw_client(self, replies, stop_reason='end_turn'):
        self.calls = 0
        def create(**kwargs):
            self.calls += 1
            return SimpleNamespace(stop_reason=stop_reason, content=[
                SimpleNamespace(type='text', text=replies[min(self.calls - 1, len(replies) - 1)])])
        return SimpleNamespace(messages=SimpleNamespace(create=create))

    def test_markdown_wrapper(self):
        client = self.raw_client(['```json\n' + json.dumps(self.approved()) + '\n```'])
        self.assertEqual(screen_publication_images(client, self.paths, 'worry'), self.approved())
        self.assertEqual(self.calls, 1)

    def test_empty_response_retries_once(self):
        client = self.raw_client(['', json.dumps(self.approved())])
        self.assertEqual(screen_publication_images(client, self.paths, 'worry'), self.approved())
        self.assertEqual(self.calls, 2)

    def test_invalid_response_stays_blocked(self):
        with self.assertRaisesRegex(ValueError, 'invalid JSON twice'):
            screen_publication_images(self.raw_client(['not JSON']), self.paths, 'worry')
        self.assertEqual(self.calls, 2)

    def test_rejection_is_not_retried(self):
        data = self.approved()
        data['images'][0]['approved'] = False
        with self.assertRaises(ValueError):
            screen_publication_images(self.raw_client([json.dumps(data), json.dumps(self.approved())]), self.paths, 'worry')
        self.assertEqual(self.calls, 1)

    def test_invalid_types_and_truncation_fail_closed(self):
        for data in [[], {'images': [None] * 4}]:
            with self.assertRaises(ValueError):
                screen_publication_images(self.client(data), self.paths, 'worry')
        with self.assertRaisesRegex(ValueError, 'truncated'):
            screen_publication_images(self.raw_client([json.dumps(self.approved())], 'max_tokens'), self.paths, 'worry')

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

    def test_regenerates_only_rejected_asset_and_rescreens(self):
        rejected = self.approved()
        rejected['images'][2]['approved'] = False
        changed = []
        def regenerate(index):
            changed.append(index)
            Image.new('RGB', (16, 16), (200, 100, 50)).save(self.paths[index])
        client = self.raw_client([json.dumps(rejected), json.dumps(self.approved())])
        screen_with_regeneration(client, self.paths, 'worry', regenerate)
        self.assertEqual(changed, [2])
        self.assertEqual(self.calls, 2)

    def test_unchanged_rejected_asset_stays_blocked(self):
        rejected = self.approved()
        rejected['images'][0]['approved'] = False
        with self.assertRaisesRegex(ValueError, 'not replaced'):
            screen_with_regeneration(self.client(rejected), self.paths, 'worry', lambda index: None)

    def test_repeated_rejection_stays_blocked(self):
        rejected = self.approved()
        rejected['images'][0]['approved'] = False
        changed = []
        def regenerate(index):
            changed.append(index)
            Image.new('RGB', (16, 16), (150 + len(changed), 0, 0)).save(self.paths[index])
        with self.assertRaises(VisualRejection):
            screen_with_regeneration(self.client(rejected), self.paths, 'worry', regenerate)
        self.assertEqual(changed, [0, 0])


if __name__ == '__main__':
    unittest.main()
