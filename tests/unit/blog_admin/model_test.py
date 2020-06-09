import pytest
from model_bakery import baker


@pytest.mark.django_db
def test_post_model_string(freezer):
    """Test Post model __str__ function.
    
    Freezer is needed because post_date field in Post model
    is set to auto_now_add=True,
    which says that the date is automatically set to now.
    We don't know, how your 'now' looks like.
    """
    expected = "01.01.2020 00:00 - \"New Django version is coming\""
    
    freezer.move_to('2020-01-01 00:00:00')
    post_model = baker.make(
        'Post',
        title='New Django version is coming'
    )

    assert str(post_model) == expected
