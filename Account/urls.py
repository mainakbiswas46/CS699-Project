from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("login/", handleLogin, name="login"),
    path("signup/", handleSignup, name="signup"),
    path("logout/", handleLogout, name="logout"),
    path("token/", token, name="token"),
    path("verify/<auth_token>", verify, name="verify"),
    path("error/", error, name="error"),
    path("search/", search, name="search"),
    path("user", user, name="user"),
    path("profile/", profile, name="profile"),
    path("info/", info, name="info"),
    path("edit_profile", edit_profile, name="edit_profile"),
    path("change_safe_mode", change_safe_mode, name="change_safe_mode"),
    path("change_password", change_password, name="change_password"),
    path("change_profile_pic", change_profile_pic, name="change_profile_pic"),
    path("forgot_password/", forgot_password, name="forgot_password"),
    path("reset_password/<auth_token>", reset_password, name="reset_password"),
    path(
        "reset_password_submit/<auth_token>",
        reset_password_submit,
        name="reset_password_submit",
    ),
    
]
