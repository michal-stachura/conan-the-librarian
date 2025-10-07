from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from conan_the_librarian.core.models import BaseModel


class Book(BaseModel):
    """Model representing a book in the library."""

    serial_number = models.CharField(
        max_length=6,
        unique=True,
        validators=[RegexValidator(r"^\d{6}$", _("Serial number must be 6 digits."))],
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    borrower = models.ForeignKey(
        "readers.Reader",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="borrowed_books",
    )
    borrowed_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_borrowed(self):
        return self.borrower_id is not None

    def __str__(self):
        return f"{self.title} ({self.serial_number})"
