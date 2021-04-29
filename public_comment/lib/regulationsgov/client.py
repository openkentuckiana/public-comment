import hashlib
import logging

import httpx
import respx
from django.conf import settings
from httpx import Response

from comments.models import ClientMode, Comment
from organizations.models import Organization

logger = logging.getLogger(__name__)

API_BASE_URL = "https://api-staging.regulations.gov" if settings.USE_STAGING_REGULATIONS_API else "https://api.regulations.gov"


def submit_comment(comment: Comment):
    m = hashlib.md5()
    m.update(f"{comment.id}_{comment.document.document_id}".encode("utf-8"))
    uid = m.hexdigest()

    with get_context(comment.client_mode):
        url = f"{API_BASE_URL}/v4/comments"

        comment_submission = {
            "data": {
                "type": "comments",
                "attributes": {
                    "comment": comment.comment,
                    "commentOnDocumentId": comment.document.document_id,
                    "submissionKey": uid,
                    "submissionType": "API",
                    "firstName": comment.commenter.first_name,
                    "lastName": comment.commenter.last_name,
                    "email": comment.commenter.email,
                    "sendEmailReceipt": True,
                    "submitterType": "INDIVIDUAL",
                },
            }
        }

        if comment.client_mode == ClientMode.TESTING:
            respx.post(url).mock(return_value=Response(204, json={"testing_mode": True}))

        response = httpx.post(
            url,
            headers={"X-Api-Key": comment.organization.regulations_gov_api_key, "Content-Type": "application/vnd.api+json"},
            json=comment_submission,
        )

        return response


def get_document(document_id: str, organization: Organization):
    response = httpx.get(
        f"{API_BASE_URL}/v4/documents/{document_id}", headers={"X-Api-Key": organization.regulations_gov_api_key}
    )
    return response.json()


def get_context(mode: ClientMode):
    if mode == ClientMode.TESTING:
        return respx.mock
    return httpx.Client()
