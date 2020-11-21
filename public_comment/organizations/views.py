from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView

from lib.views import OrganizationView, ProtectedView
from organizations.forms import LoginForm, OrganizationUpdateForm, UserUpdateForm
from organizations.models import Organization


class SignInView(LoginView):
    authentication_form = LoginForm
    template_name = "registration/sign-in.html"
    success_url = reverse_lazy("comments:index")


class SignOutView(LogoutView):
    authentication_form = LoginForm
    template_name = "registration/signed-out.html"
    success_url = reverse_lazy("comments:index")


class AccountView(ProtectedView):
    def get(self, request):
        return render(request, "organizations/account.html", context={"user": request.user})


class UserUpdateView(ProtectedView, FormView):
    template_name = "organizations/user_update.html"
    form_class = UserUpdateForm
    success_url = reverse_lazy("account")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your information has been updated")
        return super().form_valid(form)


class OrganizationUpdateView(SuccessMessageMixin, ProtectedView, UpdateView):
    template_name = "organizations/organization_update.html"
    model = Organization
    form_class = OrganizationUpdateForm
    success_url = reverse_lazy("account")
    success_message = "Your information has been updated"

    def dispatch(self, request, *args, **kwargs):
        self.kwargs = {"pk": request.user.organization.id}
        return super().dispatch(request, *args, **kwargs)
