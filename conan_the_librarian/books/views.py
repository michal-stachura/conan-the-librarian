import django_filters
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from conan_the_librarian.books.models import Book
from conan_the_librarian.books.serializers import BookSerializer


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


class BookViewSet(ListModelMixin, GenericViewSet):
    """
    View that allows retrieving a list of all books.
    """

    queryset = Book.objects.select_related("borrower").all()
    serializer_class = BookSerializer

    filterset_class = BookFilter
    search_fields = ["id", "serial_number", "title", "author"]
    ordering_fields = ["title", "author", "borrowed_at"]
