"""Smoke tests module.

This module holds smoke tests - the most valuable and fast tests
that checks the main functionality of the app.

"""


def test_server_is_running(browser):
    """Test checks that local django server is up and running."""
    browser.visit('http://127.0.0.1:8000/')
    assert browser.title == 'Blog home'
