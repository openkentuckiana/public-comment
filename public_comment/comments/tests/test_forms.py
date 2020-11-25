from unittest.mock import patch

from comments.forms import DocumentCreateForm, DocumentUpdateForm
from comments.models import ClientMode
from comments.tests import UnitBaseTestCase


@patch("comments.forms.get_document")
@patch("comments.models.Document.set_from_api_response")
class DocumentCreateFormTests(UnitBaseTestCase):
    def test_fields(self, m_set_from_api_response, m_get_document):
        self.assertEqual(DocumentCreateForm.Meta.fields, ["document_id"])

    def test_creates_document(self, m_set_from_api_response, m_get_document):
        document_from_api = {}
        m_get_document.return_value = document_from_api

        form = DocumentCreateForm(user=self.org_user, data={"document_id": "new-doc"})

        self.assertTrue(form.is_valid())
        m_get_document.assert_called_once_with("new-doc", self.org_user.organization)
        m_set_from_api_response.assert_called_once_with(form.instance, document_from_api, self.org_user.organization)

    def test_prevents_duplicate_document(self, m_set_from_api_response, m_get_document):
        form = DocumentCreateForm(user=self.org_user, data={"document_id": self.org_document.document_id})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["__all__"][0], "You already have created this document")

    def test_does_not_prevent_duplicate_for_other_org(self, m_set_from_api_response, m_get_document):
        m_get_document.return_value = {}

        form = DocumentCreateForm(user=self.org_user, data={"document_id": self.other_org_document.document_id})

        self.assertTrue(form.is_valid())

    def test_returns_error_if_document_can_not_be_retrieved(self, m_set_from_api_response, m_get_document):
        m_get_document.return_value = {"errors": ["whoops"]}

        form = DocumentCreateForm(user=self.org_user, data={"document_id": "new-doc"})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["document_id"][0], "Could not find a document with that ID")

    def test_generic_exception_returns_nice_error(self, m_set_from_api_response, m_get_document):
        m_get_document.side_effect = Exception
        form = DocumentCreateForm(user=self.org_user, data={"document_id": "new-doc"})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["__all__"][0], "Could not get document info from regulations.gov")


class DocumentUpdateFormTests(UnitBaseTestCase):
    def test_fields(self):
        self.assertEqual(DocumentUpdateForm.Meta.fields, ["title", "description", "client_mode"])

    def test_updates_document(self):
        form = DocumentUpdateForm(
            user=self.org_user, data={"title": "New Title", "description": "New Description", "client_mode": ClientMode.LIVE}
        )

        self.assertTrue(form.is_valid())

    def test_prevents_live_mode_if_missing_api_key(self):
        self.org_user.organization.regulations_gov_api_key = None
        form = DocumentUpdateForm(
            user=self.org_user, data={"title": "New Title", "description": "New Description", "client_mode": ClientMode.LIVE}
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["client_mode"][0], "You must set an organization regulations.gov API key to enable live mode."
        )
