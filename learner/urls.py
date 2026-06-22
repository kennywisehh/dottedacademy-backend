from django.urls import path
from .views import (
    DashboardView, EnrolledCourseListView, CourseProgressView,
    CertificateListView, BookmarkListView, StreakView, ActivityFeedListView,
    BookmarkToggleView, NotificationListView, NotificationReadView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='learner-dashboard'),
    path('courses/', EnrolledCourseListView.as_view(), name='learner-enrolled-courses'),
    path('courses/<uuid:id>/progress/', CourseProgressView.as_view(), name='learner-course-progress'),
    path('certificates/', CertificateListView.as_view(), name='learner-certificates'),
    path('bookmarks/', BookmarkListView.as_view(), name='learner-bookmarks'),
    path('bookmarks/<uuid:lesson_id>/', BookmarkToggleView.as_view(), name='learner-bookmark-toggle'),
    path('streak/', StreakView.as_view(), name='learner-streak'),
    path('activity/', ActivityFeedListView.as_view(), name='learner-activity'),
    path('notifications/', NotificationListView.as_view(), name='learner-notifications'),
    path('notifications/<uuid:id>/read/', NotificationReadView.as_view(), name='learner-notification-read'),
]