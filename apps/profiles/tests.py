import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Profile, Interest, Photo, City

User = get_user_model()


class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.city = City.objects.create(name="New York")
        self.profile = Profile.objects.create(user=self.user, city=self.city, bio="Test bio", age=25)

    def test_profile_creation(self):
        profile = self.profile
        self.assertEqual(profile.user.username, "testuser")
        self.assertEqual(profile.city.name, "New York")
        self.assertEqual(profile.bio, "Test bio")
        self.assertEqual(profile.age, 25)

    def test_profile_main_image(self):
        # Test main_image property without any photos
        self.assertIsNone(self.profile.main_image)

    def test_profile_photo(self):
        # Add a photo and test main image functionality
        photo = Photo.objects.create(profile=self.profile, image="test_image.jpg", is_profile_avatar=True)
        self.profile.photos.add(photo)
        self.assertEqual(self.profile.main_image, "test_image.jpg")


class InterestModelTest(TestCase):

    def setUp(self):
        self.interest = Interest.objects.create(name="Music")

    def test_interest_creation(self):
        interest = self.interest
        self.assertEqual(interest.name, "Music")


class PhotoModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.profile = Profile.objects.create(user=self.user, bio="Test bio", age=25)
        self.photo = Photo.objects.create(profile=self.profile, image="test_image.jpg", is_profile_avatar=False)

    def test_photo_creation(self):
        photo = self.photo
        self.assertEqual(photo.profile.user.username, "testuser")
        self.assertEqual(photo.image, "test_image.jpg")
        self.assertFalse(photo.is_profile_avatar)


class CityModelTest(TestCase):

    def setUp(self):
        self.city = City.objects.create(name="New York")

    def test_city_creation(self):
        city = self.city
        self.assertEqual(city.name, "New York")


class ProfileSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.city = City.objects.create(name="New York")
        self.profile = Profile.objects.create(user=self.user, city=self.city, bio="Test bio", age=25)
        self.serializer = ProfileSerializer(instance=self.profile)

    def test_serializer_fields(self):
        data = self.serializer.data
        self.assertEqual(data['user_id'], self.user.id)
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['age'], 25)
        self.assertEqual(data['bio'], "Test bio")
        self.assertEqual(data['city']['name'], "New York")

    def test_serializer_update(self):
        data = {
            'bio': "Updated bio",
            'age': 30,
        }
        serializer = ProfileSerializer(self.profile, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()
        self.assertEqual(updated_profile.bio, "Updated bio")
        self.assertEqual(updated_profile.age, 30)


@pytest.mark.django_db
class CitySerializerTest:

    def test_city_serializer(self):
        city = City.objects.create(name="New York")
        serializer = CitySerializer(city)
        assert serializer.data['name'] == "New York"

