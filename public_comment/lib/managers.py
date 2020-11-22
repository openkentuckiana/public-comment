import logging
from datetime import datetime

from django.db import models
from django.db.models import QuerySet

from . import _thread_locals

logger = logging.getLogger(__name__)


class SoftDeleteManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.with_deleted = kwargs.pop("deleted", False)
        super().__init__(*args, **kwargs)

    def _base_queryset(self):
        return SoftDeleteQuerySet(self.model)

    def get_queryset(self):
        qs = self._base_queryset()
        if self.with_deleted:
            return qs
        return qs.filter(deleted_at=None)


class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        return super().update(deleted_at=datetime.utcnow())

    def hard_delete(self):
        return super().delete()

    def restore(self):
        return super().update(deleted_at=None)


class OrganizationOwnedModelManager(SoftDeleteManager):
    def __init__(self, *args, **kwargs):
        self.with_deleted = kwargs.pop("deleted", False)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.model.__name__ != "Organization":
            organization = getattr(_thread_locals, "organization", None)
            if organization:
                logger.info("Setting organization on queryset to %s (%s)", organization, organization.id)
                return qs.filter(organization=organization).prefetch_related("organization")
        return qs
