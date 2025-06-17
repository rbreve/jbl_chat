from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from . import views
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health_check"),
    path("users/", include("users.urls")),  # UI routes
    path("chat/", include("chat.urls")),  # Chat UI routes
    path("api/users/", include("users.urls_api")),  # API routes
    path("api/chat/", include("chat.urls_api")),  # Chat API routes
    path("", RedirectView.as_view(url="users/")),
]
