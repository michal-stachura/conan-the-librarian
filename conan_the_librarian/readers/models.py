from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from conan_the_librarian.core.models import BaseModel


class Reader(BaseModel):
    """Model representing a library reader."""

    card_number = models.CharField(
        max_length=6,
        unique=True,
        validators=[RegexValidator(r"^\d{6}$", _("Card number must be 6 digits."))],
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.card_number})"
