import uuid

from django.test import TestCase


class MediaControllerTests(TestCase):
    def test_post_returns_uid_and_filename(self):
        response = self.client.post(
            '/api/media/',
            data={'filename': 'clip.mp4', 'size': 1024},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload['filename'], 'clip.mp4')
        self.assertTrue(uuid.UUID(payload['uid']))
