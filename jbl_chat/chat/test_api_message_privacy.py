import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Chat


@pytest.mark.django_db
def test_api_messages_only_shows_user_conversations():
    """Test that /api/chat/messages/<user_id>/ only returns messages where request.user is sender or recipient"""

    # Create test users
    user1 = User.objects.create_user(username="user1", password="test123")
    user2 = User.objects.create_user(username="user2", password="test123")
    user3 = User.objects.create_user(username="user3", password="test123")

    # Create messages between different users
    # Messages between user1 and user2
    message1 = Chat.objects.create(
        sender=user1, recipient=user2, message="Hello from user1 to user2"
    )
    message2 = Chat.objects.create(
        sender=user2, recipient=user1, message="Reply from user2 to user1"
    )

    # Messages between user2 and user3 (user1 should NOT see these)
    Chat.objects.create(
        sender=user2, recipient=user3, message="Private message to user3"
    )
    Chat.objects.create(sender=user3, recipient=user2, message="Private reply to user2")

    # Create API client and authenticate as user1
    client = APIClient()
    refresh = RefreshToken.for_user(user1)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    # Test: user1 requesting messages with user2
    response = client.get(f"/api/chat/messages/{user2.id}/")

    assert response.status_code == 200
    data = response.json()

    # Should return exactly 2 messages (conversation between user1 and user2)
    assert len(data) == 2

    # Verify the returned messages are the correct ones
    message_texts = [msg["message"] for msg in data]
    assert "Hello from user1 to user2" in message_texts
    assert "Reply from user2 to user1" in message_texts

    # Verify private messages are NOT included
    assert "Private message to user3" not in message_texts
    assert "Private reply to user2" not in message_texts

    # Verify the message IDs match our expected messages
    message_ids = [msg["id"] for msg in data]
    assert message1.id in message_ids
    assert message2.id in message_ids


@pytest.mark.django_db
def test_api_messages_excludes_unrelated_conversations():
    """Test that user1 gets empty result when requesting messages with user3 (no conversation exists)"""

    # Create test users
    user1 = User.objects.create_user(username="user1", password="test123")
    user2 = User.objects.create_user(username="user2", password="test123")
    user3 = User.objects.create_user(username="user3", password="test123")

    # Create messages only between user2 and user3
    Chat.objects.create(sender=user2, recipient=user3, message="Secret message")
    Chat.objects.create(sender=user3, recipient=user2, message="Secret reply")

    # Create API client and authenticate as user1
    client = APIClient()
    refresh = RefreshToken.for_user(user1)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    # Test: user1 requesting messages with user3 (should be empty)
    response = client.get(f"/api/chat/messages/{user3.id}/")

    assert response.status_code == 200
    data = response.json()

    # Should return empty list (no conversation between user1 and user3)
    assert len(data) == 0


@pytest.mark.django_db
def test_api_messages_requires_authentication():
    """Test that the API endpoint requires authentication"""

    # Create test users
    user1 = User.objects.create_user(username="user1", password="test123")
    user2 = User.objects.create_user(username="user2", password="test123")

    # Create a message
    Chat.objects.create(sender=user1, recipient=user2, message="Test message")

    # Create API client without authentication
    client = APIClient()

    # Test: requesting messages without authentication
    response = client.get(f"/api/chat/messages/{user2.id}/")

    # Should return 401 Unauthorized
    assert response.status_code == 401
