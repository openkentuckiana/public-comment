import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, View
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django_tables2.export import ExportMixin

from lib.regulationsgov.client import get_document
from lib.views import OrganizationView
from organizations.models import Organization

from . import tasks
from .filters import CommentsFilter, DocumentsFilter
from .forms import CommentForm, DocumentCreateForm, DocumentUpdateForm
from .models import Comment, Commenter, Document
from .tables import CommentsTable, DocumentsTable

logger = logging.getLogger(__name__)


class IndexView(View):
    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("org-index", args=[request.user.organization.slug]))

        return render(request, "index.html")


class OrgIndexView(OrganizationView):
    def get(self, request, organization_slug):
        if request.user.organization.slug != organization_slug:
            raise PermissionDenied

        total_document_count = Document.objects.all().count()
        documents_accepting_comments_count = Document.objects.filter(is_accepting_comments=True).count()
        total_comment_count = Comment.objects.all().count()
        comments_on_active_documents_count = Comment.objects.filter(document__is_accepting_comments=True).count()
        context = {
            "user": request.user,
            "total_document_count": total_document_count,
            "documents_accepting_comments_count": documents_accepting_comments_count,
            "total_comment_count": total_comment_count,
            "comments_on_active_documents_count": comments_on_active_documents_count,
        }
        return render(request, "org-index.html", context=context)


class DocumentDetailView(OrganizationView, DetailView):
    model = Document


class FilteredDocumentListView(OrganizationView, ExportMixin, SingleTableMixin, FilterView):
    table_class = DocumentsTable
    model = Document
    template_name = "comments/document_list.html"

    filterset_class = DocumentsFilter

    table_pagination = {"per_page": 50}


class DocumentCreate(SuccessMessageMixin, OrganizationView, CreateView):
    template_name = "comments/document_create.html"
    form_class = DocumentCreateForm
    success_message = "Document added successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class DocumentRefreshView(OrganizationView):
    def post(self, request, organization_slug, slug):
        document = Document.objects.get(slug=slug, deleted_at=None)
        try:
            if not self.organization.regulations_gov_api_key:
                messages.error(request, "Missing regulations.gov API key")
            else:
                api_document = get_document(document.document_id, self.organization)
                document.set_from_api_response(document, api_document, self.organization)
                messages.success(request, "Document successfully refreshed from regulations.gov")
        except Exception:
            logger.exception("Could not get document info from regulations.gov")
            messages.error(request, "Could not get document info from regulations.gov")

        return redirect(reverse("document-detail", args=[self.organization.slug, document.slug]))


class DocumentUpdate(OrganizationView, UpdateView):
    template_name = "comments/document_update.html"
    model = Document
    form_class = DocumentUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class DocumentDelete(OrganizationView, DeleteView):
    model = Document

    def get_success_url(self):
        return reverse("documents", args=[self.organization.slug])

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Document was deleted successfully.")
        return response

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["comments_count"] = Comment.objects.filter(document=context["object"]).count()
        return context


class CommentDetailView(OrganizationView, DetailView):
    model = Comment


class ResubmitCommentView(OrganizationView):
    def post(self, request, organization_slug, comment_id):
        comment = Comment.objects.get(id=comment_id)
        if comment.was_submitted:
            messages.error(request, "Comment has already been successfully submitted.")
        else:
            tasks.submit_comment.delay(comment.id)
            messages.success(request, "Comment queued for submission.")
        return redirect(reverse("comment-detail", args=[self.organization.slug, comment.id]))


class ResubmitCommentsView(OrganizationView):
    def post(self, request, organization_slug):

        comment_ids = set(request.POST.getlist("resubmit"))

        if not comment_ids:
            messages.error(request, f"No comments selected.")
            return redirect(reverse("comments", args=[self.organization.slug]))

        if len(comment_ids) > settings.TABLE_PAGE_SIZE:
            messages.error(request, f"You may only submit {settings.TABLE_PAGE_SIZE} comments at a time.")
            return redirect(reverse("comments", args=[self.organization.slug]))

        comments = Comment.objects.filter(organization=request.user.organization, id__in=comment_ids)

        found_comment_ids = set([str(c.id) for c in comments])
        if comment_ids != found_comment_ids:
            messages.error(request, f"Could not find comments with IDs: {', '.join(comment_ids-found_comment_ids)}.")
            return redirect(reverse("comments", args=[self.organization.slug]))

        submitted_ids = [str(c.id) for c in comments if c.was_submitted]
        if submitted_ids:
            messages.error(request, f"Comments with IDs: {', '.join(submitted_ids)} have already been submitted.")
            return redirect(reverse("comments", args=[self.organization.slug]))

        for c in comments:
            tasks.submit_comment.delay(c.id)

        messages.success(request, "Comments queued for submission.")

        return redirect(reverse("comments", args=[self.organization.slug]))


class FilteredCommentListView(OrganizationView, ExportMixin, SingleTableMixin, FilterView):
    table_class = CommentsTable
    model = Comment
    template_name = "comments/comment_list.html"
    export_name = "comments"

    filterset_class = CommentsFilter

    table_pagination = {"per_page": settings.TABLE_PAGE_SIZE}

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related("organization", "document", "commenter")


################
# Public Views #
################


@csrf_exempt
@xframe_options_exempt
def comment_view(request, organization_slug, document_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    document = get_object_or_404(Document, organization=organization, slug=document_slug)
    if request.method == "POST":
        form = CommentForm(request.POST, document=document)
        if form.is_valid():
            commenter = Commenter.objects.get_or_create(email=form.cleaned_data["email"], organization=document.organization)[0]
            commenter.first_name = form.cleaned_data["first_name"]
            commenter.last_name = form.cleaned_data["last_name"]
            commenter.save()
            comment = Comment(
                commenter=commenter,
                comment=form.cleaned_data["comment"],
                document=document,
                organization=document.organization,
                client_mode=document.client_mode,
            )
            comment.save()
            tasks.submit_comment.delay(comment.id)
            return HttpResponseRedirect(reverse("comment-thanks", args=[organization_slug, document_slug]))
        else:
            messages.error(request, _("There were problems with your submission. Please correct them below."))
    else:
        form = CommentForm(document=document)

    return render(
        request,
        "comments/comment_form.html",
        {"form": form, "document": document, "is_staging_api": settings.USE_STAGING_REGULATIONS_API},
    )


@csrf_exempt
@xframe_options_exempt
def comment_thanks_view(request, organization_slug, document_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    return render(
        request,
        "comments/comment_thanks.html",
        {"document": get_object_or_404(Document, organization=organization, slug=document_slug)},
    )
