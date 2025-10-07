import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BooksConfig(AppConfig):
    name = "conan_the_librarian.books"
    verbose_name = _("Books")

    def ready(self):
        with contextlib.suppress(ImportError):
            import conan_the_librarian.books.signals  # noqa: F401, PLC0415
