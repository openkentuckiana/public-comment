import base64
import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.timezone import activate

from . import _thread_locals

logger = logging.getLogger(__name__)


class TurbolinksMiddleware(object):
    """Send the `Turbolinks-Location` header in response to a visit that was redirected,
    and Turbolinks will replace the browser's topmost history entry.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        is_turbolinks = request.META.get("HTTP_TURBOLINKS_REFERRER")
        is_response_redirect = response.has_header("Location")

        if is_turbolinks:
            if is_response_redirect:
                location = response["Location"]
                prev_location = request.session.pop("_turbolinks_redirect_to", None)
                if prev_location is not None:
                    # relative subsequent redirect
                    if location.startswith("."):
                        location = prev_location.split("?")[0] + location
                request.session["_turbolinks_redirect_to"] = location
            else:
                if request.session.get("_turbolinks_redirect_to"):
                    location = request.session.pop("_turbolinks_redirect_to")
                    response["Turbolinks-Location"] = location
        return response


class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def unauthorized(self):
        response = HttpResponse("Unauthorized", status=401)
        response["WWW-Authenticate"] = f'Basic realm="{settings.SITE_NAME} App"'
        return response

    def __call__(self, request):
        if "HTTP_AUTHORIZATION" in request.META and (settings.BASIC_AUTH_USERNAME and settings.BASIC_AUTH_PASSWORD):
            authentication = request.META["HTTP_AUTHORIZATION"]
            (method, auth) = authentication.split(" ", 1)

            if method.upper() != "BASIC":
                return self.unauthorized()

            auth = base64.b64decode(auth.strip()).decode("utf-8")
            username, password = auth.split(":", 1)
            if username == settings.BASIC_AUTH_USERNAME and password == settings.BASIC_AUTH_PASSWORD:
                return self.get_response(request)

        return self.unauthorized()


class OrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user and not request.user.is_anonymous and request.user.organization:
            logger.info(
                "Setting organization on thread to %s (%s) for user %s",
                request.user.organization,
                request.user.organization.id,
                request.user,
            )
            setattr(_thread_locals, "organization", request.user.organization)

            logger.info("Setting organization timezone to %s", request.user.organization.timezone)
            activate(request.user.organization.timezone)
        elif request.user and not request.user.is_anonymous and request.user.organization:
            # All users should have an org.
            raise PermissionDenied
        return self.get_response(request)
