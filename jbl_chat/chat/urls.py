from django.urls import path
from . import views

urlpatterns = [
    path("<int:user_id>/", views.ChatRoomView.as_view(), name="chat-room"),
    path(
        "<int:user_id>/messages/",
        views.MessageBubblesView.as_view(),
        name="chat-messages",
    ),
]
