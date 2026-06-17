from django.urls import path
from .views import (
    DashboardView, EnrolledCourseListView, CourseProgressView,
    CertificateListView, BookmarkListView, StreakView, ActivityFeedListView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='learner-dashboard'),
    path('courses/', EnrolledCourseListView.as_view(), name='learner-enrolled-courses'),
    path('courses/<uuid:id>/progress/', CourseProgressView.as_view(), name='learner-course-progress'),
    path('certificates/', CertificateListView.as_view(), name='learner-certificates'),
    path('bookmarks/', BookmarkListView.as_view(), name='learner-bookmarks'),
    path('streak/', StreakView.as_view(), name='learner-streak'),
    path('activity/', ActivityFeedListView.as_view(), name='learner-activity'),
]