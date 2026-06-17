from django.urls import path
from .views import (
    SectionView,
    SectionUpdateView,
    UniversityProfileView,
    UniversityProfileUpdateView,
    SkillsProfileView,
    SkillsProfileUpdateView,
    OnboardingStatusView,
    OnboardingCompleteView,
)

urlpatterns = [
    path('section/', SectionView.as_view(), name='onboarding-section'),
    path('section/update/', SectionUpdateView.as_view(), name='onboarding-section-update'),
    path('university-profile/', UniversityProfileView.as_view(), name='onboarding-university-profile'),
    path('university-profile/update/', UniversityProfileUpdateView.as_view(), name='onboarding-university-profile-update'),
    path('skills-profile/', SkillsProfileView.as_view(), name='onboarding-skills-profile'),
    path('skills-profile/update/', SkillsProfileUpdateView.as_view(), name='onboarding-skills-profile-update'),
    path('status/', OnboardingStatusView.as_view(), name='onboarding-status'),
    path('complete/', OnboardingCompleteView.as_view(), name='onboarding-complete'),
]