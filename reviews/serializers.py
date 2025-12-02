from rest_framework import serializers
from .models import Review
import bleach


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    status = serializers.ReadOnlyField()  # only admin can change

    class Meta:
        model = Review
        fields = ['id', 'user_id', 'user', 'menu_item', 'rating', 'text', 'status', 'created_at']
        read_only_fields = ['id', 'user_id', 'user', 'status', 'created_at']

    # -------------------------
    # Validate text
    # -------------------------
    def validate_text(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Review text is too short (minimum 3 characters).")

        # Sanitize HTML/XSS
        value = bleach.clean(value, tags=[], attributes={}, strip=True)
        return value

    # -------------------------
    # Validate rating
    # -------------------------
    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    # -------------------------
    # Assign user automatically with auth check
    # -------------------------
    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        
        if user is None or user.is_anonymous:
            raise serializers.ValidationError("Authentication required to post a review.")
        
        return Review.objects.create(user=user, **validated_data)