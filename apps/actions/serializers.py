from rest_framework import serializers
from .models import Swipe # Import Swipe from the current app's models

class SwipeActionSerializer(serializers.ModelSerializer):
    # swiped_user_id is what the client will send
    swiped_user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Swipe
        fields = ['swiped_user_id', 'action'] # 'swiper' will be set from request.user
        read_only_fields = ['swiper', 'timestamp']

    def validate_action(self, value):
        if value.upper() not in ['LIKE', 'PASS']:
            raise serializers.ValidationError("Action must be 'LIKE' or 'PASS'.")
        return value.upper()