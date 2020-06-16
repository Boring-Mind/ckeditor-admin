import pytest
from django.urls import reverse

from src.blog_admin.models import Post as PostModel


# Register view
##############################################


@pytest.mark.django_db
def test_register_view_saves_user_and_logs_in(browser, user_with_delete):
    browser.visit('http://127.0.0.1:8000/register/')
    assert browser.title == 'Register'

    browser.fill('username', user_with_delete.username)
    browser.fill('email', user_with_delete.email)
    browser.fill('password1', user_with_delete.password)
    browser.fill('password2', user_with_delete.password)

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

    response = client.post(reverse('create_post'), data)

    post = PostModel.objects.filter(
        title=data['title'], content=data['content']
    )

    # Testing length of a posts array
    assert len(post) == 1, "There must be one post object."

    # Testing content of saved post model
    assert post[0].title == 'Title'
    assert post[0].description == 'Description'
    assert post[0].content == 'Content'
    assert post[0].preview_img_url == 'https://example.com/apparatus/image.png'
    assert post[0].post_status == 'DR'

    # Shortcut for the statements below
    hashtags = post[0].hashtags.values()

    # Testing content of saved hashtags models
    assert len(hashtags) == 4, \
        "There must be four hashtags linked with post"

    # Getting hashtags' text values
    hashtags_values = [tag['text'] for tag in hashtags]

    # Testing saved hashtags' texts
    assert 'Muhammad' in hashtags_values
    assert 'Fernandez' in hashtags_values
    assert 'Aida' in hashtags_values
    assert 'Bullock' in hashtags_values

    # Testing response
    assert response.status_code == 302
    assert response.url == reverse('home')
