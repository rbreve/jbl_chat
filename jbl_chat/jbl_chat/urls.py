from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),  # UI routes
    path("chat/", include("chat.urls")),  # Chat UI routes
    path("api/users/", include("users.urls_api")),  # API routes
    path("api/chat/", include("chat.urls_api")),  # Chat API routes
]
