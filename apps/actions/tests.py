from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from apps.actions.models import Swipe
from apps.matches.models import Match

User = get_user_model()

class SwipeActionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='password123')
        self.swipe_url = reverse('swipe-action')  # Update with your actual URL name

    def test_swipe_action_like(self):
        self.client.force_authenticate(user=self.user1)
        data = {'swiped_user_id': self.user2.id, 'action': 'LIKE'}
        response = self.client.post(self.swipe_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Swipe.objects.count(), 1)
        self.assertEqual(Swipe.objects.first().action, 'LIKE')

    def test_swipe_action_pass(self):
        self.client.force_authenticate(user=self.user1)
        data = {'swiped_user_id': self.user2.id, 'action': 'PASS'}
        response = self.client.post(self.swipe_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Swipe.objects.count(), 1)
        self.assertEqual(Swipe.objects.first().action, 'PASS')

    def test_mutual_like_creates_match(self):
        self.client.force_authenticate(user=self.user1)
        data1 = {'swiped_user_id': self.user2.id, 'action': 'LIKE'}
        self.client.post(self.swipe_url, data1)

        self.client.force_authenticate(user=self.user2)
        data2 = {'swiped_user_id': self.user1.id, 'action': 'LIKE'}
        response = self.client.post(self.swipe_url, data2)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Match.objects.count(), 1)
        match = Match.objects.first()
        self.assertTrue(match.users.filter(id=self.user1.id).exists())
        self.assertTrue(match.users.filter(id=self.user2.id).exists())

    def test_swipe_on_self(self):
        self.client.force_authenticate(user=self.user1)
        data = {'swiped_user_id': self.user1.id, 'action': 'LIKE'}
        response = self.client.post(self.swipe_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You cannot swipe on yourself.")

