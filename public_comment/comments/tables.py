import django_tables2 as tables
from django_tables2 import A

from comments.models import Comment, Document


class CheckBoxColumnWithName(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name


class CommentsTable(tables.Table):
    resubmit = CheckBoxColumnWithName(accessor="pk", verbose_name="Resubmit?", exclude_from_export=True)
    id = tables.LinkColumn()
    document = tables.LinkColumn(exclude_from_export=True)
    short_comment = tables.Column(orderable=False, verbose_name="Comment", exclude_from_export=True)
    commenter = tables.Column(exclude_from_export=True)

    commenter__first_name = tables.Column(verbose_name="Commenter First Name", visible=False)
    commenter__last_name = tables.Column(verbose_name="Commenter Last Name", visible=False)
    commenter__email = tables.Column(verbose_name="Commenter Email", visible=False)
    comment = tables.Column(visible=False)
    document__document_id = tables.Column(verbose_name="Document ID", visible=False)
    document__title = tables.Column(verbose_name="Document Title", visible=False)
    document__document_type = tables.Column(verbose_name="Document Type", visible=False)
    document__comment_start_date = tables.Column(verbose_name="Document Comment Start Date", visible=False)
    document__comment_end_date = tables.Column(verbose_name="Document Comment End Date", visible=False)
    document__topics = tables.ManyToManyColumn(verbose_name="Document Topics", visible=False)

    class Meta:
        model = Comment
        order_by = ("-created_at",)
        fields = ["id", "created_at", "document", "commenter", "short_comment", "client_mode", "was_submitted", "resubmit"]


class DocumentsTable(tables.Table):
    document_id = tables.LinkColumn()
    short_title = tables.Column(orderable=False)
    is_accepting_comments = tables.Column(orderable=False, verbose_name="Accepting comments?")
    is_withdrawn = tables.Column(orderable=False, verbose_name="Withdrawn?")

    class Meta:
        model = Document
        order_by = ("-created_at",)
        fields = [
            "document_id",
            "short_title",
            "document_type",
            "comment_end_date",
            "comment_start_date",
            "is_accepting_comments",
            "is_withdrawn",
        ]
