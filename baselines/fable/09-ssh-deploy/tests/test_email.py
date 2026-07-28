"""This project sends no transactional mail; verify the skip path."""

from django.core import mail

from core.notifications import send_transactional_email


def test_transactional_email_is_skipped(settings):
    settings.TRANSACTIONAL_EMAIL_ENABLED = False

    sent = send_transactional_email("Welcome", "Hello!", "user@example.com")

    assert sent is False
    assert len(mail.outbox) == 0


def test_transactional_email_sends_when_enabled(settings):
    settings.TRANSACTIONAL_EMAIL_ENABLED = True

    sent = send_transactional_email("Welcome", "Hello!", "user@example.com")

    assert sent is True
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["user@example.com"]
