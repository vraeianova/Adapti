from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import (
    CreateView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from apps.users.models import Profile
from apps.utils import generate_password
from apps.utils.tokens import account_activation_token

from ..forms import ProfileCreateForm, SignupUsersForm


User = get_user_model()


class LoginView(LoginView):
    template_name = "users/login.html"

    def post(self, request):
        username = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(email=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                if user.new_pass_confirmed is False:
                    return HttpResponseRedirect(
                        reverse("users:password_change")
                    )
                elif user.is_client:
                    return HttpResponseRedirect(
                        reverse("users:user_dashboard")
                    )
                elif user.is_superuser:
                    return HttpResponseRedirect(
                        reverse("administrators:admin_home")
                    )
                elif user.is_employee or user.is_security_guard:
                    return HttpResponseRedirect(
                        reverse("employees:employee_home")
                    )
            else:
                print("usuario inactivo")
                return HttpResponse("Inactive user.")
        else:
            messages.add_message(
                request,
                messages.INFO,
                "¡Credenciales inválidas!",
                extra_tags="error",
            )
            return HttpResponseRedirect(settings.LOGIN_URL)


class TermsAndConditionsView(View):
    def get(self, request, **kwargs):
        return render(request, "users/terms_and_conditions.html")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(settings.LOGIN_URL)


class ActivateAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(
            user, token
        ):
            user.is_active = True
            user.email_confirmed = True
            user.new_pass_confirmed = True
            user.save()
            login(request, user)
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "¡Su cuenta ha sido activada!",
                extra_tags="success",
            )

            if user.is_employee:
                return HttpResponseRedirect(reverse("users:login"))
            if user.is_client:
                return HttpResponseRedirect(reverse("users:login"))

        else:
            messages.warning(request, ("El link de confirmación es inválido"))
            return HttpResponseRedirect(reverse("users:login"))


class EmailConfirmView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, "users/email_confirm.html")


class TempPasswordChangeView(View):
    def post(self, request, **kwargs):
        new_password = generate_password()
        email = request.POST["email"]
        user = User.objects.get(email=email)
        user.new_pass_confirmed = True
        user.set_password(new_password)
        user.save()

        """Send temp password"""
        current_site = get_current_site(request)
        subject = "¡Cambio de contraseña!, Lomas Club Deportivo"
        from_email = "Lomas Club Deportivo <noreply@lomasclub.com>"
        message = render_to_string(
            "users/temp_password_email.html",
            {
                "user": email,
                "domain": current_site.domain,
                "password": new_password,
            },
        )
        msg = EmailMessage(subject, message, from_email, [email])
        msg.content_subtype = "html"
        msg.send()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "¡Se ha enviado un mail al cliente con una nueva contraseña!",
            extra_tags="success",
        )
        success_url = reverse_lazy("clients:clients_list")
        return HttpResponseRedirect(success_url)


class CustomPasswordChangeView(View):
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:login")

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        password = request.POST["password"]
        password_confirm = request.POST["password2"]

        if password == password_confirm:
            user.new_pass_confirmed = True
            user.set_password(password)
            user.save()

            messages.add_message(
                self.request,
                messages.SUCCESS,
                "¡Contraseña actualizada!",
                extra_tags="success",
            )
            return HttpResponseRedirect(self.success_url)
        else:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "¡Las contraseñas no coinciden!",
                extra_tags="error",
            )
            return HttpResponseRedirect(self.request.path_info)


class UserDashboardView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, "users/user_dashboard.html")


class UserListView(ListView):
    model = User
    template_name = "users/users_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.filter(is_employee=True)
        context["users"] = users
        return context


class UserAddView(CreateView):
    form_class = SignupUsersForm
    template_name = "users/user_add.html"

    def get(self, request, **kwargs):
        user_form = self.form_class()
        profile_form = ProfileCreateForm()
        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
            },
        )

    def post(self, request):
        form = self.form_class(request.POST)
        profile_form = ProfileCreateForm(request.POST, request=request)
        context = {
            "user_form": form,
            "profile_form": profile_form,
        }
        if form.is_valid() and profile_form.is_valid():
            options = form.cleaned_data["options"]
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.username = user.email
                    password = generate_password()
                    user.set_password(password)
                    if options == "is_employee":
                        user.is_employee = True
                    elif options == "is_superuser":
                        user.is_superuser = True

                    user.save()

                    profile = profile_form.save(commit=False)
                    profile.id_user = user
                    profile.save()

                    # TODO ACTUALIZAR PARA PODER ENVIAR EL CORREO
                    """Send account verification link"""
                    current_site = get_current_site(request)
                    subject = "¡Hola! {} , Lomas Club Deportivo".format(
                        user.email
                    )
                    from_email = "Lomas Club Deportivo <noreply@lomasclub.com>"
                    message = render_to_string(
                        "users/account_activation_email.html",
                        {
                            "user": user,
                            "domain": current_site.domain,
                            "password": password,
                            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                            "token": account_activation_token.make_token(user),
                        },
                    )
                    msg = EmailMessage(
                        subject, message, from_email, [user.email]
                    )
                    msg.content_subtype = "html"
                    msg.send()
                    messages.add_message(
                        self.request,
                        messages.SUCCESS,
                        "¡Usuario creado correctamente!",
                        extra_tags="success",
                    )
                    return HttpResponseRedirect(reverse("users:users_list"))

            except IntegrityError as e:
                print("Error al crear usuario", e)
            return HttpResponseRedirect(reverse("users:users_list"))

        else:
            for error in form.error_list:
                messages.add_message(
                    self.request, messages.INFO, error, extra_tags="warning"
                )
            for error in profile_form.error_list:
                messages.add_message(
                    self.request, messages.INFO, error, extra_tags="warning"
                )
            return render(request, self.template_name, context)

    def get_success_url(self):
        return reverse("users:users_list")


class UserUpdateView(UpdateView):
    model = User
    template_name = "users/user_update.html"
    form_class_user = SignupUsersForm
    form_class_profile = ProfileCreateForm

    def get(self, request, *args, **kwargs):
        user_form = self.form_class_user(instance=self.get_object())
        profile = Profile.objects.get(id_user=self.get_object())
        profile_form = self.form_class_profile(instance=profile)

        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
            },
        )

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.get(id_user=self.get_object())
        profile_form = self.form_class_profile(request.POST, instance=profile)
        form = self.form_class_user(request.POST, instance=self.get_object())

        if form.is_valid() and profile_form.is_valid():
            options = form.cleaned_data["options"]
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    if options == "is_employee":
                        user.is_employee = True
                    elif options == "is_superuser":
                        user.is_superuser = True
                    user.save()
                    profile = profile_form.save(commit=False)
                    profile.save()

                    messages.add_message(
                        self.request,
                        messages.SUCCESS,
                        "¡Usuario actualizado correctamente!",
                        extra_tags="success",
                    )
                return HttpResponseRedirect(self.request.path_info)

            except IntegrityError as e:
                print("e", e)
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    "¡Error al actualizar usuario!",
                    extra_tags="error",
                )
            return HttpResponseRedirect(self.request.path_info)

        else:
            for error in form.error_list:
                messages.add_message(
                    self.request, messages.INFO, error, extra_tags="warning"
                )
            for error in profile_form.error_list:
                messages.add_message(
                    self.request, messages.INFO, error, extra_tags="warning"
                )
            return HttpResponseRedirect(self.request.path_info)
