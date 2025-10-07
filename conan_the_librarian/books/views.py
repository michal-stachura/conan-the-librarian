import django_filters
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from conan_the_librarian.books.models import Book
from conan_the_librarian.books.serializers import BookSerializer
from conan_the_librarian.readers.models import Reader


class BookFilter(django_filters.FilterSet):
    is_borrowed = django_filters.BooleanFilter(method="filter_is_borrowed")

    class Meta:
        model = Book
        fields = ["author"]

    def filter_is_borrowed(self, queryset, name, value):
        if value is True:
            return queryset.filter(borrower__isnull=False)
        if value is False:
            return queryset.filter(borrower__isnull=True)
        return queryset


class BookViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    View that allows retrieving a list of all books.
    """

    queryset = Book.objects.select_related("borrower").all()
    serializer_class = BookSerializer

    filterset_class = BookFilter
    search_fields = ["id", "serial_number", "title", "author"]
    ordering_fields = ["title", "author", "borrowed_at"]
    lookup_field = "id"
    lookup_url_kwarg = "pk"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_borrowed:
            raise ValidationError({"detail": _("Cannot delete a borrowed book.")})
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def borrow(self, request, pk=None):
        """
        Mark the book as borrowed by a reader (given reader_id in request.data).
        """
        book = self.get_object()

        if book.is_borrowed:
            raise ValidationError({"detail": _("This book is already borrowed.")})

        reader_id = request.data.get("reader_id")
        if not reader_id:
            raise ValidationError(
                {"detail": _("Reader ID is required to borrow a book.")},
            )

        try:
            reader = Reader.objects.get(id=reader_id)
        except Reader.DoesNotExist as err:
            raise ValidationError({"detail": _("Reader not found.")}) from err

        book.borrower = reader
        book.borrowed_at = timezone.now()
        book.save()

        return Response(
            {"detail": _("Book successfully borrowed."), "book_id": str(book.id)},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        """
        Mark the book as returned.
        """
        book = self.get_object()

        if not book.is_borrowed:
            raise ValidationError({"detail": _("This book is not currently borrowed.")})

        book.borrower = None
        book.borrowed_at = None
        book.save()

        return Response(
            {"detail": _("Book successfully returned."), "book_id": str(book.id)},
            status=status.HTTP_200_OK,
        )
