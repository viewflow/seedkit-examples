import pytest


@pytest.mark.django_db
def test_login_page_loads(client):
    assert client.get("/accounts/login/").status_code == 200


@pytest.mark.django_db
def test_create_user_by_email():
    from users.models import User

    user = User.objects.create_user(email="jane@example.com", password="s3cr3t-pw!")
    assert user.email == "jane@example.com"
    assert user.check_password("s3cr3t-pw!")
