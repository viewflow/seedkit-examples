import pytest
from django.contrib.sessions.models import Session
from django.utils import timezone

from jobs.tasks import cleanup_expired_sessions


@pytest.mark.django_db
def test_cleanup_expired_sessions_runs_inline():
    Session.objects.create(
        session_key="expired-session-key",
        session_data="",
        expire_date=timezone.now() - timezone.timedelta(days=1),
    )
    Session.objects.create(
        session_key="live-session-key",
        session_data="",
        expire_date=timezone.now() + timezone.timedelta(days=1),
    )

    result = cleanup_expired_sessions.enqueue()

    assert result.return_value == 1
    assert Session.objects.filter(session_key="live-session-key").exists()
    assert not Session.objects.filter(session_key="expired-session-key").exists()
