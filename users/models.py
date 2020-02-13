import uuid
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.shortcuts import reverse

# Create your models here.


class User(AbstractUser):
    """ Custom User Model """

    GENDER_MAIL = "male"
    GENDER_FEMAIL = "female"
    GENDER_OTHER = "other"
    GENDER_CHOICES = (
        (GENDER_MAIL, "Male"),
        (GENDER_FEMAIL, "Female"),
        (GENDER_OTHER, "Other"),
    )
    LANGUAGE_ENGLISH = "en"
    LANGUAGE_KOREAN = "kr"
    LANGUAGE_CHOICES = (
        (LANGUAGE_ENGLISH, "English"),
        (LANGUAGE_KOREAN, "Korean"),
    )
    CURRENCY_USD = "usd"
    CURRENCY_KRW = "krw"

    CURRENCY_CHOICES = (
        (CURRENCY_USD, "USD"),
        (CURRENCY_KRW, "KRW"),
    )

    LOGIN_EMAIL = "email"
    LOGIN_GITHUB = "github"
    LOGIN_KAKAO = "kakao"

    LOGIN_CHOICES = (
        (LOGIN_EMAIL, "Email"),
        (LOGIN_GITHUB, "Github"),
        (LOGIN_KAKAO, "Kakao"),
    )

    avatar = models.ImageField(upload_to="avatars", blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, blank=True)
    bio = models.TextField(default="", blank=True)
    birthdate = models.DateField(blank=True, null=True)
    language = models.CharField(
        choices=LANGUAGE_CHOICES, max_length=2, blank=True, default=LANGUAGE_KOREAN
    )
    currency = models.CharField(
        choices=CURRENCY_CHOICES, max_length=5, blank=True, default=CURRENCY_KRW
    )
    superhost = models.BooleanField(default=False)
    # default를 주던가 null=True로 해서 비어도 상관없음 두개중 하나로 선택해야함.

    email_verified = models.BooleanField(default=False)
    email_secret = models.CharField(max_length=120, default="")
    login_method = models.CharField(
        max_length=50, choices=LOGIN_CHOICES, default=LOGIN_EMAIL
    )

    def get_my_fav_rooms(self):
        lists = self.lists.get(name="My Favorite Houses")
        return lists.rooms

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={"pk": self.pk})

    def verify_email(self):

        if self.email_verified is False:

            secret = uuid.uuid4().hex[:20]
            self.email_secret = secret
            html_message = render_to_string(
                "emails/verify_email.html", {"secret": secret}
            )
            send_mail(
                "Verify Airbnb Account",
                strip_tags(html_message),
                settings.EMAIL_FROM,
                [self.email],
                fail_silently=False,
                html_message=html_message,
            )
            self.save()
        return

    def __str__(self):
        return self.username
