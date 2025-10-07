import factory

from conan_the_librarian.readers.models import Reader


class ReaderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reader

    card_number = factory.Sequence(lambda n: f"{n:06d}")
    name = factory.Faker("name")
