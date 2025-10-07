from datetime import UTC
from datetime import datetime
from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework import status

from conan_the_librarian.books.models import Book
from conan_the_librarian.books.tests.factories import BookFactory
from conan_the_librarian.readers.tests.factories import ReaderFactory


@pytest.mark.django_db
class TestBookViewSetList:
    @pytest.fixture(autouse=True)
    def setup_method(self, api_client):
        self.api_client = api_client
        self.url = reverse("books-list")

    def test_list_returns_all_books(self):
        """Should return all books in paginated response"""
        BookFactory.create_batch(3)
        response = self.api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 3  # noqa: PLR2004

    def test_pagination_page_size_limit(self, settings):
        """Should respect PAGE_SIZE defined in DRF settings"""
        settings.REST_FRAMEWORK["PAGE_SIZE"] = 5

        BookFactory.create_batch(12)
        response = self.api_client.get(f"{self.url}?page_size=5")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 5  # noqa: PLR2004
        assert "next" in response.data

    def test_filter_by_author_exact(self):
        """Should filter books by exact author name"""
        BookFactory(author="John Doe")
        BookFactory(author="Jane Doe")
        response = self.api_client.get(self.url, {"author": "John Doe"})

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert all(book["author"] == "John Doe" for book in results)
        assert len(results) == 1

    def test_filter_borrowed_and_available_books(self):
        """Should return only borrowed or available books depending on filter"""
        borrowed = BookFactory(borrower=ReaderFactory())
        available = BookFactory(borrower=None)

        borrowed_response = self.api_client.get(self.url, {"is_borrowed": True})
        available_response = self.api_client.get(self.url, {"is_borrowed": False})

        assert all(
            book["is_borrowed"] is True for book in borrowed_response.data["results"]
        )
        assert all(
            book["is_borrowed"] is False for book in available_response.data["results"]
        )
        assert borrowed.id != available.id  # sanity check

    def test_search_by_title_and_author(self):
        """Should support search via DRF SearchFilter"""
        BookFactory(title="Python for Pros", author="John Smith")
        BookFactory(title="Django for Dummies", author="Jane Brown")
        response = self.api_client.get(self.url, {"search": "Django"})

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["title"] == "Django for Dummies"

    @pytest.mark.parametrize("ordering", ["title", "-borrowed_at"])
    def test_ordering_fields(self, ordering):
        """Should correctly order books by given fields"""
        Book.objects.all().delete()

        now = datetime.now(tz=UTC)
        older = now - timedelta(days=10)

        # Deterministic dataset
        BookFactory(title="A Book", borrowed_at=older)
        BookFactory(title="Z Book", borrowed_at=now)

        response = self.api_client.get(self.url, {"ordering": ordering})
        assert response.status_code == status.HTTP_200_OK

        results = response.data["results"]
        titles = [book["title"] for book in results]

        if ordering == "title":
            # Lexicographic order by title
            assert titles == ["A Book", "Z Book"]

        elif ordering == "-borrowed_at":
            # Descending by borrowed_at (newest first)
            assert titles == ["Z Book", "A Book"]
