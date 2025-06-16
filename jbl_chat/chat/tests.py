from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Chat


class MessagePrivacyAPITestCase(TestCase):

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username="user1", password="test123")
        self.user2 = User.objects.create_user(username="user2", password="test123")
        self.user3 = User.objects.create_user(username="user3", password="test123")

        # Create API client and authenticate as user1
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_api_messages_only_shows_user_conversations(self):
        """Test that /api/chat/messages/<user_id>/ only returns messages where request.user is sender or recipient"""

        # Create messages between different users
        # Messages between user1 and user2
        message1 = Chat.objects.create(
            sender=self.user1, recipient=self.user2, message="Hello from user1 to user2"
        )
        message2 = Chat.objects.create(
            sender=self.user2, recipient=self.user1, message="Reply from user2 to user1"
        )

        # Messages between user2 and user3 (user1 should NOT see these)
        Chat.objects.create(
            sender=self.user2, recipient=self.user3, message="Private message to user3"
        )
        Chat.objects.create(
            sender=self.user3, recipient=self.user2, message="Private reply to user2"
        )

        # Test: user1 requesting messages with user2
        response = self.client.get(f"/api/chat/messages/{self.user2.id}/")

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should return exactly 2 messages (conversation between user1 and user2)
        self.assertEqual(len(data), 2)

        # Verify the returned messages are the correct ones
        message_texts = [msg["message"] for msg in data]
        self.assertIn("Hello from user1 to user2", message_texts)
        self.assertIn("Reply from user2 to user1", message_texts)

        # Verify private messages are NOT included
        self.assertNotIn("Private message to user3", message_texts)
        self.assertNotIn("Private reply to user2", message_texts)

        # Verify the message IDs match our expected messages
        message_ids = [msg["id"] for msg in data]
        self.assertIn(message1.id, message_ids)
        self.assertIn(message2.id, message_ids)

    def test_api_messages_excludes_unrelated_conversations(self):
        """Test that user1 gets empty result when requesting messages with user3 (no conversation exists)"""

        # Create messages only between user2 and user3
        Chat.objects.create(
            sender=self.user2, recipient=self.user3, message="Secret message"
        )
        Chat.objects.create(
            sender=self.user3, recipient=self.user2, message="Secret reply"
        )

        # Test: user1 requesting messages with user3 (should be empty)
        response = self.client.get(f"/api/chat/messages/{self.user3.id}/")

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should return empty list (no conversation between user1 and user3)
        self.assertEqual(len(data), 0)

    def test_api_messages_requires_authentication(self):
        """Test that the API endpoint requires authentication"""

        # Create a message
        Chat.objects.create(
            sender=self.user1, recipient=self.user2, message="Test message"
        )

        # Create API client without authentication
        unauthenticated_client = APIClient()

        # Test: requesting messages without authentication
        response = unauthenticated_client.get(f"/api/chat/messages/{self.user2.id}/")

        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, 401)
