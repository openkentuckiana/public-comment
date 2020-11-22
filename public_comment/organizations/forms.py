import logging

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UsernameField
from django.core.exceptions import ValidationError

from comments.models import ClientMode, Document
from organizations.models import Organization, User

logger = logging.getLogger(__name__)


class LoginForm(AuthenticationForm):
    username = UsernameField(label="Email address", widget=forms.TextInput(attrs={"autofocus": True, "type": "email"}))
    password = forms.CharField(label="Password", max_length=100, widget=forms.PasswordInput())


class UserUpdateForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"autocomplete": "given-name", "autofocus": True}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"autocomplete": "family-name"}))

    old_password = forms.CharField(
        label="Old password",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    field_order = ["first_name", "last_name", "old_password", "new_password1", "new_password2"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        kwargs["initial"] = {"first_name": self.user.first_name, "last_name": self.user.last_name}
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        old_password = cleaned_data.get("old_password")
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1:
            if not self.user.check_password(old_password):
                raise ValidationError("Your old password was entered incorrectly. Please enter it again.")

            if password1 and password2:
                if password1 != password2:
                    raise ValidationError("The two password fields didn’t match.")
            password_validation.validate_password(password2, self.user)

        return cleaned_data

    def save(self, commit=True):
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        password = self.cleaned_data.get("new_password1")
        if password:
            self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class OrganizationUpdateForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            "name",
            "organization_url",
            "regulations_gov_api_key",
            "timezone",
            "comment_page_header",
            "thank_you_page_content",
        ]

    def clean(self):
        cleaned_data = super().clean()

        api_key = cleaned_data.get("regulations_gov_api_key")
        has_live_documents = Document.objects.filter(organization=self.instance, client_mode=ClientMode.LIVE).count()

        if has_live_documents and not api_key:
            self.add_error("regulations_gov_api_key", "Cannot remove API key while documents are in live mode.")

        return cleaned_data
