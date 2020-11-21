from django.contrib.admin import ModelAdmin


class SoftDeleteModelAdmin(ModelAdmin):
    def get_queryset(self, request):
        qs = self.model.objects_with_deleted
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    readonly_fields = ("deleted_at",)
