from rest_framework import serializers
from .models import Profile, Interest, Photo, City # Removed Swipe from this import
from django.contrib.auth import get_user_model

User = get_user_model()

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name'] # Or other fields you want to expose


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image', 'caption', 'is_profile_picture', 'order', 'profile', 'uploaded_at']
        read_only_fields = ['profile', 'uploaded_at'] # Profile set based on authenticated user for create operations

    def validate_is_profile_picture(self, value):
        if value and self.context.get('request'): # If trying to set this photo as the profile picture
            profile = self.context['request'].user.profile
            # Check if another photo (excluding the current one if it's an update) is already the profile picture
            if Photo.objects.filter(profile=profile, is_profile_picture=True).exclude(pk=getattr(self.instance, 'pk', None)).exists():
                raise serializers.ValidationError("Another photo is already set as the profile picture. Please unset it first or update that photo.")
        return value

class ProfileSerializer(serializers.ModelSerializer):
    # User specific fields for read-only representation
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True) # Assuming you want to expose user's email

    interests = InterestSerializer(many=True, read_only=True) # For displaying interests
    # For updating interests, client should send a list of interest IDs
    interest_ids = serializers.PrimaryKeyRelatedField(
        queryset=Interest.objects.all(),
        source='interests',  # This tells DRF to use this field to update the 'interests' M2M relationship
        many=True,
        write_only=True,
        required=False
    )

    bio = serializers.CharField(required=False, allow_blank=True)
    city = CitySerializer(read_only=True) # For displaying city details
    # For updating city, client should send the city ID
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        source='city', # This tells DRF to use this field to update the 'city' ForeignKey relationship
        write_only=True,
        allow_null=True, # Allow unsetting the city
        required=False
    )

    photos = PhotoSerializer(many=True, read_only=True)
    distance = serializers.FloatField(read_only=True, required=False) # To show distance when annotated

    class Meta:
        model = Profile
        fields = [
            'id', 'user_id', 'username', 'email', # User related info
            'age', 'bio', 'gender', 'phone_number', # Profile specific fields
            'city', 'city_id', # City relationship (read/write)
            'interests', 'interest_ids', # Interests relationship (read/write)
            'photos', # Associated photos
            'distance' # For potential future use or if annotated
        ]

    def update(self, instance, validated_data):
        # Interests and City are handled by DRF due to 'source' in PrimaryKeyRelatedField
        # for 'interest_ids' and 'city_id'.
        # No need to pop 'interests' or 'city' manually if using this pattern.

        # The 'interests' M2M field will be automatically handled by DRF if 'interest_ids' is in validated_data
        # The 'city' ForeignKey field will be automatically handled by DRF if 'city_id' is in validated_data

        instance = super().update(instance, validated_data)
        return instance

# You'll create SwipeSerializer later when building swipe functionality