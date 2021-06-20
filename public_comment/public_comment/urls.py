from csp.decorators import csp_exempt
from decorator_include import decorator_include
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path
from multifactor.decorators import multifactor_protected

admin.site.site_header = "Gov Commenter Administration"

urlpatterns = [
    path("account/multifactor/", decorator_include(csp_exempt, "multifactor.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", decorator_include(multifactor_protected(factors=1, max_age=60 * 60 * 72, advertise=True), admin.site.urls)),
    path("", include("comments.urls")),
    url(r"", include("user_sessions.urls", "user_sessions")),
    path("<path:url>", views.flatpage),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    # Debug could be on when deployed, but we'd be using django-storages and a remote location for media storage
    if settings.MEDIA_URL and settings.MEDIA_ROOT:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
