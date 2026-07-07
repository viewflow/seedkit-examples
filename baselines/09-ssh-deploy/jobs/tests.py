from django.test import TestCase

from jobs.tasks import log_greeting


class LogGreetingTaskTests(TestCase):
    def test_enqueues(self):
        result = log_greeting.enqueue("world")
        self.assertEqual(result.args, ["world"])
