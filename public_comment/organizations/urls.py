from django.urls import path

from organizations.views import AccountView, OrganizationUpdateView, SignInView, SignOutView, UserUpdateView

urlpatterns = [
    path("", AccountView.as_view(), name="account"),
    path("sign-in/", SignInView.as_view(), name="sign-in"),
    path("sign-out/", SignOutView.as_view(), name="sign-out"),
    path("edit/", UserUpdateView.as_view(), name="user-update"),
    path("<slug:organization_slug>/edit/", OrganizationUpdateView.as_view(), name="org-update"),
]
