import logging

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View

from . import _thread_locals

logger = logging.getLogger(__name__)


class AsyncViewMixin:
    async def __call__(self):
        return super().__call__(self)


@method_decorator(login_required, name="dispatch")
class ProtectedView(View):
    pass


class OrganizationView(ProtectedView):
    """
    Overrides get_queryset used by default views and limits results to the organization set by OrganizationMiddleware.
    **Must be the first in the list of a view's parent classes/mixins**
    """

    def get_queryset(self):
        if hasattr(super(), "get_queryset"):
            queryset = super().get_queryset()

            organization = getattr(_thread_locals, "organization")
            logger.info("Setting organization on queryset to %s (%s)", organization, organization.id)

            queryset = queryset.filter(organization=organization)
            return queryset
