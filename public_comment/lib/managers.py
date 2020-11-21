from datetime import datetime

from django.db import models
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404


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

    def for_organization(self, organization, **kwargs):
        return self.get_queryset().filter(organization=organization, **kwargs)

    def get_for_organization(self, organization, **kwargs):
        return get_object_or_404(self.get_queryset(), organization=organization, **kwargs)
