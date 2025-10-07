import pytest
from rest_framework.test import APIClient

from conan_the_librarian.users.models import User
from conan_the_librarian.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def api_client():
    """Provides DRF APIClient instance."""
    return APIClient()
