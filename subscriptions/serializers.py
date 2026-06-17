from rest_framework import serializers
from .models import Plan, Subscription, PaymentTransaction


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'plan_type', 'price', 'description']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'status', "auto_renew",
            'trial_start', 'trial_end',
            'current_period_start', 'current_period_end',
            'cancelled_at', 'created_at',
        ]


class InitiatePaymentSerializer(serializers.Serializer):
    plan_type = serializers.ChoiceField(choices=['university', 'skills', 'combined'])
    gateway = serializers.ChoiceField(choices=['paystack', 'flutterwave'])


class PaymentTransactionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'plan', 'gateway', 'reference',
            'amount', 'status', 'created_at',
        ]