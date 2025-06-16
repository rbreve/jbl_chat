from rest_framework import serializers
from chat.models import Chat
from django.contrib.auth.models import User


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    recipient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Chat
        fields = ["id", "sender", "recipient", "message", "created_at"]

    def create(self, validated_data):
        # Set the sender to the current user
        validated_data["sender"] = self.context["request"].user
        return super().create(validated_data)
