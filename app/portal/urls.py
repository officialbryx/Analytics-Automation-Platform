from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("login/error/", views.login_error, name="login_error_page"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]