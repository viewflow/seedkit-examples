import pytest

from jobs.tasks import send_welcome_email


@pytest.mark.django_db
def test_send_welcome_email_enqueues():
    result = send_welcome_email.enqueue("jane@example.com")
    assert result.task.name == "send_welcome_email"
