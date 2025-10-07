import factory

from conan_the_librarian.books.models import Book


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    serial_number = factory.Sequence(lambda n: f"{n:06d}")
    title = factory.Faker("sentence", nb_words=3)
    author = factory.Faker("name")
    borrower = None
    borrowed_at = None
