from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="api-login"),
    path("token/", TokenObtainPairView.as_view(), name="api-token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("profile/", views.UserProfileView.as_view(), name="api-user-profile"),
    path("profiles/", views.UserProfileListView.as_view(), name="api-user-profiles"),
]
