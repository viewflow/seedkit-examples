import msgspec
from django.contrib.auth.models import User
from django_bolt import BoltAPI
from django_bolt.exceptions import NotFound

api = BoltAPI()


class UserOut(msgspec.Struct):
    id: int
    username: str


@api.get("/users/{user_id}")
async def get_user(user_id: int) -> UserOut:
    try:
        user = await User.objects.aget(id=user_id)
    except User.DoesNotExist:
        raise NotFound(detail=f"User {user_id} not found") from None
    return UserOut(id=user.pk, username=user.username)
