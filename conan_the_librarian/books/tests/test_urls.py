import pytest
from django.urls import resolve
from django.urls import reverse

from conan_the_librarian.books.tests.factories import BookFactory

pytestmark = pytest.mark.django_db


class TestBookUrls:
    def test_list(self):
        assert reverse("books-list") == "/api/books/"
        assert resolve("/api/books/").view_name == "books-list"

    def test_detail_url(self):
        """
        books-detail should resolve correctly for given UUID.
        """
        book = BookFactory()
        expected_path = f"/api/books/{book.id}/"
        assert reverse("books-detail", kwargs={"pk": book.id}) == expected_path
        assert resolve(expected_path).view_name == "books-detail"

    def test_borrow_action_url(self):
        """books-borrow should resolve correctly for given UUID."""
        book = BookFactory()
        expected_path = f"/api/books/{book.id}/borrow/"
        assert reverse("books-borrow", kwargs={"pk": book.id}) == expected_path
        match = resolve(expected_path)
        assert match.view_name == "books-borrow"

    def test_return_action_url(self):
        """books-return-book should resolve correctly for given UUID."""
        book = BookFactory()
        expected_path = f"/api/books/{book.id}/return_book/"
        assert reverse("books-return-book", kwargs={"pk": book.id}) == expected_path
        match = resolve(expected_path)
        assert match.view_name == "books-return-book"
