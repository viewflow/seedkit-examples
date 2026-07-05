import msgspec
from django_bolt import BoltAPI
from mailauth.contrib.user.models import EmailUser

api = BoltAPI()


class UserSchema(msgspec.Struct):
    id: int
    # `mailauth.contrib.user.EmailUser` (this project's AUTH_USER_MODEL) has no
    # `username` field — `email` is its USERNAME_FIELD, so that's what's exposed here.
    email: str


@api.get("/users/{user_id}")
async def get_user(user_id: int) -> UserSchema:
    user = await EmailUser.objects.aget(id=user_id)
    # `email` is nullable at the DB level (mailauth's model), though every
    # real row has one since it's the USERNAME_FIELD — narrow for pyright.
    return UserSchema(id=user.pk, email=user.email or "")
