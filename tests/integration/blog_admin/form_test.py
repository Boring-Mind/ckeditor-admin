import pytest

from src.blog_admin.forms import PostForm


# Post form
##############################################


@pytest.mark.parametrize('message,invalid_data,expected', [
    (
        "Invalid url test",
        {
            'title': 'Title',
            'description': 'Description',
            'hashtags': (
                '[{"value":"Muhammad"}]'
            ),
            'content': 'Content',
            'preview_img_url': 'htpts://example.com/',
            'post_status': 'DR'
        },
        False
    ),

    (
        "Invalid post status test",
        {
            'title': 'Title',
            'description': 'Description',
            'hashtags': (
                '[{"value":"Muhammad"}]'
            ),
            'content': 'Content',
            'preview_img_url': 'https://example.com/',
            'post_status': 'vs'
        },
        False
    ),

    (
        "Valid form data test",
        {
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
        },
        True
    )
])
def test_post_form(
    invalid_data: str, expected: bool, message: str
):
    form = PostForm(invalid_data)
    assert form.is_valid() is expected, message
