from django.db.models import Q
from rest_framework import generics, permissions
from .models import Chat
from .serializers import ChatMessageSerializer


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
