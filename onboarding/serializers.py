from rest_framework import serializers
from .models import OnboardingProfile, UniversityProfile, SkillsProfile


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingProfile
        fields = ['selected_section']

    def validate_selected_section(self, value):
        if value not in ['university', 'skills', 'both']:
            raise serializers.ValidationError('Invalid section choice.')
        return value


class UniversityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityProfile
        fields = ['university', 'faculty', 'department', 'level']

    def validate(self, data):
        faculty = data.get('faculty')
        department = data.get('department')
        university = data.get('university')

        if faculty and faculty.university != university:
            raise serializers.ValidationError('Faculty does not belong to the selected university.')

        if department and department.faculty != faculty:
            raise serializers.ValidationError('Department does not belong to the selected faculty.')

        return data


class SkillsProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillsProfile
        fields = ['interests']

    def validate_interests(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError('Please select at least one interest.')
        return value


class OnboardingStatusSerializer(serializers.ModelSerializer):
    section_complete = serializers.SerializerMethodField()
    university_profile_complete = serializers.SerializerMethodField()
    skills_profile_complete = serializers.SerializerMethodField()

    class Meta:
        model = OnboardingProfile
        fields = [
            'selected_section',
            'section_complete',
            'university_profile_complete',
            'skills_profile_complete',
            'is_completed',
        ]

    def get_section_complete(self, obj):
        return obj.selected_section is not None

    def get_university_profile_complete(self, obj):
        return hasattr(obj, 'university_profile')

    def get_skills_profile_complete(self, obj):
        if not hasattr(obj, 'skills_profile'):
            return False
        return obj.skills_profile.interests.exists()