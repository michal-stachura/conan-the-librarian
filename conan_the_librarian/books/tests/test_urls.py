import pytest
from django.urls import resolve
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestBookUrls:
    def test_list(self):
        assert reverse("books-list") == "/api/books/books/"
        assert resolve("/api/books/books/").view_name == "books-list"
