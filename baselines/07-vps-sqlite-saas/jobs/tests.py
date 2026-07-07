from django.test import TestCase

from jobs.tasks import log_greeting


class LogGreetingTaskTests(TestCase):
    def test_enqueue_runs_immediately_in_tests(self):
        result = log_greeting.enqueue("world")

        self.assertEqual(result.status, "SUCCESSFUL")
