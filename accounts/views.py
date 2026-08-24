from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as s
from .models import EmailVerificationToken, PasswordResetToken
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    VerifyEmailSerializer
)
from .tasks import send_verification_email_task, send_password_reset_email_task
from learner.models import Streak
from datetime import timedelta
from sib_api_v3_sdk.rest import ApiException
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: inline_serializer('RegisterResponse', fields={
                'message': s.CharField(),
                'user': UserSerializer(),
            }),
            400: OpenApiResponse(description='Validation error'),
        },
        summary='Register a new user',
        tags=['Auth'],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token_obj, _ = EmailVerificationToken.objects.get_or_create(user=user)
            try:
                send_verification_email_task(user.first_name, user.email, token_obj.token)
            except ApiException:
                logger.error(f"Verification email failed to send for {user.email}")
            Streak.objects.create(user=user)
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: inline_serializer('LoginResponse', fields={
                'access': s.CharField(),
                'refresh': s.CharField(),
                'user': UserSerializer(),
            }),
            400: OpenApiResponse(description='Invalid credentials'),
        },
        summary='Login with email and password',
        tags=['Auth'],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            Streak.record_login(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer('LogoutRequest', fields={
            'refresh': s.CharField(),
        }),
        responses={
            200: OpenApiResponse(description='Logged out successfully'),
            400: OpenApiResponse(description='Invalid or missing refresh token'),
        },
        summary='Logout and blacklist refresh token',
        tags=['Auth'],
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=inline_serializer('TokenRefreshRequest', fields={
            'refresh': s.CharField(),
        }),
        responses={
            200: inline_serializer('TokenRefreshResponse', fields={
                'access': s.CharField(),
                'refresh': s.CharField(),
            }),
            400: OpenApiResponse(description='Invalid or missing refresh token'),
        },
        summary='Refresh access token',
        tags=['Auth'],
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            return Response({
                'access': str(token.access_token),
                'refresh': str(token)
            }, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


OTP_EXPIRY_MINUTES = 15


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyEmailSerializer,
        responses={
            200: inline_serializer('VerifyEmailResponse', fields={
                'message': s.CharField(),
                'access': s.CharField(),
                'refresh': s.CharField(),
                'user': UserSerializer(),
            }),
            400: OpenApiResponse(description='Invalid or expired token'),
        },
        summary='Verify email with token',
        tags=['Auth'],
    )
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            try:
                token_obj = EmailVerificationToken.objects.get(token=token)

                expiry_cutoff = timezone.now() - timedelta(minutes=OTP_EXPIRY_MINUTES)
                if token_obj.created_at < expiry_cutoff:
                    token_obj.delete()
                    return Response({'error': 'This code has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

                user = token_obj.user
                user.is_verified = True
                user.save()
                token_obj.delete()

                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Email verified successfully.',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data,
                }, status=status.HTTP_200_OK)
            except EmailVerificationToken.DoesNotExist:
                return Response({'error': 'Invalid or expired verification token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(description='Reset email sent if account exists'),
            400: OpenApiResponse(description='Validation error'),
        },
        summary='Request password reset email',
        tags=['Auth'],
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
                token_obj = PasswordResetToken.objects.create(user=user)
                try:
                    send_password_reset_email_task(user.first_name, user.email, token_obj.token)
                except ApiException:
                    logger.error(f"Password reset email failed to send for {user.email}")
            except User.DoesNotExist:
                pass
            return Response({'message': 'If this email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(description='Password reset successful'),
            400: OpenApiResponse(description='Invalid or expired token'),
        },
        summary='Confirm password reset with token',
        tags=['Auth'],
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            try:
                token_obj = PasswordResetToken.objects.get(token=token, is_used=False)

                expiry_cutoff = timezone.now() - timedelta(minutes=OTP_EXPIRY_MINUTES)
                if token_obj.created_at < expiry_cutoff:
                    token_obj.is_used = True
                    token_obj.save()
                    return Response({'error': 'This code has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

                user = token_obj.user
                user.set_password(password)
                user.save()
                token_obj.is_used = True
                token_obj.save()
                return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
            except PasswordResetToken.DoesNotExist:
                return Response({'error': 'Invalid or expired reset token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=inline_serializer('ResendVerificationRequest', fields={
            'email': s.EmailField(),
        }),
        responses={
            200: OpenApiResponse(description='Verification email sent if account exists'),
            400: OpenApiResponse(description='Email is required'),
        },
        summary='Resend email verification link',
        tags=['Auth'],
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                return Response({'message': 'This account is already verified.'}, status=status.HTTP_200_OK)
            EmailVerificationToken.objects.filter(user=user).delete()
            token_obj = EmailVerificationToken.objects.create(user=user)
            try:
                send_verification_email_task(user.first_name, user.email, token_obj.token)
            except ApiException:
                logger.error(f"Verification email resend failed for {user.email}")
            return Response({'message': 'Verification email resent. Please check your inbox.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'If this email exists, a verification email has been sent.'}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer()},
        summary='Get current user profile',
        tags=['Auth'],
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserSerializer,
        responses={
            200: UserSerializer(),
            400: OpenApiResponse(description='Validation error'),
        },
        summary='Update current user profile',
        tags=['Auth'],
    )
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: OpenApiResponse(description='Account deactivated successfully')},
        summary='Deactivate current user account',
        tags=['Auth'],
    )
    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({'message': 'Account deactivated successfully.'}, status=status.HTTP_200_OK)