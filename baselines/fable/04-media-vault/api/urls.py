"""API routes, mounted in ``config/urls.py`` under the ``api`` namespace."""

from django.urls import path
from dmr.routing import Router

from api.views import MediaController

router = Router(
    "api/",
    [
        path("media/", MediaController.as_view(), name="media"),
    ],
)
