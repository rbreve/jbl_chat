from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.shortcuts import redirect
from rest_framework import permissions, status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.http import HttpResponse

from .models import UserProfile
from .serializers import (
    UserProfileSerializer,
)


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user.userprofile


class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserProfile.objects.exclude(user=self.request.user.pk)

    def list(self, request, *args, **kwargs):
        # Check if the request is from HTMX
        if request.headers.get("Hx-Request"):
            queryset = self.get_queryset()
            html = render_to_string(
                "users/partials/user_list_items.html", {"users": queryset}
            )
            return HttpResponse(html)

        # Fallback to default JSON response
        return super().list(request, *args, **kwargs)


class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)


class LogoutView(TemplateView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")


class LoginView(TemplateView):
    template_name = "users/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("user-list")
        return super().get(request, *args, **kwargs)


class LoginAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = []  # Bypass session auth and CSRF check

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response(
                {"access": str(refresh.access_token), "refresh": str(refresh)}
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class UserListView(LoginRequiredMixin, TemplateView):
    template_name = "users/user_list.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = UserProfile.objects.all()
        return context
