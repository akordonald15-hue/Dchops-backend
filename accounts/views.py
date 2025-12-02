from rest_framework import generics, status, permissions
from rest_framework.generics import ListAPIView
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from rest_framework.throttling import UserRateThrottle

import logging

from .models import EmailVerification, CustomerProfile
from .serializers import (
    UserSerializer,
    LoginSerializer,
    LogoutSerializer,
    VerifyEmailSerializer,
    RefreshTokenSerializer
)

from orders.models import Order
from orders.serializers import OrderSerializer

User = get_user_model()

admin_logger = logging.getLogger('admin_actions')


class AdminThrottle(UserRateThrottle):
    rate = '30/hour'


class OTPThrottle(UserRateThrottle):
    rate = '10/hour'


# -------------------------------------------
# Order List (Admin / Tests)
# -------------------------------------------
class OrderListAPIView(ListAPIView):
    """
    Admin endpoint to view all orders.
    Only accessible to staff/admin users.
    """
    queryset = Order.objects.select_related('user').prefetch_related('items__menu_item')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    throttle_classes = [AdminThrottle]


# -------------------------------------------
# Register View
# -------------------------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # --- Create Profile ---
        phone = request.data.get("phone", "").strip()
        avatar = request.FILES.get("avatar") if hasattr(request, "FILES") else None

        CustomerProfile.objects.get_or_create(
            user=user,
            defaults={"phone": phone, "avatar": avatar}
        )

        # --- OTP generation ---
        verification, _ = EmailVerification.objects.get_or_create(user=user)
        verification.generate_otp()

        # Send email with error handling
        try:
            send_mail(
                subject="Your Verification Code",
                message=f"Your verification code is {verification.otp}",
                from_email="akordonald15@gmail.com",
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            admin_logger.warning(f"Email send failed for user {user.id}: {str(e)}")

        # ✅ Return 201 with user data
        return Response({
            "success": True,
            "message": "Registration successful. Please verify your email.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_201_CREATED)

# -------------------------------------------
# Verify Email
# -------------------------------------------
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
            verification = EmailVerification.objects.get(user=user)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)
        except EmailVerification.DoesNotExist:
            return Response({'detail': 'Verification record missing'}, status=status.HTTP_400_BAD_REQUEST)

        if verification.otp == otp:
            verification.is_verified = True
            verification.otp = None
            verification.save()
            admin_logger.info(f"User {user.id} email verified: {email}")
            return Response({'detail': 'Email verified successfully'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------
# Login View
# -------------------------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if not user:
            admin_logger.warning(f"Failed login attempt for username: {username}")
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Require email verification
        try:
            verification = EmailVerification.objects.get(user=user)
            if not verification.is_verified:
                return Response({'detail': 'Email not verified'}, status=status.HTTP_403_FORBIDDEN)
        except EmailVerification.DoesNotExist:
            return Response({'detail': 'Verification record missing'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        admin_logger.info(f"User {user.id} logged in successfully")

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        }, status=status.HTTP_200_OK)


# -------------------------------------------
# Refresh Token
# -------------------------------------------
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data['refresh_token']

        try:
            token = RefreshToken(refresh_token)
            return Response({"access": str(token.access_token)}, status=status.HTTP_200_OK)
        except Exception as e:
            admin_logger.warning(f"Invalid token refresh attempt: {str(e)}")
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)


# -------------------------------------------
# Logout View
# -------------------------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        admin_logger.info(f"User {request.user.id} logged out")
        return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)