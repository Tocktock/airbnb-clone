import os
import requests
from django.utils import translation
from django.http import HttpResponse
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import FormView, DetailView, UpdateView
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from . import forms, models, mixins


class LoginView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        else:
            return reverse("core:home")


def log_out(request):
    messages.info(request, f"See you later")
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(FormView):
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        print("successful" + key)
        # to do : add success message
    except models.User.DoesNotExist:
        # to do : add error message
        print("failed" + key)
        pass
    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get("GH_ID")
    redirect_uri = "http://airbnb-clone.xvuzexi3fp.ap-northeast-2.elasticbeanstalk.com//users/continue/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
    )
    pass


class GithubException(Exception):
    pass


def github_callback(request):
    code = request.GET.get("code")
    client_id = os.environ.get("GH_ID")
    client_secret = os.environ.get("GH_SECRET")

    try:
        if code is not None:
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            token_json = token_request.json()
            error = token_json.get("error", None)
            if error is not None:
                raise GithubException("Can't get access token")
            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)
                if username is not None:
                    name = profile_json.get("name", None)
                    email = profile_json.get("email", None)
                    bio = profile_json.get("bio", None)
                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(
                                f"Please login with {user.login_method}"
                            )
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,
                            bio=bio,
                            first_name=name,
                            username=email,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(request, f"Welcome back {user.first_name}")
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException("Can't get your profile")
        else:
            raise GithubException("Can't get Code from github")
    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("core:home"))


class KakaoException(Exception):
    pass


def kakao_login(request):
    client_id = os.environ.get("KAKAO_ID")
    redirect_uri = "http://airbnb-clone.xvuzexi3fp.ap-northeast-2.elasticbeanstalk.com/users/continue/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )


def kakao_callback(request):
    try:
        code = request.GET.get("code")
        client_id = os.environ.get("KAKAO_ID")
        redirect_uri = "http://airbnb-clone.xvuzexi3fp.ap-northeast-2.elasticbeanstalk.com/users/continue/kakao/callback"
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException("Can't get authorization code")
        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_request.json()
        kakao_account = profile_json.get("kakao_account")
        email = kakao_account.get("email", None)
        if email is None:
            raise KakaoException("Please also g ive me your email")
        profile = kakao_account.get("profile")
        nickname = profile.get("nickname")
        profile_image = profile.get("profile_image_url")

        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException(f"Please Login with:{user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                username=email,
                email=email,
                email_verified=True,
                first_name=nickname,
                login_method=models.User.LOGIN_KAKAO,
            )
            user.set_unusable_password()
            user.save()

            if profile_image is not None:
                photo_request = requests.get(profile_image)

                user.avatar.save(
                    f"{nickname}-avatar.jpg", ContentFile(photo_request.content),
                )
        login(request, user)
        messages.success(request, f"Welcome back {user.first_name}")
        return redirect(reverse("core:home"))
        if email is None:
            raise KakaoException()
    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):

    model = models.User
    context_object_name = "user_obj"


class UpdateProfileView(mixins.LoggedOnlyView, SuccessMessageMixin, UpdateView):

    model = models.User
    template_name = "users/update-profile.html"
    fields = (
        "first_name",
        "last_name",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency",
    )

    success_message = "profile updated"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["first_name"].widget.attrs = {"placeholder": "First name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "Last name"}
        form.fields["bio"].widget.attrs = {"placeholder": "Bio"}
        form.fields["gender"].widget.attrs = {"placeholder": "Gender"}
        form.fields["birthdate"].widget.attrs = {"placeholder": "Birthdate"}
        form.fields["language"].widget.attrs = {"placeholder": "Language"}
        form.fields["currency"].widget.attrs = {"placeholder": "Currency"}
        return form


class UpdatePasswordView(
    mixins.LoggedOnlyView,
    mixins.EmailLoggedInOnlyView,
    SuccessMessageMixin,
    PasswordChangeView,
):
    template_name = "users/update-password.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Current Password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New Password"}
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "Confirm New Password"
        }
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()


@login_required
def switch_hosting(request):
    try:
        del request.session["is_hosting"]
    except KeyError:
        request.session["is_hosting"] = True
    return redirect(reverse("core:home"))


def switch_language(request):

    lang = request.GET.get("lang", None)
    if lang is not None:
        request.session[translation.LANGUAGE_SESSION_KEY] = lang
        print(lang)
    return HttpResponse(status=200)
