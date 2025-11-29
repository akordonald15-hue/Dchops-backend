from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
import logging
from rest_framework.throttling import UserRateThrottle
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .models import EmailVerification
from .models import CustomerProfile

# --------------------------
# YOUR EXISTING SECURITY CODE
# --------------------------
admin_logger = logging.getLogger('admin_actions')

class AdminThrottle(UserRateThrottle):
    rate = '30/hour'  # max 50 requests per hour for admin users
class OTPThrottle(UserRateThrottle):
    rate = '10/hour'
# --------------------------
# Register / Signup View
# --------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Validate first
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        user = serializer.save()

        phone = self.request.data.get("phone", "").strip()
        avatar = (
            self.request.FILES.get("avatar")
            if hasattr(self.request, "FILES")
            else None
        )

        # SAFE profile creation
        profile, created = CustomerProfile.objects.get_or_create(
            user=user,
            defaults={
                "phone": phone,
                "avatar": avatar,
            }
        )

        # Create verification entry
        verification, _ = EmailVerification.objects.get_or_create(user=user)
        verification.generate_otp()

        print("Generated OTP:", verification.otp)  # <--- Add this to debug

        # Send email
        send_mail(
            subject="Your Verification Code",
            message=f"Your verification code is {verification.otp}",
            from_email="akordonald15@gmail.com",
            recipient_list=[user.email],
            fail_silently=False,
        )


# --------------------------
# Email Verification View
# --------------------------
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)
            verification = EmailVerification.objects.get(user=user)
        except (User.DoesNotExist, EmailVerification.DoesNotExist):
            return Response({'detail': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)

        if verification.otp == otp:
            verification.is_verified = True
            verification.otp = None
            verification.save()
            return Response({'detail': 'Email verified successfully'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

# --------------------------
# Login View (restrict unverified users)
# --------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            # Check if user is verified
            try:
                if not user.verification.is_verified:
                    return Response({'detail': 'Email not verified'}, status=status.HTTP_403_FORBIDDEN)
            except EmailVerification.DoesNotExist:
                return Response({'detail': 'Verification record missing'}, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)
            response = Response({
                'access': str(refresh.access_token),
                'user': {'username': user.username, 'email': user.email}
            }, status=status.HTTP_200_OK)

            # Set HttpOnly refresh token cookie
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,       # True in production (HTTPS)
                samesite='Lax',
                max_age=7*24*60*60
            )
            return response

        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# --------------------------
# Refresh Token View
# --------------------------
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'detail': 'Refresh token missing'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = RefreshToken(refresh_token)
            new_access = str(token.access_token)
            return Response({'access': new_access})
        except Exception:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

# --------------------------
# Logout View
# --------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        response = Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')
        return response
