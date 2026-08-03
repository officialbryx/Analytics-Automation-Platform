from django.urls import path
from main import views
from portal import views as portal_views

app_name = "main"

urlpatterns = [
    path("", portal_views.login_page, name="login_page"),
    path("form", views.form_page, name="form_page"),
    path("requests", views.requests_page, name="requests_page"),
    path("cancel/<str:task_id>/", views.cancel_celery_task, name="cancel_request"),
    path("delete/<str:task_id>/", views.delete_request, name="delete_request"),
]
