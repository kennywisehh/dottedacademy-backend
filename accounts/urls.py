from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, TokenRefreshView,
    VerifyEmailView, PasswordResetRequestView, PasswordResetConfirmView,
    ResendVerificationEmailView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('resend-verification-email/', ResendVerificationEmailView.as_view(), name='resend-verification-email'),
]