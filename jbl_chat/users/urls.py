from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("", views.UserListView.as_view(), name="user-list"),
]
