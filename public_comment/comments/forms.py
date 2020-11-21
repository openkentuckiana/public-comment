import logging
from collections import namedtuple
from os import path

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from markdownx.forms import ImageForm
from markdownx.views import ImageUploadView
from storages.backends.s3boto3 import S3Boto3Storage

from comments.models import ClientMode, Document
from lib.regulationsgov.client import get_document

logger = logging.getLogger(__name__)


class PublicMediaStorage(S3Boto3Storage):
    default_acl = "public-read"
    file_overwrite = False
    querystring_auth = False


class MarkdownxImageForm(ImageForm):
    def _save(self, image, file_name, commit):
        unique_file_name = self.get_unique_file_name(file_name)
        full_path = path.join("markdownx", unique_file_name)

        if commit:
            storage = PublicMediaStorage()
            storage.save(full_path, image)
            return storage.url(full_path)

        image_data = namedtuple("image_data", ["path", "image"])
        return image_data(path=full_path, image=image)


ImageUploadView.form_class = MarkdownxImageForm


class DocumentCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Document
        fields = ["document_id"]

    def clean(self):
        cleaned_data = super().clean()

        document_id = cleaned_data.get("document_id")
        organization = self.user.organization

        if Document.objects.for_organization(organization=organization, document_id=document_id, deleted_at=None).count():
            raise ValidationError("You already have created this document")

        try:
            if not organization.regulations_gov_api_key:
                raise ValidationError("Missing regulations.gov API key")

            document = get_document(document_id, organization)

            if document.get("errors"):
                self.add_error("document_id", "Could not find a document with that ID")
                return cleaned_data

            self.instance.set_from_api_response(self.instance, document, organization)
        except:
            logger.exception("Could not get document info from regulations.gov")
            raise ValidationError("Could not get document info from regulations.gov")

        return cleaned_data


class DocumentUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Document
        fields = ["title", "description", "client_mode"]

    def clean(self):
        cleaned_data = super().clean()

        client_mode = cleaned_data.get("client_mode")
        organization = self.user.organization

        if client_mode == ClientMode.LIVE and not organization.regulations_gov_api_key:
            self.add_error("client_mode", "You must set an organization regulations.gov API key to enable live mode.")

        return cleaned_data


class CommentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop("document")
        super().__init__(*args, **kwargs)

    first_name = forms.CharField(label=_("Your first name"), max_length=100)
    last_name = forms.CharField(label=_("Your last name"), max_length=100)
    email = forms.EmailField(label=_("Your email"), max_length=100)
    comment = forms.CharField(label=_("Your comment"), widget=forms.Textarea)
