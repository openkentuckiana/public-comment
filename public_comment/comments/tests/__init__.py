from django.test import TestCase

from comments.models import Document
from organizations.models import Organization, User


class UnitBaseTestCase(TestCase):
    org = None
    org_user = None
    other_org = None
    other_org_user = None
    org_document = None
    other_org_document = None

    @classmethod
    def setUpTestData(cls):
        cls.org = Organization.objects.create(
            name="Org 1", slug="org-1", organization_url="https://1.org", regulations_gov_api_key="123"
        )
        cls.org_user = User.objects.create(is_active=True, username="eleanor@shellstrop.com", organization=cls.org)

        cls.other_org = Organization.objects.create(
            name="Other org", slug="other-org", organization_url="https://other.org", regulations_gov_api_key="123"
        )
        cls.other_org_user = User.objects.create(is_active=True, username="chidi@anagonye.com", organization=cls.other_org)

        cls.org_document = Document.objects.create(
            document_id="abc123", slug="abc123", title="Org doc", document_type="Notice", organization=cls.org
        )
        cls.other_org_document = Document.objects.create(
            document_id="xyz789", slug="xyz789", title="Other org doc", document_type="Notice", organization=cls.other_org
        )

    def setUp(self):
        self.org.refresh_from_db()
        self.org_user.refresh_from_db()
        self.other_org.refresh_from_db()
        self.other_org_user.refresh_from_db()
        self.org_document.refresh_from_db()
        self.other_org_document.refresh_from_db()
