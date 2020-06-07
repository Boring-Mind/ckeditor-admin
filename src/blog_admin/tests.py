from unittest.mock import MagicMock

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.urls import reverse
from django.utils.text import slugify
from faker import Faker
from model_bakery import baker
from splinter import Browser

# from .forms import PostForm
from .models import Post as PostModel
from src.blog_admin.views import RegisterView
from src.blog_admin.views import PostFormView


##############################################
# Fixtures
##############################################

@pytest.fixture(scope='module')
def browser():
    """Return an instance of chrome headless browser."""
    br = Browser("chrome", headless=True)
    yield br
    br.quit()


@pytest.fixture
@pytest.mark.django_db
def user():
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
    """Fake user data factory. Generate random user profile."""

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


def test_server_is_running(browser):
    browser.visit('http://127.0.0.1:8000/')
    assert browser.title == 'Blog home'

##############################################
# Integration tests
##############################################


##############################################
# View tests

# Register view
##############################################

@pytest.mark.django_db
def test_register_view_saves_user_and_logs_in(browser, user):
    browser.visit('http://127.0.0.1:8000/register/')
    assert browser.title == 'Register'

    browser.fill('username', user.username)
    browser.fill('email', user.email)
    browser.fill('password1', user.password)
    browser.fill('password2', user.password)

    browser.find_by_name('submit').click()
    assert browser.title == 'Blog home'

    browser.visit('http://127.0.0.1:8000/logout/')
    assert browser.title == 'Blog home'

# PostForm view
##############################################
@pytest.mark.django_db
def test_post_form_view_form_valid(client, django_user_model):
    # Create and login some user
    # in order to have access to the post create view
    user = django_user_model.objects.create_user(
        username="somename", password="p@ssw0rd"
    )
    client.login(username=user.username, password="p@ssw0rd")

    # Generate request data
    data = {
        'title': 'Title',
        'description': 'Description',
        'hashtags': (
            '[{"value":"Muhammad"},{"value":"Fernandez"},'
            '{"value":"Aida"},{"value":"Bullock"}]'
        ),
        'content': 'Content',
        'preview_img_url': 'https://example.com/apparatus/image.png',
        'post_status': 'DR'
    }

    # form = PostForm(data)

    response = client.post(reverse('create_post'), data)

    post = PostModel.objects.filter(
        title=data['title'], content=data['content']
    )

    # Testing length of a posts array
    assert len(post) == 1

    # Testing content of saved post model
    assert post[0].title == 'Title'
    assert post[0].description == 'Description'
    assert post[0].content == 'Content'
    assert post[0].preview_img_url == 'https://example.com/apparatus/image.png'
    assert post[0].post_status == 'DR'

    # Testing content of saved hashtags models
    assert len(post[0].hashtags.values()) == 4
    assert post[0].hashtags.values()[0].get('id') is not None
    assert post[0].hashtags.values()[1].get('id') is not None
    assert post[0].hashtags.values()[2].get('id') is not None
    assert post[0].hashtags.values()[3].get('id') is not None

    # Getting hashtags' text values
    hashtags_values = [tag['text'] for tag in post[0].hashtags.values()]

    # Testing saved hashtags' texts
    assert 'Muhammad' in hashtags_values
    assert 'Fernandez' in hashtags_values
    assert 'Aida' in hashtags_values
    assert 'Bullock' in hashtags_values

    # Testing response
    assert response.status_code == 302
    assert response.url == reverse('home')

##############################################
# Unit tests
##############################################

##############################################
# View tests

# Register view
##############################################
@pytest.mark.django_db
def test_register_view_returns_redirect(rf, user, django_user_model):
    # Get the request with the users data
    request = rf.post(reverse('register'), {
        'username': user.username,
        'email': user.email,
        'password': user.password
    })
    # Add session object for the proper work of login()
    request.session = SessionStore()
    request.session.create()
    # Make a new user object in order to mock the registration form
    new_user = django_user_model.objects.create_user(
        username=user.username, password=user.password
    )
    # Mock the Register form object
    form = MagicMock()
    form.save.return_value = new_user
    # Get an instance of the view and initialize it
    view = RegisterView()
    view.setup(request)

    response = view.form_valid(form)

    # When the new user object is created, it's last_login date would be None
    assert new_user.last_login is not None, \
        "User is not logged in"
    assert response.status_code == 302, \
        "Response is not redirect response"
    assert response.url == reverse('home'), \
        "Response does not redirect to the correct page"


# Unfinished test
@pytest.mark.django_db
def test_post_create_view_form_valid(rf, client, django_user_model):
    # Create and login some user
    # in order to have access to the post create view
    user = django_user_model.objects.create_user(
        username="somename", password="p@ssw0rd"
    )
    client.login()

    # Generate request data
    data = {
        'title': 'Title',
        'description': 'Description',
        'hashtags': (
            '[{"value":"Muhammad"},{"value":"Fernandez"},'
            '{"value":"Tayyib"},{"value":"Leach"},'
            '{"value":"Thelma"},{"value":"Zavala"},'
            '{"value":"Harmony"},{"value":"Lyons"},'
            '{"value":"Aida"},{"value":"Bullock"}]'
        ),
        'content': 'Content',
        'preview_img_url': 'https://example.com/apparatus/image.png',
        'post_status': 'DR'
    }

    # Get request object with data in it
    request = rf.post(reverse('create_post'), data)

    # Mock the form object
    form = MagicMock()
    form.is_valid.return_value = True
    form.cleaned_data = data
    form.save.return_value = baker.make(PostModel, make_m2m=True)


@pytest.mark.parametrize("hashtags, expected", [
    ((
        '[{"value":"Muhammad"},{"value":"Fernandez"},'
        '{"value":"Tayyib"},{"value":"Leach"},'
        '{"value":"Thelma"},{"value":"Zavala"},'
        '{"value":"Harmony"},{"value":"Lyons"},'
        '{"value":"Aida"},{"value":"Bullock"}]'
    ), [
        "Muhammad", "Fernandez", "Tayyib", "Leach", "Thelma",
        "Zavala", "Harmony", "Lyons", "Aida", "Bullock"
    ]),
    ((
        '[{"value":""},{"value":""},'
        '{"value":"Croatia Weekend 2010"},{"value":""},'
        '{"value":""},{"value":"Beautiful Landscape"}]'
    ), [
        'Croatia Weekend 2010', 'Beautiful Landscape'
    ])
])
def test_parse_hashtags(hashtags: str, expected: str):
    actual = PostFormView.parse_hashtags(hashtags)

    assert actual == expected, "Lists aren\'t equal"
