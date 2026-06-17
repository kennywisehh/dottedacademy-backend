from rest_framework import serializers
from .models import (
    Course, Module, Lesson, Quiz, Question, Option,
    Enrollment, LessonProgress, QuizAttempt, Certificate,
    CourseReview, Bookmark,
)


# ─── Option & Question ───────────────────────────────────────────────

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'options']


# ─── Quiz ────────────────────────────────────────────────────────────

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'pass_score']


class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ['id', 'score', 'passed', 'attempted_at']


class SubmitQuizSerializer(serializers.Serializer):
    # expects: {"answers": [{"question_id": "uuid", "option_id": "uuid"}, ...]}
    answers = serializers.ListField(
        child=serializers.DictField()
    )


# ─── Lesson ──────────────────────────────────────────────────────────

class LessonListSerializer(serializers.ModelSerializer):
    has_quiz = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'order', 'duration_minutes',
            'is_free_preview', 'has_quiz',
            'video_url', 'pdf_file', 'text_content',
        ]

    def get_has_quiz(self, obj):
        return hasattr(obj, 'quiz')


class LessonDetailSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'order', 'duration_minutes',
            'is_free_preview', 'video_url', 'pdf_file',
            'text_content', 'quiz', 'is_completed',
        ]

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return LessonProgress.objects.filter(
            user=request.user, lesson=obj, is_completed=True
        ).exists()


# ─── Module ──────────────────────────────────────────────────────────

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'title', 'order']


class ModuleWithLessonsSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title', 'order', 'lesson_count', 'lessons']

    def get_lesson_count(self, obj):
        return obj.lessons.count()


# ─── Course Review ───────────────────────────────────────────────────

class CourseReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = CourseReview
        fields = ['id', 'user_email', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user_email', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value


# ─── Course ──────────────────────────────────────────────────────────

class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'thumbnail', 'sector', 'level',
            'course_level', 'price', 'is_featured',
            'enrolled_count', 'average_rating',
            'instructor_name', 'category_name', 'department_name',
            'created_at',
        ]

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() or obj.instructor.email


class CourseDetailSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    modules = ModuleWithLessonsSerializer(many=True, read_only=True)
    reviews = CourseReviewSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'thumbnail', 'sector',
            'level', 'course_level', 'price', 'is_featured',
            'enrolled_count', 'average_rating',
            'instructor_name', 'category_name', 'department_name',
            'modules', 'reviews', 'is_enrolled', 'created_at',
        ]

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() or obj.instructor.email

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Enrollment.objects.filter(user=request.user, course=obj).exists()


# ─── Enrollment ──────────────────────────────────────────────────────

class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'enrolled_at', 'is_completed', 'completed_at']


# ─── Certificate ─────────────────────────────────────────────────────

class CertificateSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'certificate_id', 'course', 'issued_at']