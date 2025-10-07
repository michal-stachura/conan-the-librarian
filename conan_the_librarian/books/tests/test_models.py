import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from conan_the_librarian.books.models import Book
from conan_the_librarian.books.tests.factories import BookFactory
from conan_the_librarian.readers.tests.factories import ReaderFactory

SERIAL_LENGTH = 6


@pytest.mark.django_db
class TestBookModel:
    def test_create_book(self):
        book = BookFactory()

        assert isinstance(book, Book)
        assert len(book.serial_number) == SERIAL_LENGTH
        assert book.borrower is None
        assert book.is_borrowed is False

    def test_str_representation(self):
        book = BookFactory(serial_number="654321", title="Dune")

        assert str(book) == "Dune (654321)"

    def test_is_borrowed_property_true(self):
        reader = ReaderFactory()
        book = BookFactory(borrower_id=reader.id, borrowed_at=timezone.now())

        assert book.is_borrowed is True

    def test_serial_number_validation(self):
        book = Book(serial_number="ABC123", title="Invalid", author="Author")
        with pytest.raises(ValidationError):
            book.full_clean()

    def test_unique_serial_number_constraint(self):
        BookFactory(serial_number="999999")
        with pytest.raises(IntegrityError):
            BookFactory(serial_number="999999")

    def test_soft_delete_marks_deleted_at(self):
        book = BookFactory()

        assert book.deleted_at is None
        book.delete()
        assert book.deleted_at is not None
        assert Book.objects.filter(id=book.id).count() == 0
        assert Book.objects.with_deleted().filter(id=book.id).count() == 1
