# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomerProfile, EmailVerification
import bleach

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    pass


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, write_only=True)


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, required=True)
    password2 = serializers.CharField(write_only=True, min_length=6, required=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    avatar = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2', 'phone', 'address', 'avatar']

    def validate_username(self, value):
        if " " in value:
            raise serializers.ValidationError("Username cannot contain spaces.")
        return value.strip()

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_address(self, value):
        return bleach.clean(value.strip(), tags=[], strip=True)

    def validate_phone(self, value):
        value = value.strip()
        if value and (not value.isdigit() or len(value) < 8):
            raise serializers.ValidationError("Invalid phone number.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords did not match."})
        return attrs

    def create(self, validated_data):
        phone = validated_data.pop('phone', None)
        address = validated_data.pop('address', None)
        avatar = validated_data.pop('avatar', None)
        validated_data.pop('password2')

        user = User(username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()

        CustomerProfile.objects.create(user=user, phone=phone, address=address, avatar=avatar)

        # Create email verification record
        EmailVerification.objects.get_or_create(user=user)

        return user
