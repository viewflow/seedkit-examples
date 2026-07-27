import msgspec
from django_bolt import BoltAPI

# Import the concrete model — get_user_model() returns a generic type that
# hides `.id` / `.email` from pyright. The project's user model is
# mailauth's EmailUser (no username field — auth is email-only).
from mailauth.contrib.user.models import EmailUser

api = BoltAPI()


class UserSchema(msgspec.Struct):
    id: int
    username: str


@api.get("/users/{user_id}")
async def get_user(user_id: int) -> UserSchema:
    user = await EmailUser.objects.aget(id=user_id)
    return UserSchema(id=user.pk, username=str(user.email))
