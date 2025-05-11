from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Match, Conversation, Message
from apps.profiles.models import City, Interest

User = get_user_model()

class MatchModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

    def test_match_creation(self):
        match, created = Match.create_match_and_conversation(self.user1, self.user2)
        self.assertTrue(created)
        self.assertEqual(match.user1, self.user1)
        self.assertEqual(match.user2, self.user2)

    def test_match_exists(self):
        match, created = Match.create_match_and_conversation(self.user1, self.user2)
        self.assertFalse(created)  # Match already exists
        match_2, created_2 = Match.create_match_and_conversation(self.user1, self.user2)
        self.assertFalse(created_2)  # Should not create a new match

    def test_match_str(self):
        match, _ = Match.create_match_and_conversation(self.user1, self.user2)
        self.assertEqual(str(match), 'Match between user1 and user2')

class ConversationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

    def test_create_conversation(self):
        conversation, created = Conversation.get_or_create_for_users(self.user1, self.user2)
        self.assertTrue(created)
        self.assertIn(self.user1, conversation.participants.all())
        self.assertIn(self.user2, conversation.participants.all())

    def test_existing_conversation(self):
        conversation, created = Conversation.get_or_create_for_users(self.user1, self.user2)
        self.assertFalse(created)
        conversation_2, created_2 = Conversation.get_or_create_for_users(self.user1, self.user2)
        self.assertFalse(created_2)  # No new conversation

    def test_conversation_str(self):
        conversation, _ = Conversation.get_or_create_for_users(self.user1, self.user2)
        self.assertEqual(str(conversation), 'Conversation between user1 and user2 (ID: {})'.format(conversation.id))

class MessageModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.conversation, _ = Conversation.get_or_create_for_users(self.user1, self.user2)

    def test_message_creation(self):
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="Hello!"
        )
        self.assertEqual(message.content, "Hello!")
        self.assertEqual(message.sender, self.user1)

    def test_message_str(self):
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="Hello!"
        )
        self.assertEqual(str(message), f"Message from user1 in conversation {self.conversation.id}")

class MatchListViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.client.login(username='user1', password='password123')
        self.match, _ = Match.create_match_and_conversation(self.user1, self.user2)

    def test_match_list_view(self):
        response = self.client.get(reverse('match-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Ensure one match exists

class ConversationListViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.client.login(username='user1', password='password123')
        self.conversation, _ = Conversation.get_or_create_for_users(self.user1, self.user2)

    def test_conversation_list_view(self):
        response = self.client.get(reverse('conversation-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Ensure one conversation exists

class MessageListViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.client.login(username='user1', password='password123')
        self.conversation, _ = Conversation.get_or_create_for_users(self.user1, self.user2)
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="Hello!"
        )

    def test_message_list_view(self):
        response = self.client.get(reverse('message-list', kwargs={'conversation_id': self.conversation.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Ensure one message exists

    def test_message_permission_view(self):
        # Try to access the messages from a different user
        self.client.logout()
        self.client.login(username='user2', password='password123')
        response = self.client.get(reverse('message-list', kwargs={'conversation_id': self.conversation.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # user2 should also be allowed to see
        self.client.logout()

    def test_message_permission_view_unauthorized(self):
        # Try to access the messages from a non-participant
        self.client.logout()
        self.client.login(username='some_other_user', password='password123')
        response = self.client.get(reverse('message-list', kwargs={'conversation_id': self.conversation.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# Additional tests can be added for other views or edge cases, such as error handling or invalid data.

