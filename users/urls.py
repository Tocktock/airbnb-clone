from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.log_out, name="logout"),
    path("signup", views.SignUpView.as_view(), name="signup"),
    path("verify/<str:key>", views.complete_verification, name="complete-verification"),
    path("continue/github", views.github_login, name="github-login"),
    path("continue/github/callback", views.github_callback, name="github-callback"),
    path("continue/kakao", views.kakao_login, name="kakao-login"),
    path("continue/kakao/callback", views.kakao_callback, name="kakao-callback"),
]

