import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReadersConfig(AppConfig):
    name = "conan_the_librarian.readers"
    verbose_name = _("Readers")

    def ready(self):
        with contextlib.suppress(ImportError):
            import conan_the_librarian.readers.signals  # noqa: F401, PLC0415
