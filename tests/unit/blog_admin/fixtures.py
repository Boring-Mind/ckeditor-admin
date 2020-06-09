import pytest
from django.conf import settings
from django.utils.text import slugify
from faker import Faker


class FakeUser:
    """Fake user data factory. Generates random user profile."""

    def __init__(self, *args, **kwargs):
        fake = Faker()
        self.username = kwargs.get('username', slugify(fake.name()))
        self.email = kwargs.get('email', fake.email())
        self.password = kwargs.get(
            'password', fake.password(length=settings.MIN_PASSWORD_LENGTH)
        )


@pytest.fixture
def user():
    """Fake user data fixture.
    
    Generate user data.
    """
    yield FakeUser()
