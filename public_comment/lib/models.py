from django.db import models

from lib.managers import OrganizationOwnedModelManager


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=None, blank=True, null=True)

    objects = OrganizationOwnedModelManager()
    objects_with_deleted = OrganizationOwnedModelManager(deleted=True)

    class Meta:
        abstract = True


class OrganizationOwnedModel(BaseModel):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, db_index=True)

    class Meta:
        abstract = True
