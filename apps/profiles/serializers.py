from rest_framework import serializers
from .models import Profile, Interest, Photo # Removed Swipe from this import
from django.contrib.auth import get_user_model

User = get_user_model()

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
    user = serializers.StringRelatedField(read_only=True) # Display username
    interests = InterestSerializer(many=True, read_only=False, required=False) # Made 'required=False' for partial updates
    photos = PhotoSerializer(many=True, read_only=True) # Add this line
    distance = serializers.FloatField(read_only=True, required=False) # To show distance when annotated

    class Meta:
        model = Profile
        fields = [
                    'user', 'age', 'location', 'interests',
                    'photos', 'bio', 'distance' # Add photos here
                ]
        read_only_fields = ['user']
        # For location, you might need a custom serializer field if using GeoDjango REST framework extensions

    def get_location(self, obj):
        # If you want to return a more user-friendly format for the location
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None

    def update(self, instance, validated_data):
        interests_data = validated_data.pop('interests', None)
        
        # Update other Profile fields using the parent's update method
        instance = super().update(instance, validated_data)

        if interests_data is not None:
            # interests_data is a list of dicts, e.g., 
            # [{'id': 1, 'name': 'Music'}, {'name': 'Sports'}]
            # We need to convert this to a list of Interest instances for .set()
            
            current_interest_instances = []
            for interest_dict in interests_data:
                interest_id = interest_dict.get('id')
                # 'name' is unique in your Interest model
                interest_name = interest_dict.get('name') 

                if interest_id:
                    # If ID is provided, try to fetch the existing interest.
                    try:
                        interest_obj = Interest.objects.get(pk=interest_id)
                        # Optional: If name is also provided and differs, you might want to update it.
                        # This depends on whether profile updates should modify global Interest records.
                        # For now, we'll assume if ID is given, it's just for association.
                        # If you wanted to update the interest name:
                        # if interest_name and interest_obj.name != interest_name:
                        #     interest_obj.name = interest_name
                        #     interest_obj.save()
                        current_interest_instances.append(interest_obj)
                    except Interest.DoesNotExist:
                        # Handle cases where an invalid ID might be passed.
                        # You could raise a ValidationError or simply skip.
                        # For example:
                        # raise serializers.ValidationError(
                        #     {f"interests": f"Interest with id {interest_id} not found."}
                        # )
                        pass # Skipping for now
                elif interest_name:
                    # If only name is provided, get or create the interest.
                    # This leverages the 'unique=True' on Interest.name.
                    interest_obj, created = Interest.objects.get_or_create(name=interest_name)
                    current_interest_instances.append(interest_obj)
                # Else: The interest_dict might be malformed (e.g., empty or missing both id and name).
                # You might want to add error handling or logging here.

            instance.interests.set(current_interest_instances)
        
        return instance

# You'll create SwipeSerializer later when building swipe functionality
