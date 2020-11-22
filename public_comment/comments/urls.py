from decorator_include import decorator_include
from django.contrib.auth.decorators import login_required
from django.urls import include, path

from .views import (
    CommentDetailView,
    DocumentCreate,
    DocumentDelete,
    DocumentDetailView,
    DocumentRefreshView,
    DocumentUpdate,
    FilteredCommentListView,
    FilteredDocumentListView,
    IndexView,
    OrgIndexView,
    ResubmitCommentsView,
    ResubmitCommentView,
    comment_thanks_view,
    comment_view,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("account/", include("organizations.urls")),
    path("submit-comment/<slug:document_slug>", comment_view, name="comment"),
    path("submit-comment/thanks/<slug:document_slug>", comment_thanks_view, name="comment-thanks"),
    path("<slug:organization_slug>/comments/", FilteredCommentListView.as_view(), name="comments"),
    path("<slug:organization_slug>/comments/<slug:pk>", CommentDetailView.as_view(), name="comment-detail"),
    path(
        "<slug:organization_slug>/comments/resubmit/<slug:comment_id>", ResubmitCommentView.as_view(), name="comment-resubmit"
    ),
    path("<slug:organization_slug>/comments/resubmit/", ResubmitCommentsView.as_view(), name="comments-resubmit"),
    path("<slug:organization_slug>/documents/", FilteredDocumentListView.as_view(), name="documents"),
    path("<slug:organization_slug>/documents/<slug:slug>", DocumentDetailView.as_view(), name="document-detail"),
    path("<slug:organization_slug>/documents/new/", DocumentCreate.as_view(), name="document-create"),
    path("<slug:organization_slug>/documents/edit/<slug:slug>", DocumentUpdate.as_view(), name="document-edit"),
    path("<slug:organization_slug>/documents/delete/<slug:slug>", DocumentDelete.as_view(), name="document-delete"),
    path("<slug:organization_slug>/documents/refresh/<slug:slug>", DocumentRefreshView.as_view(), name="document-refresh"),
    path("markdownx/", decorator_include(login_required, "markdownx.urls")),
    path("<slug:organization_slug>", OrgIndexView.as_view(), name="org-index"),
]
