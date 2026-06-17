from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.PlanListView.as_view(), name='plan-list'),
    path('status/', views.SubscriptionStatusView.as_view(), name='subscription-status'),
    path('subscribe/', views.InitiatePaymentView.as_view(), name='initiate-payment'),
    path('verify/', views.VerifyPaymentView.as_view(), name='verify-payment'),
    path('cancel/', views.CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment-history'),
    path('webhook/paystack/', views.PaystackWebhookView.as_view(), name='paystack-webhook'),
    path('webhook/flutterwave/', views.FlutterwaveWebhookView.as_view(), name='flutterwave-webhook'),
    path('auto-renew/', views.AutoRenewToggleView.as_view(), name='auto-renew-toggle'),
]