from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from courses.models import (
    Enrollment, LessonProgress, QuizAttempt, Certificate, Bookmark, Lesson
)
from .models import Streak, ActivityFeed, Notification
from .serializers import (
    EnrolledCourseSerializer, CertificateSerializer,
    BookmarkSerializer, StreakSerializer, ActivityFeedSerializer,
    NotificationSerializer,
)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        enrollments = Enrollment.objects.filter(user=user)
        enrolled_count = enrollments.count()
        completed_count = enrollments.filter(is_completed=True).count()
        in_progress_count = enrolled_count - completed_count

        completed_lessons_qs = LessonProgress.objects.filter(user=user, is_completed=True)
        completed_lessons_count = completed_lessons_qs.count()
        hours_spent = sum(
            (lp.lesson.duration_minutes for lp in completed_lessons_qs.select_related('lesson')),
            0
        ) / 60

        total_lessons_in_enrolled_courses = Lesson.objects.filter(
            module__course__in=enrollments.values_list('course', flat=True)
        ).count()

        overall_progress = (
            round((completed_lessons_count / total_lessons_in_enrolled_courses) * 100)
            if total_lessons_in_enrolled_courses > 0 else 0
        )

        quiz_attempts = QuizAttempt.objects.filter(user=user)
        quizzes_attempted = quiz_attempts.count()
        quizzes_passed = quiz_attempts.filter(passed=True).count()

        streak, _ = Streak.objects.get_or_create(user=user)

        return Response({
            'enrolled_courses': enrolled_count,
            'completed_courses': completed_count,
            'in_progress_courses': in_progress_count,
            'overall_progress_percent': overall_progress,
            'hours_spent': round(hours_spent, 1),
            'quizzes_attempted': quizzes_attempted,
            'quizzes_passed': quizzes_passed,
            'streak': StreakSerializer(streak).data,
        })


class EnrolledCourseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
        serializer = EnrolledCourseSerializer(enrollments, many=True, context={'request': request})
        return Response(serializer.data)


class CourseProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            enrollment = Enrollment.objects.get(user=request.user, course__id=id)
        except Enrollment.DoesNotExist:
            return Response({'detail': 'You are not enrolled in this course.'}, status=status.HTTP_404_NOT_FOUND)

        course = enrollment.course
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = LessonProgress.objects.filter(
            user=request.user, lesson__module__course=course, is_completed=True
        ).count()

        progress_percent = round((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

        return Response({
            'course_id': course.id,
            'course_title': course.title,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percent': progress_percent,
            'is_completed': enrollment.is_completed,
        })


class CertificateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        certificates = Certificate.objects.filter(user=request.user).select_related('course')
        serializer = CertificateSerializer(certificates, many=True)
        return Response(serializer.data)


class BookmarkListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookmarks = Bookmark.objects.filter(user=request.user).select_related('lesson__module__course')
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)


class StreakView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        streak, _ = Streak.objects.get_or_create(user=request.user)
        serializer = StreakSerializer(streak)
        return Response(serializer.data)


class ActivityFeedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = ActivityFeed.objects.filter(user=request.user)[:50]
        serializer = ActivityFeedSerializer(activities, many=True)
        return Response(serializer.data)

class BookmarkToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, lesson=lesson)
        if not created:
            return Response({'detail': 'Already bookmarked.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Bookmark added.'}, status=status.HTTP_201_CREATED)

    def delete(self, request, lesson_id):
        try:
            bookmark = Bookmark.objects.get(user=request.user, lesson__id=lesson_id)
        except Bookmark.DoesNotExist:
            return Response({'detail': 'Bookmark not found.'}, status=status.HTTP_404_NOT_FOUND)
        bookmark.delete()
        return Response({'detail': 'Bookmark removed.'}, status=status.HTTP_204_NO_CONTENT)


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            notification = Notification.objects.get(id=id, user=request.user)
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'detail': 'Notification marked as read.'})