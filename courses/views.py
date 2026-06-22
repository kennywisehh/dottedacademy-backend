from django.utils import timezone
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as s
from .models import (
    Course, Module, Lesson, Quiz, Question, Option,
    Enrollment, LessonProgress, QuizAttempt, Certificate,
    CourseReview, Bookmark,
)
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    ModuleSerializer, ModuleWithLessonsSerializer,
    LessonListSerializer, LessonDetailSerializer,
    QuizSerializer, QuestionSerializer,
    QuizAttemptSerializer, SubmitQuizSerializer,
    CourseReviewSerializer, EnrollmentSerializer,
    CertificateSerializer,
)
from subscriptions.models import Subscription
from learner.models import Streak, ActivityFeed


# ─── Helpers ─────────────────────────────────────────────────────────

def has_active_subscription(user):
    try:
        sub = user.subscription
        return sub.status in ['trial', 'active']
    except Subscription.DoesNotExist:
        return False


def is_enrolled(user, course):
    return Enrollment.objects.filter(user=user, course=course).exists()


def check_and_complete_course(user, course):
    total_lessons = Lesson.objects.filter(module__course=course).count()
    completed_lessons = LessonProgress.objects.filter(
        user=user, lesson__module__course=course, is_completed=True
    ).count()
    if total_lessons > 0 and total_lessons == completed_lessons:
        enrollment = Enrollment.objects.get(user=user, course=course)
        if not enrollment.is_completed:
            enrollment.is_completed = True
            enrollment.completed_at = timezone.now()
            enrollment.save()
            Certificate.objects.get_or_create(user=user, course=course)


# ─── Course Views ─────────────────────────────────────────────────────

class CourseListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CourseListSerializer(many=True), 403: OpenApiResponse(description='No active subscription')},
        summary='List all published courses',
        tags=['Courses'],
    )
    def get(self, request):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required to view courses.'}, status=status.HTTP_403_FORBIDDEN)
        queryset = Course.objects.filter(status='published')
        category = request.query_params.get('category')
        level = request.query_params.get('level')
        difficulty = request.query_params.get('difficulty')
        sector = request.query_params.get('sector')
        if category:
            queryset = queryset.filter(category__id=category)
        if level:
            queryset = queryset.filter(course_level=level)
        if difficulty:
            queryset = queryset.filter(level=difficulty)
        if sector:
            queryset = queryset.filter(sector=sector)
        serializer = CourseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class UniversityCourseListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CourseListSerializer(many=True), 403: OpenApiResponse(description='No active subscription')},
        summary='List university courses tailored to user profile',
        tags=['Courses'],
    )
    def get(self, request):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required.'}, status=status.HTTP_403_FORBIDDEN)
        queryset = Course.objects.filter(status='published', sector='university')
        try:
            university_profile = request.user.onboarding.university_profile
            department = university_profile.department
            course_level = university_profile.level
            queryset = queryset.filter(department=department, course_level=course_level)
        except Exception:
            pass
        serializer = CourseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class SkillsCourseListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CourseListSerializer(many=True), 403: OpenApiResponse(description='No active subscription')},
        summary='List skills courses',
        tags=['Courses'],
    )
    def get(self, request):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required.'}, status=status.HTTP_403_FORBIDDEN)
        queryset = Course.objects.filter(status='published', sector='skills')
        serializer = CourseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class CourseSearchView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CourseListSerializer(many=True), 403: OpenApiResponse(description='No active subscription')},
        summary='Search published courses',
        tags=['Courses'],
    )
    def get(self, request):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required.'}, status=status.HTTP_403_FORBIDDEN)
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response([])
        queryset = Course.objects.filter(status='published').filter(
            Q(title__icontains=q) | Q(description__icontains=q) |
            Q(category__name__icontains=q) | Q(department__name__icontains=q)
        )
        serializer = CourseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class FeaturedCourseListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CourseListSerializer(many=True), 403: OpenApiResponse(description='No active subscription')},
        summary='List featured courses',
        tags=['Courses'],
    )
    def get(self, request):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required.'}, status=status.HTTP_403_FORBIDDEN)
        queryset = Course.objects.filter(status='published', is_featured=True)
        serializer = CourseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class PopularCourseListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CourseListSerializer(many=True), 403: OpenApiResponse(description='No active subscription')},
        summary='List popular courses by enrollment count',
        tags=['Courses'],
    )
    def get(self, request):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required.'}, status=status.HTTP_403_FORBIDDEN)
        queryset = Course.objects.filter(status='published').order_by('-enrolled_count')[:20]
        serializer = CourseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CourseDetailSerializer, 403: OpenApiResponse(description='No active subscription'), 404: OpenApiResponse(description='Course not found')},
        summary='Get course detail',
        tags=['Courses'],
    )
    def get(self, request, id):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            course = Course.objects.get(id=id, status='published')
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CourseDetailSerializer(course, context={'request': request})
        return Response(serializer.data)


class CourseEnrollmentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: inline_serializer('EnrollmentStatusResponse', fields={'is_enrolled': s.BooleanField()}),
            404: OpenApiResponse(description='Course not found'),
        },
        summary='Check enrollment status for a course',
        tags=['Courses'],
    )
    def get(self, request, id):
        try:
            course = Course.objects.get(id=id, status='published')
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        enrolled = is_enrolled(request.user, course)
        return Response({'is_enrolled': enrolled})


class CourseEnrolledCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: inline_serializer('EnrolledCountResponse', fields={'enrolled_count': s.IntegerField()}),
            404: OpenApiResponse(description='Course not found'),
        },
        summary='Get enrolled count for a course',
        tags=['Courses'],
    )
    def get(self, request, id):
        try:
            course = Course.objects.get(id=id, status='published')
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'enrolled_count': course.enrolled_count})


class EnrollView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            201: OpenApiResponse(description='Enrolled successfully'),
            400: OpenApiResponse(description='Already enrolled'),
            403: OpenApiResponse(description='No active subscription'),
            404: OpenApiResponse(description='Course not found'),
        },
        summary='Enroll in a course',
        tags=['Courses'],
    )
    def post(self, request, id):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required to enroll.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            course = Course.objects.get(id=id, status='published')
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        if is_enrolled(request.user, course):
            return Response({'detail': 'Already enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)
        Enrollment.objects.create(user=request.user, course=course)
        course.enrolled_count += 1
        course.save(update_fields=['enrolled_count'])
        return Response({'detail': 'Enrolled successfully.'}, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description='Unenrolled successfully'),
            400: OpenApiResponse(description='Not enrolled'),
            404: OpenApiResponse(description='Course not found'),
        },
        summary='Unenroll from a course',
        tags=['Courses'],
    )
    def delete(self, request, id):
        try:
            course = Course.objects.get(id=id, status='published')
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
        except Enrollment.DoesNotExist:
            return Response({'detail': 'Not enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)
        enrollment.delete()
        course.enrolled_count = max(0, course.enrolled_count - 1)
        course.save(update_fields=['enrolled_count'])
        return Response({'detail': 'Unenrolled successfully.'}, status=status.HTTP_200_OK)


# ─── Module Views ─────────────────────────────────────────────────────

class ModuleListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ModuleWithLessonsSerializer(many=True), 403: OpenApiResponse(description='No active subscription'), 404: OpenApiResponse(description='Course not found')},
        summary='List modules for a course',
        tags=['Courses'],
    )
    def get(self, request, id):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            course = Course.objects.get(id=id, status='published')
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        modules = course.modules.all()
        serializer = ModuleWithLessonsSerializer(modules, many=True, context={'request': request})
        return Response(serializer.data)


class ModuleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ModuleWithLessonsSerializer, 403: OpenApiResponse(description='No active subscription'), 404: OpenApiResponse(description='Module not found')},
        summary='Get module detail',
        tags=['Courses'],
    )
    def get(self, request, id, module_id):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            course = Course.objects.get(id=id, status='published')
            module = course.modules.get(id=module_id)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Module.DoesNotExist:
            return Response({'detail': 'Module not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ModuleWithLessonsSerializer(module, context={'request': request})
        return Response(serializer.data)


# ─── Lesson Views ─────────────────────────────────────────────────────

class LessonListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: LessonListSerializer(many=True), 403: OpenApiResponse(description='No active subscription'), 404: OpenApiResponse(description='Module not found')},
        summary='List lessons in a module',
        tags=['Courses'],
    )
    def get(self, request, id, module_id):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            course = Course.objects.get(id=id, status='published')
            module = course.modules.get(id=module_id)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Module.DoesNotExist:
            return Response({'detail': 'Module not found.'}, status=status.HTTP_404_NOT_FOUND)
        lessons = module.lessons.all()
        serializer = LessonListSerializer(lessons, many=True, context={'request': request})
        return Response(serializer.data)


class LessonDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: LessonDetailSerializer, 403: OpenApiResponse(description='Not enrolled or no subscription'), 404: OpenApiResponse(description='Lesson not found')},
        summary='Get lesson detail',
        tags=['Courses'],
    )
    def get(self, request, id, module_id, lesson_id):
        if not has_active_subscription(request.user):
            return Response({'detail': 'An active subscription is required.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            course = Course.objects.get(id=id, status='published')
            module = course.modules.get(id=module_id)
            lesson = module.lessons.get(id=lesson_id)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Module.DoesNotExist:
            return Response({'detail': 'Module not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not lesson.is_free_preview and not is_enrolled(request.user, course):
            return Response({'detail': 'You must be enrolled to access this lesson.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = LessonDetailSerializer(lesson, context={'request': request})
        return Response(serializer.data)


# ─── Standalone Lesson Views ──────────────────────────────────────────

class StandaloneLessonDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: LessonDetailSerializer, 403: OpenApiResponse(description='Not enrolled'), 404: OpenApiResponse(description='Lesson not found')},
        summary='Get standalone lesson detail by lesson ID',
        tags=['Lessons'],
    )
    def get(self, request, id):
        try:
            lesson = Lesson.objects.get(id=id)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)
        course = lesson.module.course
        if not lesson.is_free_preview and not is_enrolled(request.user, course):
            return Response({'detail': 'You must be enrolled to access this lesson.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = LessonDetailSerializer(lesson, context={'request': request})
        return Response(serializer.data)


class LessonCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description='Lesson marked as complete'),
            403: OpenApiResponse(description='Not enrolled'),
            404: OpenApiResponse(description='Lesson not found'),
        },
        summary='Mark a lesson as complete',
        tags=['Lessons'],
    )
    def post(self, request, id):
        try:
            lesson = Lesson.objects.get(id=id)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)
        course = lesson.module.course
        if not is_enrolled(request.user, course):
            return Response({'detail': 'You must be enrolled to complete lessons.'}, status=status.HTTP_403_FORBIDDEN)
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user, lesson=lesson,
            defaults={'is_completed': True, 'completed_at': timezone.now()}
        )
        if not created and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
        check_and_complete_course(request.user, course)
        streak = Streak.record_activity(request.user, 'lesson_completed')
        if streak:
            ActivityFeed.objects.create(
                user=request.user,
                activity_type='streak',
                description=f'🔥 {streak.current_streak} day streak! Keep it up! 🔥'
            )
        return Response({'detail': 'Lesson marked as complete.'}, status=status.HTTP_200_OK)


class LessonBookmarkView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            201: OpenApiResponse(description='Lesson bookmarked'),
            400: OpenApiResponse(description='Already bookmarked'),
            404: OpenApiResponse(description='Lesson not found'),
        },
        summary='Bookmark a lesson',
        tags=['Lessons'],
    )
    def post(self, request, id):
        try:
            lesson = Lesson.objects.get(id=id)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, lesson=lesson)
        if not created:
            return Response({'detail': 'Already bookmarked.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Lesson bookmarked.'}, status=status.HTTP_201_CREATED)


# ─── Quiz Views ───────────────────────────────────────────────────────

class QuizQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: QuestionSerializer(many=True), 403: OpenApiResponse(description='Not enrolled'), 404: OpenApiResponse(description='Quiz not found')},
        summary='Get quiz questions',
        tags=['Quizzes'],
    )
    def get(self, request, id):
        try:
            quiz = Quiz.objects.get(id=id)
        except Quiz.DoesNotExist:
            return Response({'detail': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not is_enrolled(request.user, quiz.lesson.module.course):
            return Response({'detail': 'You must be enrolled to access this quiz.'}, status=status.HTTP_403_FORBIDDEN)
        questions = quiz.questions.prefetch_related('options').all()
        serializer = QuestionSerializer(questions, many=True)
        data = serializer.data
        for question in data:
            for option in question['options']:
                option.pop('is_correct', None)
        return Response(data)


class QuizAttemptsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: QuizAttemptSerializer(many=True), 404: OpenApiResponse(description='Quiz not found')},
        summary='List quiz attempts for current user',
        tags=['Quizzes'],
    )
    def get(self, request, id):
        try:
            quiz = Quiz.objects.get(id=id)
        except Quiz.DoesNotExist:
            return Response({'detail': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)
        attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-attempted_at')
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)


class QuizAttemptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: QuizAttemptSerializer, 404: OpenApiResponse(description='Attempt not found')},
        summary='Get a specific quiz attempt',
        tags=['Quizzes'],
    )
    def get(self, request, id, attempt_id):
        try:
            quiz = Quiz.objects.get(id=id)
            attempt = QuizAttempt.objects.get(id=attempt_id, user=request.user, quiz=quiz)
        except Quiz.DoesNotExist:
            return Response({'detail': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)
        except QuizAttempt.DoesNotExist:
            return Response({'detail': 'Attempt not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)


class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SubmitQuizSerializer,
        responses={
            201: inline_serializer('QuizSubmitResponse', fields={
                'score': s.IntegerField(),
                'passed': s.BooleanField(),
                'correct': s.IntegerField(),
                'total': s.IntegerField(),
                'attempt_id': s.UUIDField(),
            }),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Not enrolled'),
            404: OpenApiResponse(description='Quiz not found'),
        },
        summary='Submit a quiz attempt',
        tags=['Quizzes'],
    )
    def post(self, request, id):
        try:
            quiz = Quiz.objects.get(id=id)
        except Quiz.DoesNotExist:
            return Response({'detail': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not is_enrolled(request.user, quiz.lesson.module.course):
            return Response({'detail': 'You must be enrolled to attempt this quiz.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = SubmitQuizSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        answers = serializer.validated_data['answers']
        total_questions = quiz.questions.count()
        correct = 0
        for answer in answers:
            question_id = answer.get('question_id')
            option_id = answer.get('option_id')
            try:
                option = Option.objects.get(id=option_id, question__id=question_id, question__quiz=quiz)
                if option.is_correct:
                    correct += 1
            except Option.DoesNotExist:
                pass
        score = int((correct / total_questions) * 100) if total_questions > 0 else 0
        passed = score >= quiz.pass_score
        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, score=score, passed=passed)
        streak = Streak.record_activity(request.user, 'quiz_attempted')
        if streak:
            ActivityFeed.objects.create(
                user=request.user,
                activity_type='streak',
                description=f'🔥 {streak.current_streak} day streak! Keep it up! 🔥'
            )
        return Response({
            'score': score,
            'passed': passed,
            'correct': correct,
            'total': total_questions,
            'attempt_id': attempt.id,
        }, status=status.HTTP_201_CREATED)


# ─── Review Views ─────────────────────────────────────────────────────

class CourseReviewListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CourseReviewSerializer(many=True), 404: OpenApiResponse(description='Course not found')},
        summary='List reviews for a course',
        tags=['Courses'],
    )
    def get(self, request, id):
        try:
            course = Course.objects.get(id=id, status='published')
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        reviews = course.reviews.all().order_by('-created_at')
        serializer = CourseReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=CourseReviewSerializer,
        responses={
            201: CourseReviewSerializer,
            400: OpenApiResponse(description='Already reviewed or validation error'),
            403: OpenApiResponse(description='Not enrolled'),
            404: OpenApiResponse(description='Course not found'),
        },
        summary='Submit a review for a course',
        tags=['Courses'],
    )
    def post(self, request, id):
        try:
            course = Course.objects.get(id=id, status='published')
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not is_enrolled(request.user, course):
            return Response({'detail': 'You must be enrolled to review this course.'}, status=status.HTTP_403_FORBIDDEN)
        if CourseReview.objects.filter(user=request.user, course=course).exists():
            return Response({'detail': 'You have already reviewed this course.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CourseReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user, course=course)
        all_ratings = CourseReview.objects.filter(course=course).values_list('rating', flat=True)
        avg = sum(all_ratings) / len(all_ratings)
        course.average_rating = round(avg, 2)
        course.save(update_fields=['average_rating'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)