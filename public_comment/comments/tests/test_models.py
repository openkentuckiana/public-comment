from datetime import datetime, timedelta

from dateutil import tz
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from comments.tests import UnitBaseTestCase


class DocumentModelTests(UnitBaseTestCase):
    def test_str_repr(self):
        self.org_document.title = "This title is short!"
        self.assertEqual(str(self.org_document), f"This title is short! - {self.org_document.document_id}")

        self.org_document.title = "This title is very very very long!"
        self.assertEqual(str(self.org_document), f"This title is very very… - {self.org_document.document_id}")

    def test_get_absolute_url(self):
        self.assertEqual(
            self.org_document.get_absolute_url(), reverse("document-detail", args=[self.org.slug, self.org_document.slug])
        )

    def test_formatted_description(self):
        self.org_document.description = "**Hello**"
        self.assertEqual(self.org_document.formatted_description(), "<p><strong>Hello</strong></p>")
        self.org_document.description = None
        self.assertEqual(self.org_document.formatted_description(), "")

    def test_short_title(self):
        self.org_document.title = "This title is short!"
        self.assertEqual(str(self.org_document.short_title()), "This title is short!")

        self.org_document.title = "This title is very very very long!"
        self.assertEqual(str(self.org_document.short_title()), "This title is very very…")

    def test_comment_end_date_passed(self):
        self.org_document.comment_end_date = datetime.utcnow().astimezone(tz.UTC)
        self.assertTrue(self.org_document.comment_end_date_passed())

        self.org_document.comment_end_date = datetime.utcnow().astimezone(tz.UTC) + timedelta(days=1)
        self.assertFalse(self.org_document.comment_end_date_passed())

    def test_comment_start_date_not_reached(self):
        self.org_document.comment_start_date = datetime.utcnow().astimezone(tz.UTC) + timedelta(days=1)
        self.assertTrue(self.org_document.comment_start_date_not_reached())

        self.org_document.comment_start_date = datetime.utcnow().astimezone(tz.UTC)
        self.assertFalse(self.org_document.comment_start_date_not_reached())

    def test_set_from_api_response(self):
        document_from_api = {
            "data": {
                "id": "new-doc",
                "attributes": {
                    "title": "new title",
                    "documentType": "new doc type",
                    "commentStartDate": "2020-10-01 06:00+00:00",
                    "commentEndDate": "2020-10-01 07:00+00:00",
                    "openForComment": False,
                    "withdrawn": False,
                    "topics": ["topic1", "topic2"],
                },
            }
        }

        self.org_document.set_from_api_response(self.org_document, document_from_api, self.org)
        self.org_document.refresh_from_db()

        self.assertEqual(self.org_document.slug, "new-doc")
        self.assertEqual(self.org_document.title, "new title")
        self.assertEqual(self.org_document.document_type, "new doc type")
        self.assertEqual(self.org_document.comment_start_date, parse_datetime("2020-10-01 06:00+00:00"))
        self.assertEqual(self.org_document.comment_end_date, parse_datetime("2020-10-01 07:00+00:00"))
        self.assertFalse(self.org_document.is_accepting_comments)
        self.assertFalse(self.org_document.is_withdrawn)
        self.assertEqual(self.org_document.organization, self.org)

        self.assertEqual(self.org_document.topics.count(), 2)
        self.assertListEqual([t.name for t in self.org_document.topics.all()], ["topic1", "topic2"])
