from django.utils import timezone
from django.conf import settings
import hmac
import hashlib
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as s
from .models import Plan, Subscription, PaymentTransaction
from .serializers import (
    PlanSerializer,
    SubscriptionSerializer,
    InitiatePaymentSerializer,
    PaymentTransactionSerializer,
)
from .utils import (
    generate_reference,
    initiate_paystack,
    initiate_flutterwave,
    verify_paystack,
    verify_flutterwave,
    process_payment_reference,
)


class PlanListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PlanSerializer(many=True)},
        summary='List active subscription plans',
        tags=['Subscriptions'],
    )
    def get(self, request):
        plans = Plan.objects.filter(is_active=True)
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)


class SubscriptionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: SubscriptionSerializer,
            404: OpenApiResponse(description='No subscription found'),
        },
        summary='Get current user subscription status',
        tags=['Subscriptions'],
    )
    def get(self, request):
        try:
            subscription = request.user.subscription
        except Subscription.DoesNotExist:
            return Response({'detail': 'No subscription found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=InitiatePaymentSerializer,
        responses={
            200: inline_serializer('InitiatePaymentResponse', fields={
                'reference': s.CharField(),
                'payment_url': s.CharField(),
                'gateway': s.CharField(),
                'plan': PlanSerializer(),
                'amount': s.DecimalField(max_digits=10, decimal_places=2),
            }),
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Plan not found'),
            502: OpenApiResponse(description='Payment gateway error'),
        },
        summary='Initiate a subscription payment',
        tags=['Subscriptions'],
    )
    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        plan_type = serializer.validated_data['plan_type']
        gateway = serializer.validated_data['gateway']
        try:
            plan = Plan.objects.get(plan_type=plan_type, is_active=True)
        except Plan.DoesNotExist:
            return Response({'detail': 'Plan not found.'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        reference = generate_reference()
        callback_url = f"{settings.FRONTEND_URL}/subscription/verify?reference={reference}&gateway={gateway}"
        try:
            if gateway == 'paystack':
                payment_data = initiate_paystack(
                    email=user.email,
                    amount_naira=plan.price,
                    reference=reference,
                    callback_url=callback_url,
                )
            else:
                payment_data = initiate_flutterwave(
                    email=user.email,
                    amount_naira=plan.price,
                    reference=reference,
                    callback_url=callback_url,
                    name=user.full_name or user.email,
                )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        PaymentTransaction.objects.create(
            user=user,
            plan=plan,
            gateway=gateway,
            reference=reference,
            amount=plan.price,
            status='pending',
        )
        return Response({
            'reference': payment_data['reference'],
            'payment_url': payment_data['payment_url'],
            'gateway': gateway,
            'plan': PlanSerializer(plan).data,
            'amount': plan.price,
        }, status=status.HTTP_200_OK)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer('VerifyPaymentRequest', fields={
            'reference': s.CharField(),
            'gateway': s.CharField(),
        }),
        responses={
            200: inline_serializer('VerifyPaymentResponse', fields={
                'detail': s.CharField(),
                'reference': s.CharField(),
                'gateway': s.CharField(),
                'subscription': SubscriptionSerializer(),
            }),
            400: OpenApiResponse(description='Payment verification failed'),
            404: OpenApiResponse(description='Transaction not found'),
        },
        summary='Verify a subscription payment',
        tags=['Subscriptions'],
    )
    def post(self, request):
        reference = request.data.get('reference')
        gateway = request.data.get('gateway')
        if not reference or not gateway:
            return Response({'detail': 'reference and gateway are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            transaction = PaymentTransaction.objects.get(reference=reference, user=request.user)
        except PaymentTransaction.DoesNotExist:
            return Response({'detail': 'Transaction not found.'}, status=status.HTTP_404_NOT_FOUND)
        if transaction.status == 'success':
            return Response({'detail': 'Payment already verified.'}, status=status.HTTP_200_OK)
        success = process_payment_reference(reference, gateway)
        if not success:
            return Response({'detail': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
        transaction.refresh_from_db()
        return Response({
            'detail': 'Payment successful. Subscription activated.',
            'reference': reference,
            'gateway': gateway,
            'subscription': SubscriptionSerializer(transaction.subscription).data,
        }, status=status.HTTP_200_OK)


class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description='Subscription cancelled successfully'),
            400: OpenApiResponse(description='Subscription already inactive'),
            404: OpenApiResponse(description='No subscription found'),
        },
        summary='Cancel current subscription',
        tags=['Subscriptions'],
    )
    def post(self, request):
        try:
            subscription = request.user.subscription
        except Subscription.DoesNotExist:
            return Response({'detail': 'No subscription found.'}, status=status.HTTP_404_NOT_FOUND)
        if subscription.status in ['cancelled', 'expired']:
            return Response({'detail': 'Subscription is already inactive.'}, status=status.HTTP_400_BAD_REQUEST)
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.save()
        return Response({'detail': 'Subscription cancelled successfully.'}, status=status.HTTP_200_OK)


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PaymentTransactionSerializer(many=True)},
        summary='Get payment history for current user',
        tags=['Subscriptions'],
    )
    def get(self, request):
        transactions = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')
        serializer = PaymentTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class PaystackWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description='Webhook received'),
            401: OpenApiResponse(description='Invalid signature'),
        },
        summary='Paystack webhook receiver',
        tags=['Webhooks'],
    )
    def post(self, request):
        signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
        secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
        computed_signature = hmac.new(secret, request.body, hashlib.sha512).hexdigest()
        if not hmac.compare_digest(computed_signature, signature):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        event = request.data
        if event.get('event') == 'charge.success':
            reference = event.get('data', {}).get('reference')
            if reference:
                process_payment_reference(reference, 'paystack')
        return Response(status=status.HTTP_200_OK)


class FlutterwaveWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description='Webhook received'),
            401: OpenApiResponse(description='Invalid signature'),
        },
        summary='Flutterwave webhook receiver',
        tags=['Webhooks'],
    )
    def post(self, request):
        received_hash = request.META.get('HTTP_VERIF_HASH', '')
        if received_hash != settings.FLUTTERWAVE_SECRET_HASH:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        event = request.data
        if event.get('event') == 'charge.completed':
            reference = event.get('data', {}).get('tx_ref')
            if reference:
                process_payment_reference(reference, 'flutterwave')
        return Response(status=status.HTTP_200_OK)


class AutoRenewToggleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer('AutoRenewRequest', fields={
            'auto_renew': s.BooleanField(),
        }),
        responses={
            200: SubscriptionSerializer,
            400: OpenApiResponse(description='auto_renew boolean is required'),
            404: OpenApiResponse(description='No subscription found'),
        },
        summary='Toggle auto-renew for subscription',
        tags=['Subscriptions'],
    )
    def patch(self, request):
        try:
            subscription = request.user.subscription
        except Subscription.DoesNotExist:
            return Response({'detail': 'No subscription found.'}, status=status.HTTP_404_NOT_FOUND)
        auto_renew = request.data.get('auto_renew')
        if not isinstance(auto_renew, bool):
            return Response({'detail': 'auto_renew (boolean) is required.'}, status=status.HTTP_400_BAD_REQUEST)
        subscription.auto_renew = auto_renew
        subscription.save()
        return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_200_OK)