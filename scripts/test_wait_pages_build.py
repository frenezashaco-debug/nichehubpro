import unittest
from unittest.mock import Mock
from wait_pages_build import wait_for_build


class PagesTests(unittest.TestCase):
    def session(self, builds):
        session = Mock()
        session.get.side_effect = [Mock(json=Mock(return_value=b)) for b in builds]
        return session

    def test_waits_for_exact_commit(self):
        session = self.session([{'commit': 'old', 'status': 'built'},
                                {'commit': 'new', 'status': 'building'},
                                {'commit': 'new', 'status': 'built'}])
        wait_for_build(session, 'https://example.test/pages', 'new', 3, Mock())
        self.assertEqual(session.get.call_count, 3)
        session.post.assert_called_once()

    def test_failed_build_blocks_distribution(self):
        session = self.session([{'commit': 'new', 'status': 'errored'}])
        with self.assertRaises(RuntimeError):
            wait_for_build(session, 'https://example.test/pages', 'new', 1, Mock())

    def test_old_build_never_counts_as_success(self):
        session = self.session([{'commit': 'old', 'status': 'built'}])
        with self.assertRaises(RuntimeError):
            wait_for_build(session, 'https://example.test/pages', 'new', 1, Mock())


if __name__ == '__main__':
    unittest.main()
