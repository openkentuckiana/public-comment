import logging
from datetime import datetime

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from httpx import HTTPStatusError, RequestError

from comments.models import Comment
from lib.regulationsgov import client

logger = logging.getLogger(__name__)


class RetryableHTTPStatusError(HTTPStatusError):
    pass


@shared_task(
    autoretry_for=(RequestError, RetryableHTTPStatusError), retry_backoff=10, retry_backoff_max=30 * 60, retry_jitter=True
)
def submit_comment(comment_id):
    comment = Comment.objects.get(id=comment_id)
    logger.info("Found comment %s", comment)

    if comment.was_submitted:
        logger.info("Comment already submitted %s", comment)
        return

    # Submit comment to regulations.gov
    try:
        response = client.submit_comment(comment)
        response.raise_for_status()
        comment.regulations_gov_response = response.json()
        comment.was_submitted = True
        comment.submitted_at = datetime.now()
        comment.save()
    except HTTPStatusError as exc:
        # Retry for server issues
        if exc.response.status_code >= 500:
            raise RetryableHTTPStatusError(str(exc), request=exc.request, response=exc.response)
        else:
            raise Exception(f"Could not submit comment: {exc}")

    # Confirm
    template = "comments/comment-submitted-email.txt"
    html_template = "comments/comment-submitted-email.html"

    subject, to = (_(f"Your comment has been submitted"), comment.commenter.email)
    msg = EmailMultiAlternatives(subject, render_to_string(template, {}), None, [to])
    msg.attach_alternative(render_to_string(html_template, {}), "text/html")
    msg.send()
