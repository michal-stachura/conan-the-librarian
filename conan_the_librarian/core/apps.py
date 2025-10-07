import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = "conan_the_librarian.core"
    verbose_name = _("Core")

    def ready(self):
        with contextlib.suppress(ImportError):
            import conan_the_librarian.core.signals  # noqa: F401, PLC0415
