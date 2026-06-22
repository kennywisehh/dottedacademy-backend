from rest_framework import serializers
from accounts.models import User
from courses.models import (
    Course, Module, Lesson, Quiz, Question, Option, Enrollment, CourseReview, Certificate
)
from subscriptions.models import Plan, Subscription, PaymentTransaction
from universities.models import University, Faculty, Department
from skills.models import Industry, Category


# ── Users ──────────────────────────────────────────────────────────────────

class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'avatar', 'is_verified', 'is_active', 'date_joined',
        ]


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role', 'is_active', 'is_verified']


# ── Universities ────────────────────────────────────────────────────────────

class AdminUniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'abbreviation', 'logo', 'is_active', 'created_at']


class AdminFacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'is_active', 'created_at']


class AdminDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'is_active', 'created_at']


# ── Skills ──────────────────────────────────────────────────────────────────

class AdminIndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'name', 'icon', 'is_active', 'created_at']


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'is_active', 'created_at']


# ── Courses ─────────────────────────────────────────────────────────────────

class AdminCourseSerializer(serializers.ModelSerializer):
    instructor_email = serializers.EmailField(source='instructor.email', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'thumbnail', 'sector', 'level',
            'status', 'price', 'is_featured', 'enrolled_count', 'average_rating',
            'department', 'course_level', 'category', 'instructor', 'instructor_email',
            'created_at', 'updated_at',
        ]


class AdminModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'title', 'order', 'created_at']


class AdminLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'order', 'video_url', 'pdf_file',
            'text_content', 'duration_minutes', 'is_free_preview', 'created_at',
        ]


# ── Quizzes ─────────────────────────────────────────────────────────────────

class AdminOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']


class AdminQuestionSerializer(serializers.ModelSerializer):
    options = AdminOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'options', 'created_at']


class AdminQuizSerializer(serializers.ModelSerializer):
    questions = AdminQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'pass_score', 'questions', 'created_at']


# ── Reviews ─────────────────────────────────────────────────────────────────

class AdminReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = CourseReview
        fields = ['id', 'user_email', 'course_title', 'rating', 'comment', 'created_at']


# ── Revenue ──────────────────────────────────────────────────────────────────

class AdminTransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'user_email', 'plan_name', 'gateway',
            'reference', 'amount', 'status', 'created_at',
        ]