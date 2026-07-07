import msgspec
from django.contrib.auth.models import User
from django_bolt import BoltAPI

api = BoltAPI()


class UserOut(msgspec.Struct):
    id: int
    username: str


@api.get("/users/{user_id}")
async def get_user(user_id: int) -> UserOut:
    user = await User.objects.aget(id=user_id)
    return UserOut(id=user.pk, username=user.username)
