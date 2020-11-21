from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from comments.models import Comment, Commenter, Document
from lib.admin import SoftDeleteModelAdmin


@admin.register(Document)
class CommentsDocumentAdmin(SoftDeleteModelAdmin, MarkdownxModelAdmin):
    readonly_fields = SoftDeleteModelAdmin.readonly_fields + ("document_id",)
    list_display = ("title", "is_accepting_comments", "is_withdrawn", "document_type", "organization")


@admin.register(Commenter)
class CommentsCommenterAdmin(SoftDeleteModelAdmin):
    list_display = ("email", "first_name", "last_name", "organization")


@admin.register(Comment)
class CommentsCommentAdmin(SoftDeleteModelAdmin):
    list_display = ("document", "commenter", "organization")
