from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from apps.matches.models import Match # For creating matches
from .models import Swipe # Import Swipe from the current app's models
from .serializers import SwipeActionSerializer

User = get_user_model()

class SwipeActionView(generics.CreateAPIView):
    """
    Allows the authenticated user to swipe (like/pass) on another user.
    If a mutual 'LIKE' occurs, a Match and Conversation are created.
    """
    serializer_class = SwipeActionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        swiper = self.request.user
        swiped_user_id = serializer.validated_data.pop('swiped_user_id')
        action = serializer.validated_data.get('action')

        swiped_user = get_object_or_404(User, id=swiped_user_id)

        if swiper == swiped_user:
            # Using Response for error, DRF handles raising ValidationError from serializer
            # but this is a view-level validation.
            # Consider raising serializers.ValidationError in the serializer's validate method.
            raise serializers.ValidationError({"detail": "You cannot swipe on yourself."})

        # Create or update the swipe action
        swipe_instance, created = Swipe.objects.update_or_create(
            swiper=swiper,
            swiped_user=swiped_user,
            defaults={'action': action}
        )
        serializer.instance = swipe_instance # So serializer can return the created/updated instance

        # Check for a mutual like
        if action == 'LIKE':
            try:
                reverse_swipe = Swipe.objects.get(swiper=swiped_user, swiped_user=swiper, action='LIKE')
                # Mutual like! Create a match and conversation.
                match, conversation = Match.create_match_and_conversation(swiper, swiped_user)
                # TODO: Optionally, send notifications to both users about the new match.
            except Swipe.DoesNotExist:
                # Not a mutual like yet
                pass