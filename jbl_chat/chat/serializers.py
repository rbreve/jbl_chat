from rest_framework import serializers
from chat.models import Chat


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ["id", "sender", "recipient", "message", "timestamp"]

    def create(self, validated_data):
        sender = self.context["request"].user
        recipient = self.context["recipient"]
        message = validated_data.get("message")
        chat = Chat.objects.create(sender=sender, recipient=recipient, message=message)
        return chat
