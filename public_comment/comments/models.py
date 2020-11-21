import logging
from datetime import datetime

from dateutil import tz
from django.core.exceptions import ValidationError
from django.core.serializers import serialize
from django.db import connection, models
from django.urls import reverse
from django.utils.text import Truncator, slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from lib.models import OrganizationOwnedModel

logger = logging.getLogger(__name__)


class ClientMode(models.TextChoices):
    TESTING = "T", "Testing"
    LIVE = "L", "Live"


class DocumentTopic(OrganizationOwnedModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Document(OrganizationOwnedModel):
    """
    Regulatory document the public can comment on. A notice or proposed rule.
    """

    document_id = models.CharField(max_length=100, verbose_name="Document ID")
    slug = models.SlugField()
    title = models.CharField(max_length=500)
    description = MarkdownxField(null=True, blank=True)
    is_accepting_comments = models.BooleanField(default=False)
    is_withdrawn = models.BooleanField(default=False)
    document_type = models.CharField(max_length=50)
    comment_end_date = models.DateTimeField(null=True, blank=True)
    comment_start_date = models.DateTimeField(null=True, blank=True)
    client_mode = models.CharField(
        max_length=1,
        choices=ClientMode.choices,
        default=ClientMode.TESTING,
        help_text="Switch to live when you're ready to start accepting comments and have them submitted to regulations.gov. While in testing mode, comments will be logged but not submitted.",
    )
    topics = models.ManyToManyField(DocumentTopic, related_name="documents", blank=True, db_index=True)

    class Meta:
        unique_together = [["document_id", "organization", "deleted_at"]]
        indexes = [
            models.Index(fields=["organization", "document_id"]),
            models.Index(fields=["organization", "title", "description"]),
            models.Index(fields=["organization", "document_type"]),
            models.Index(fields=["organization", "comment_end_date"]),
            models.Index(fields=["organization", "comment_start_date"]),
        ]

    def __str__(self):
        return f"{Truncator(self.title).words(5)} - {self.document_id}"

    def url(self):
        return f"https://beta.regulations.gov/document/{self.document_id}"

    def get_absolute_url(self):
        return reverse("document-detail", args=[self.slug])

    def formatted_description(self):
        return markdownify(str(self.description)) if self.description else ""

    def short_title(self):
        return Truncator(self.title).words(5)

    def comment_end_date_passed(self):
        if self.comment_end_date and self.comment_end_date <= datetime.utcnow().astimezone(tz.UTC):
            return True
        return False

    def comment_start_date_not_reached(self):
        if self.comment_start_date and self.comment_start_date >= datetime.utcnow().astimezone(tz.UTC):
            return True
        return False

    @staticmethod
    def set_from_api_response(document, api_response, organization):
        regulations_document = api_response["data"]["attributes"]

        document.slug = slugify(f"{organization.url_short_name} {api_response['data']['id']}")
        document.title = regulations_document["title"]
        document.document_type = regulations_document["documentType"]
        document.comment_start_date = regulations_document["commentStartDate"]
        document.comment_end_date = regulations_document["commentEndDate"]
        document.is_accepting_comments = regulations_document["openForComment"]
        document.is_withdrawn = regulations_document["withdrawn"]
        document.organization = organization

        document.save()

        topics = regulations_document.get("topics")
        if topics and isinstance(topics, list):
            for t in topics:
                document_topic = DocumentTopic.objects.get_or_create(name=t, organization=organization)
                document.topics.add(document_topic[0])

        document.save()


class Commenter(OrganizationOwnedModel):
    email = models.EmailField()
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.email


class Comment(OrganizationOwnedModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, db_index=True)
    commenter = models.ForeignKey(Commenter, on_delete=models.CASCADE, db_index=True)
    original_commenter = models.JSONField()
    comment = models.TextField()
    was_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    regulations_gov_response = models.JSONField(null=True, blank=True)
    client_mode = models.CharField(
        max_length=1,
        choices=ClientMode.choices,
        default=ClientMode.TESTING,
        help_text="The mode the comment was submitted under.",
        editable=False,
    )

    class Meta:
        indexes = [
            models.Index(fields=["organization", "document"]),
            models.Index(fields=["organization", "comment"]),
            models.Index(fields=["organization", "created_at"]),
        ]

    def __str__(self):
        return f"{self.document} - {self.commenter}"

    def short_comment(self):
        return Truncator(self.comment).words(15)

    def clean(self):
        if self.document.organization != self.organization:
            raise ValidationError("Comment must be in the same organization as the document it is on.")

    def save(self, *args, **kwargs):
        self.original_commenter = serialize("json", [self.commenter])
        super().save(*args, **kwargs)
