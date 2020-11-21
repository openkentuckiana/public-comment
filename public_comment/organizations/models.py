import pytz
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from lib.models import BaseModel


class UserManager(BaseUserManager):
    def create_superuser(self, email, organization_name, password=None):
        organization = Organization.objects.get_or_create(name=organization_name, url_short_name=organization_name)
        user = self.create_user(email, password=password, organization=organization)
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser, BaseModel):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.PROTECT)

    objects = UserManager()

    REQUIRED_FIELDS = ["organization"]


class Organization(BaseModel):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    name = models.CharField(max_length=255)
    url_short_name = models.CharField(
        max_length=30, help_text="Something short to use in the URL of this org's documents (eg. ACLU)."
    )
    organization_url = models.URLField()
    regulations_gov_api_key = models.CharField(max_length=255, blank=True, null=True)
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default="America/New_York")
    comment_page_header = MarkdownxField(
        verbose_name="Content to appear above the document description on the content form.", null=True, blank=True
    )
    thank_you_page_content = MarkdownxField(
        verbose_name="The content you want to display after someone submits a comment.", null=True, blank=True
    )

    def __str__(self):
        return self.name

    def formatted_comment_page_header(self):
        return markdownify(str(self.comment_page_header)) if self.comment_page_header else None

    def formatted_thank_you_page_content(self):
        return markdownify(str(self.thank_you_page_content)) if self.thank_you_page_content else None
