from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.accounts.forms import CustomUserCreationForm
from apps.accounts.serializers import UserRegisterSerializer

User = get_user_model()


class UserModelTest(TestCase):

    def test_user_creation(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="securepassword"
        )
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("securepassword"))

    def test_gender_choices(self):
        male_user = User.objects.create_user(
            username="maleuser", email="male@example.com", password="password", gender="M")
        female_user = User.objects.create_user(
            username="femaleuser", email="female@example.com", password="password", gender="F")

        self.assertEqual(male_user.gender, "M")
        self.assertEqual(female_user.gender, "F")

    def test_unique_phone(self):
        User.objects.create_user(
            username="user1", email="user1@example.com", password="password", phone="1234567890"
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="user2", email="user2@example.com", password="password", phone="1234567890"
            )


class UserViewTests(TestCase):

    def test_register_view(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_login_view(self):
        user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        url = reverse('login')
        response = self.client.post(url, {'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back, testuser!")

    def test_profile_view(self):
        user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        self.client.login(username="testuser", password="password123")
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")

    def test_logout_view(self):
        user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        self.client.login(username="testuser", password="password123")
        url = reverse('logout')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.cookies)


class CustomUserCreationFormTest(TestCase):

    def test_form_validity(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_password_mismatch(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password456',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_missing_field(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': '',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class UserRegisterSerializerTest(TestCase):

    def test_valid_data(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'phone': '1234567890'
        }
        serializer = UserRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('password123'))

    def test_invalid_username(self):
        User.objects.create_user(username="testuser", email="existing@example.com", password="password123")
        data = {
            'username': 'testuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'phone': '9876543210'
        }
        serializer = UserRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

