import pytest

from jobs.tasks import log_greeting


@pytest.mark.django_db
def test_log_greeting_enqueues():
    result = log_greeting.enqueue("world")
    assert result.task.module_path == "jobs.tasks.log_greeting"
