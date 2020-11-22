import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
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
    def dispatch(self, request, *args, **kwargs):
        self.organization = getattr(_thread_locals, "organization")
        if kwargs["organization_slug"] != self.organization.slug:
            raise PermissionDenied("You may not access this organization's data.")
        return super().dispatch(request, *args, **kwargs)
