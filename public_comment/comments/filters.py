import django_filters
from django import forms
from django.contrib.postgres.search import SearchVector
from django.db.models import Q

from comments.models import Comment, Document

WAS_SUBMITTED_CHOICES = ((1, "Yes"), (0, "No"))


class CommentsFilter(django_filters.FilterSet):
    document = django_filters.filters.CharFilter(method="filter_document")
    comment = django_filters.filters.CharFilter(method="filter_comment")
    created_at = django_filters.DateRangeFilter(empty_label="Date Created")
    was_submitted = django_filters.ChoiceFilter(
        empty_label="Was Submitted?", choices=WAS_SUBMITTED_CHOICES, method="filter_was_submitted"
    )

    class Meta:
        model = Comment
        fields = ["document", "comment", "created_at"]

    def filter_comment(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("comment", "commenter__email")).filter(
            Q(search__icontains=value) | Q(search=value)
        )

    def filter_document(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("document__title", "document__document_id")).filter(
            Q(search__icontains=value) | Q(search=value)
        )

    def filter_was_submitted(self, queryset, name, value):
        if value == "0":
            return queryset.filter(was_submitted=False)
        elif value == "1":
            return queryset.filter(was_submitted=True)
        return queryset


class DocumentsFilter(django_filters.FilterSet):
    document_id = django_filters.filters.CharFilter(method="filter_document_id")
    text = django_filters.filters.CharFilter(method="filter_text", label="Text")
    created_at = django_filters.DateRangeFilter(empty_label="Date Created")

    class Meta:
        model = Document
        fields = ["document_id", "created_at"]

    def filter_text(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("title", "description")).filter(
            Q(search__icontains=value) | Q(search=value)
        )

    def filter_document_id(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("document_id")).filter(Q(search__icontains=value) | Q(search=value))
