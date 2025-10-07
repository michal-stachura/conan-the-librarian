import uuid

from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def with_deleted(self):
        return super().get_queryset()

    def only_deleted(self):
        return super().get_queryset().filter(deleted_at__isnull=False)

    def hard_delete(self):
        return self.get_queryset().delete()


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):  # noqa: FBT002
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):  # noqa: FBT002
        # allow to use hard delete on object instance
        super().delete(using=using, keep_parents=keep_parents)
