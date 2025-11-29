from rest_framework import serializers
from .models import Review
import bleach

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = '__all__'

    def validate_comment(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError("Comment is too short.")

        # sanitize HTML
        value = bleach.clean(value, tags=[], attributes={}, strip=True)

        return value

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
