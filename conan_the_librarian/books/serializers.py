from rest_framework import serializers

from conan_the_librarian.books.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "serial_number",
            "title",
            "author",
            "borrower",
            "borrowed_at",
            "is_borrowed",
            "created_at",
        ]
        read_only_fields = ["id", "is_borrowed", "created_at"]
