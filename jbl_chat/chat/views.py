from django.db.models import Q
from rest_framework import generics, permissions
from .models import Chat
from .serializers import ChatMessageSerializer
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.http import HttpResponse


class ChatRoomView(LoginRequiredMixin, TemplateView):
    template_name = "chat/partials/chat_window.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The recipient user object
        context["recipient"] = User.objects.get(pk=self.kwargs["user_id"])
        # Pass the initial message set to the template
        context["messages"] = self._get_messages(self.kwargs["user_id"])
        return context

    def _get_messages(self, user_id):
        user = self.request.user
        return Chat.objects.filter(
            (Q(sender=user) & Q(recipient_id=user_id))
            | (Q(sender_id=user_id) & Q(recipient=user))
        ).order_by("created_at")


class MessageBubblesView(LoginRequiredMixin, TemplateView):
    """
    A dedicated view to render just the message bubbles partial.
    This is called by the chat window to refresh messages.
    """

    template_name = "chat/partials/message_bubbles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = self._get_messages(self.kwargs["user_id"])
        return context

    def _get_messages(self, user_id):
        user = self.request.user
        return Chat.objects.filter(
            (Q(sender=user) & Q(recipient_id=user_id))
            | (Q(sender_id=user_id) & Q(recipient=user))
        ).order_by("created_at")


class MessageListView(generics.ListAPIView):
    """
    API view to retrieve messages between the authenticated user and another user.
    """

    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # The other user's ID is expected as a URL parameter
        other_user_id = self.kwargs["user_id"]
        user = self.request.user

        # Filter messages where the user is either the sender or recipient
        return Chat.objects.filter(
            (Q(sender=user) & Q(recipient_id=other_user_id))
            | (Q(sender_id=other_user_id) & Q(recipient=user))
        )


class MessageCreateView(generics.CreateAPIView):
    """
    API view to create a new chat message.
    """

    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Set the sender to the current user
        serializer.save(sender=self.request.user)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        # After creating, fetch the whole conversation to return as a fragment
        recipient_id = request.data.get("recipient")
        messages = Chat.objects.filter(
            (Q(sender=request.user) & Q(recipient_id=recipient_id))
            | (Q(sender_id=recipient_id) & Q(recipient=request.user))
        ).order_by("created_at")
        # Render the fragment and return it
        html = render_to_string(
            "chat/partials/message_bubbles.html",
            {"messages": messages, "request": request},
        )
        return HttpResponse(html)
