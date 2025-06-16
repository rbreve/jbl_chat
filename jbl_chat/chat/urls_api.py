from django.urls import path
from . import views

urlpatterns = [
    path(
        "messages/<int:user_id>/",
        views.MessageListView.as_view(),
        name="api-message-list",
    ),
    path(
        "messages/create/", views.MessageCreateView.as_view(), name="api-message-create"
    ),
]
