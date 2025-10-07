from datetime import UTC
from datetime import datetime
from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework import status

from conan_the_librarian.books.models import Book
from conan_the_librarian.books.tests.factories import BookFactory
from conan_the_librarian.readers.tests.factories import ReaderFactory

pytestmark = pytest.mark.django_db


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


class TestBookViewSetCreate:
    @pytest.fixture(autouse=True)
    def setup_method(self, api_client):
        self.api_client = api_client
        self.url = reverse("books-list")

    def test_create_book_success(self):
        """Should create a new book via POST request."""
        payload = {
            "serial_number": "123456",
            "title": "The Pragmatic Programmer",
            "author": "Andrew Hunt",
        }

        response = self.api_client.post(self.url, data=payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.count() == 1

        created = Book.objects.first()
        assert created.title == payload["title"]
        assert created.author == payload["author"]
        assert created.serial_number == payload["serial_number"]
        assert created.borrower is None
        assert created.is_borrowed is False

    def test_create_book_invalid_serial_number(self):
        """Should reject invalid serial number format."""
        payload = {
            "serial_number": "ABC123",  # invalid
            "title": "Bad Book",
            "author": "No Name",
        }

        response = self.api_client.post(self.url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "serial_number" in response.data
        assert Book.objects.count() == 0


class TestBookViewSetDelete:
    @pytest.fixture(autouse=True)
    def setup_method(self, api_client):
        self.api_client = api_client

    def test_delete_book(self):
        book = BookFactory()
        url = reverse("books-detail", kwargs={"pk": book.id})
        response = self.api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Book.objects.filter(id=book.id).exists() is False

    def test_delete_nonexistent_book(self):
        url = reverse(
            "books-detail",
            kwargs={"pk": "11111111-1111-1111-1111-111111111111"},
        )
        response = self.api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_delete_borrowed_book(self):
        borrowed = BookFactory(borrower=ReaderFactory())
        url = reverse("books-detail", kwargs={"pk": borrowed.id})
        response = self.api_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete a borrowed book." in response.data["detail"]
        assert Book.objects.filter(id=borrowed.id).exists()


class TestBookBorrowReturn:
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        self.api_client = api_client

    def test_borrow_book(self):
        book = BookFactory(borrower=None)
        reader = ReaderFactory()
        url = reverse("books-borrow", kwargs={"pk": book.id})
        response = self.api_client.post(url, {"reader_id": str(reader.id)})

        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.borrower == reader
        assert book.is_borrowed is True

    def test_cannot_borrow_already_borrowed(self):
        book = BookFactory(borrower=ReaderFactory())
        url = reverse("books-borrow", kwargs={"pk": book.id})
        response = self.api_client.post(url, {"reader_id": str(book.borrower.id)})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_return_book(self):
        book = BookFactory(borrower=ReaderFactory())
        url = reverse("books-return-book", kwargs={"pk": book.id})
        response = self.api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.borrower is None
        assert book.is_borrowed is False
