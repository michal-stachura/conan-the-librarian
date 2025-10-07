from rest_framework import serializers

from conan_the_librarian.books.models import Book


class BookSerializer(serializers.ModelSerializer):
    is_borrowed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "serial_number",
            "title",
            "author",
            "borrowed_at",
            "is_borrowed",
        ]
