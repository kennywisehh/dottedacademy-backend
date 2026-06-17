from rest_framework import serializers
from courses.models import Enrollment, Certificate, Bookmark, Lesson
from .models import Streak, ActivityFeed


class EnrolledCourseSerializer(serializers.ModelSerializer):
    course_id = serializers.UUIDField(source='course.id', read_only=True)
    title = serializers.CharField(source='course.title', read_only=True)
    thumbnail = serializers.ImageField(source='course.thumbnail', read_only=True)
    sector = serializers.CharField(source='course.sector', read_only=True)
    level = serializers.CharField(source='course.level', read_only=True)
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            'course_id', 'title', 'thumbnail', 'sector', 'level',
            'enrolled_at', 'completed_at', 'is_completed', 'progress_percent',
        ]

    def get_progress_percent(self, obj):
        total_lessons = Lesson.objects.filter(module__course=obj.course).count()
        if total_lessons == 0:
            return 0
        completed_lessons = obj.user.lesson_progress.filter(
            lesson__module__course=obj.course, is_completed=True
        ).count()
        return round((completed_lessons / total_lessons) * 100)


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'course', 'course_title', 'certificate_id', 'issued_at']


class BookmarkSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_id = serializers.UUIDField(source='lesson.module.course.id', read_only=True)
    course_title = serializers.CharField(source='lesson.module.course.title', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'lesson', 'lesson_title', 'course_id', 'course_title', 'created_at']


class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = [
            'login_current_streak', 'login_longest_streak', 'last_login_date',
            'course_current_streak', 'course_longest_streak', 'last_course_activity_date',
        ]


class ActivityFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityFeed
        fields = ['id', 'description', 'created_at']