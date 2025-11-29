from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomerProfile
import bleach

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, label="Confirm password", min_length=6)

    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    avatar = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2', 'phone', 'address', 'avatar']

    # username validation
    def validate_username(self, value):
        if " " in value:
            raise serializers.ValidationError("Username cannot contain spaces.")
        return value.strip()

    # email validation
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value.lower().strip()

    # sanitization for address
    def validate_address(self, value):
        return bleach.clean(value.strip(), tags=[], strip=True)

    # phone validation
    def validate_phone(self, value):
        value = value.strip()
        if value and (not value.isdigit() or len(value) < 8):
            raise serializers.ValidationError("Invalid phone number.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match."})
        return attrs

    def create(self, validated_data):
        phone = validated_data.pop('phone', None)
        address = validated_data.pop('address', None)
        avatar = validated_data.pop('avatar', None)

        validated_data.pop('password2')

        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()

        CustomerProfile.objects.create(
            user=user,
            phone=phone,
            address=address,
            avatar=avatar
        )

        return user
