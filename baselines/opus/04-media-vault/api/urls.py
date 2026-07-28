"""API routes, collected into a ``dmr`` router so OpenAPI can see them."""

from dmr.routing import Router, path

from api.controllers import MediaController

app_name = "api"

router = Router(
    "api/",
    [
        path("media/", MediaController.as_view(), name="media"),
    ],
)
