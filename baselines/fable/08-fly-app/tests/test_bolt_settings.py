from config.settings import bolt


def test_bolt_strips_web_stack() -> None:
    assert "django.contrib.admin" not in bolt.INSTALLED_APPS
    assert "django.contrib.sessions" not in bolt.INSTALLED_APPS
    assert "django.contrib.messages" not in bolt.INSTALLED_APPS
    assert "django.contrib.staticfiles" not in bolt.INSTALLED_APPS
    assert "django.middleware.csrf.CsrfViewMiddleware" not in bolt.MIDDLEWARE
    assert "django.contrib.sessions.middleware.SessionMiddleware" not in bolt.MIDDLEWARE
    assert bolt.TEMPLATES == []
    assert bolt.ROOT_URLCONF == "config.urls_bolt"
