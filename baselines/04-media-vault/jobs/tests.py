from django.test import TestCase

from jobs.tasks import process_media


class ProcessMediaTests(TestCase):
    def test_returns_summary(self):
        result = process_media.func('clip.mp4', 1024)
        self.assertEqual(result, 'processed clip.mp4 (1024 bytes)')
