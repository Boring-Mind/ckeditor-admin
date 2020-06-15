from unittest.mock import MagicMock

import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.urls import reverse
# from model_bakery import baker

# from src.blog_admin.models import Post as PostModel
from src.blog_admin.views import RegisterView, PostFormView


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

# PostForm view
##############################################


def test_post_form_view_form_invalid(rf):
    # Making an empty response with correct url
    request = rf.post(reverse('create_post'), {})
    # Setup PostFormView instance
    view = PostFormView()
    view.setup(request)
    
    # Sending to the correct url address an empty response.
    # Empty response means empty form.
    # And it means that view cannot mark the form as valid,
    # because there are required fields in it
    response = view.post(request)

    assert response.status_code == 200
    assert response.template_name[0] == 'post-create.html', \
        'View returns not a corresponding page.'
    assert response.context_data['form'].is_valid() is False, \
        'Form must be invalid.'
    assert len(response.context_data['form'].errors) > 0, \
        'There must be form errors.'

# Unfinished test
# @pytest.mark.django_db
# def test_post_create_view_form_valid(rf, client, django_user_model):
#     # Create and login some user
#     # in order to have access to the post create view
#     user = django_user_model.objects.create_user(
#         username="somename", password="p@ssw0rd"
#     )
#     client.login()

#     # Generate request data
#     data = {
#         'title': 'Title',
#         'description': 'Description',
#         'hashtags': (
#             '[{"value":"Muhammad"},{"value":"Fernandez"},'
#             '{"value":"Tayyib"},{"value":"Leach"},'
#             '{"value":"Thelma"},{"value":"Zavala"},'
#             '{"value":"Harmony"},{"value":"Lyons"},'
#             '{"value":"Aida"},{"value":"Bullock"}]'
#         ),
#         'content': 'Content',
#         'preview_img_url': 'https://example.com/apparatus/image.png',
#         'post_status': 'DR'
#     }

#     # Get request object with data in it
#     request = rf.post(reverse('create_post'), data)

#     # Mock the form object
#     form = MagicMock()
#     form.is_valid.return_value = True
#     form.cleaned_data = data
#     form.save.return_value = baker.make(PostModel, make_m2m=True)


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
