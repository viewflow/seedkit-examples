from decimal import Decimal

import pytest

from shop.models import Product
from users.models import User


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(email="buyer@example.com", password="s3cret-passphrase")


@pytest.fixture
def product(db) -> Product:
    return Product.objects.create(
        name="Enamel Mug",
        slug="enamel-mug",
        description="Holds coffee. Survives being dropped.",
        price=Decimal("18.00"),
    )
