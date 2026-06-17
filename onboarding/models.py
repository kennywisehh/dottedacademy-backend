import uuid
from django.db import models
from accounts.models import User


class OnboardingProfile(models.Model):
    SECTION_CHOICES = [
        ('university', 'University'),
        ('skills', 'Skills'),
        ('both', 'Both'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='onboarding')
    selected_section = models.CharField(max_length=20, choices=SECTION_CHOICES, blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Onboarding for {self.user.email}'


class UniversityProfile(models.Model):
    LEVEL_CHOICES = [
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
        ('500', '500 Level'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    onboarding = models.OneToOneField(OnboardingProfile, on_delete=models.CASCADE, related_name='university_profile')
    university = models.ForeignKey('universities.University', on_delete=models.SET_NULL, null=True)
    faculty = models.ForeignKey('universities.Faculty', on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey('universities.Department', on_delete=models.SET_NULL, null=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Uni profile for {self.onboarding.user.email}'


class SkillsProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    onboarding = models.OneToOneField(OnboardingProfile, on_delete=models.CASCADE, related_name='skills_profile')
    interests = models.ManyToManyField('skills.Category', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Skills profile for {self.onboarding.user.email}'