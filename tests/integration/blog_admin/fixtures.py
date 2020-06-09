import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import slugify
from faker import Faker
from splinter import Browser


@pytest.fixture(scope='module')
def browser():
    """Return an instance of chrome headless browser."""
    br = Browser("chrome", headless=True)
    yield br
    br.quit()


@pytest.fixture
@pytest.mark.django_db
def user_with_delete():
    """Fake user data fixture.
    
    Generate user data and remove it from the db after work.
    """
    fake = Faker()
    u = FakeUser(
        slugify(fake.name()),
        fake.email(),
        fake.password(length=settings.MIN_PASSWORD_LENGTH)
    )
    yield u
    if len(User.objects.filter(username=u.username).values()) > 0:
        User.objects.filter(username=u.username).delete()


class FakeUser:
    """Fake user data factory. Generates random user profile."""

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
