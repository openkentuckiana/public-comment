from decorator_include import decorator_include
from django.contrib.auth.decorators import login_required
from django.urls import include, path

from .views import (
    CommentDetailView,
    DocumentCreate,
    DocumentDelete,
    DocumentDetailView,
    DocumentUpdate,
    FilteredCommentListView,
    FilteredDocumentListView,
    IndexView,
    comment_thanks_view,
    comment_view,
    document_refresh,
    resubmit_comment_view,
    resubmit_comments_view,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("comment/<str:document_slug>", comment_view, name="comment"),
    path("comment/thanks/<str:document_slug>", comment_thanks_view, name="comment-thanks"),
    path("comments/", FilteredCommentListView.as_view(), name="comments"),
    path("comments/<str:pk>", CommentDetailView.as_view(), name="comment-detail"),
    path("comments/resubmit/<str:comment_id>", resubmit_comment_view, name="comment-resubmit"),
    path("comments/resubmit/", resubmit_comments_view, name="comments-resubmit"),
    path("documents/", FilteredDocumentListView.as_view(), name="documents"),
    path("documents/<str:slug>", DocumentDetailView.as_view(), name="document-detail"),
    path("documents/new/", DocumentCreate.as_view(), name="document-create"),
    path("documents/edit/<str:slug>", DocumentUpdate.as_view(), name="document-edit"),
    path("documents/delete/<str:slug>", DocumentDelete.as_view(), name="document-delete"),
    path("documents/refresh/<str:slug>", document_refresh, name="document-refresh"),
    # path("api/public_comment/", csrf_exempt(comment_view), name="api_comment"),
    path("markdownx/", decorator_include(login_required, "markdownx.urls")),
    path("account/", include("organizations.urls")),
]
