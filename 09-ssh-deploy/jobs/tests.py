import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from jobs.tasks import log_greeting


@pytest.mark.django_db
def test_healthz(client):
    assert client.get("/healthz").status_code == 200


@pytest.mark.django_db
def test_readyz(client):
    assert client.get("/readyz").status_code == 200


@pytest.mark.django_db
def test_admin_login_page(client):
    assert client.get("/admin/login/").status_code == 200


@pytest.mark.django_db
def test_log_greeting_task_runs_inline():
    result = log_greeting.enqueue("world")
    assert result.status == "SUCCESSFUL"


@pytest.mark.django_db
def test_export_and_delete_user_data(capsys):
    user = get_user_model().objects.create_user(username="alice", password="s3cret!")

    call_command("export_user_data", user.pk)
    exported = capsys.readouterr().out
    assert "alice" in exported
    assert "password" not in exported

    call_command("delete_user_data", user.pk)
    assert not get_user_model().objects.filter(pk=user.pk).exists()
