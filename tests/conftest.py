"""Conftest.py - pytest config file.

Collects all the fixtures from the test packages in one place.
"""

import pytest
from .integration.blog_admin.fixtures import *
from .unit.blog_admin.fixtures import *
