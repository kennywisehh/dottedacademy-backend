from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import OnboardingProfile, UniversityProfile, SkillsProfile
from .serializers import (
    SectionSerializer,
    UniversityProfileSerializer,
    SkillsProfileSerializer,
    OnboardingStatusSerializer,
)
from subscriptions.models import Plan, Subscription
from django.utils import timezone
from datetime import timedelta

class SectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        onboarding, _ = OnboardingProfile.objects.get_or_create(user=request.user)

        if onboarding.selected_section:
            return Response(
                {'detail': 'Section already selected. Use the update endpoint.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SectionSerializer(onboarding, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SectionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            onboarding = OnboardingProfile.objects.get(user=request.user)
        except OnboardingProfile.DoesNotExist:
            return Response(
                {'detail': 'Onboarding profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SectionSerializer(onboarding, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UniversityProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            onboarding = OnboardingProfile.objects.get(user=request.user)
        except OnboardingProfile.DoesNotExist:
            return Response(
                {'detail': 'Complete section selection first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if onboarding.selected_section not in ['university', 'both']:
            return Response(
                {'detail': 'You did not select university as a section.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if hasattr(onboarding, 'university_profile'):
            return Response(
                {'detail': 'University profile already exists. Use the update endpoint.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UniversityProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(onboarding=onboarding)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UniversityProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            onboarding = OnboardingProfile.objects.get(user=request.user)
            university_profile = onboarding.university_profile
        except OnboardingProfile.DoesNotExist:
            return Response(
                {'detail': 'Onboarding profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except UniversityProfile.DoesNotExist:
            return Response(
                {'detail': 'University profile not found. Use the create endpoint.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UniversityProfileSerializer(university_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkillsProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            onboarding = OnboardingProfile.objects.get(user=request.user)
        except OnboardingProfile.DoesNotExist:
            return Response(
                {'detail': 'Complete section selection first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if onboarding.selected_section not in ['skills', 'both']:
            return Response(
                {'detail': 'You did not select skills as a section.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if hasattr(onboarding, 'skills_profile'):
            return Response(
                {'detail': 'Skills profile already exists. Use the update endpoint.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SkillsProfileSerializer(data=request.data)
        if serializer.is_valid():
            skills_profile = serializer.save(onboarding=onboarding)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkillsProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            onboarding = OnboardingProfile.objects.get(user=request.user)
            skills_profile = onboarding.skills_profile
        except OnboardingProfile.DoesNotExist:
            return Response(
                {'detail': 'Onboarding profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except SkillsProfile.DoesNotExist:
            return Response(
                {'detail': 'Skills profile not found. Use the create endpoint.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SkillsProfileSerializer(skills_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OnboardingStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            onboarding = OnboardingProfile.objects.get(user=request.user)
        except OnboardingProfile.DoesNotExist:
            return Response(
                {'detail': 'Onboarding not started.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OnboardingStatusSerializer(onboarding)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OnboardingCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            onboarding = OnboardingProfile.objects.get(user=request.user)
        except OnboardingProfile.DoesNotExist:
            return Response(
                {'detail': 'Onboarding profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if onboarding.is_completed:
            return Response(
                {'detail': 'Onboarding already completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate all required steps are done
        section = onboarding.selected_section
        if not section:
            return Response(
                {'detail': 'Please select a section first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if section in ['university', 'both'] and not hasattr(onboarding, 'university_profile'):
            return Response(
                {'detail': 'Please complete your university profile.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if section in ['skills', 'both'] and not hasattr(onboarding, 'skills_profile'):
            return Response(
                {'detail': 'Please complete your skills profile.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        onboarding.is_completed = True
        onboarding.save()
        
        plan_type = 'combined' if section == 'both' else section
        try:
            plan = Plan.objects.get(plan_type=plan_type, is_active=True)
            Subscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'plan': plan,
                    'status': 'trial',
                    'trial_start': timezone.now(),
                    'trial_end': timezone.now() + timedelta(days=7),
                }
            )
        except Plan.DoesNotExist:
            pass  # fail silently, don't block onboarding completion

        return Response(
            {'detail': 'Onboarding complete. Your free trial has been activated.'},
            status=status.HTTP_200_OK
        )