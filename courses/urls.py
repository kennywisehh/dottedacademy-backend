from django.urls import path
from . import views

urlpatterns = [
    # Course listing
    path('', views.CourseListView.as_view(), name='course-list'),
    path('university/', views.UniversityCourseListView.as_view(), name='university-courses'),
    path('skills/', views.SkillsCourseListView.as_view(), name='skills-courses'),
    path('search/', views.CourseSearchView.as_view(), name='course-search'),
    path('featured/', views.FeaturedCourseListView.as_view(), name='featured-courses'),
    path('popular/', views.PopularCourseListView.as_view(), name='popular-courses'),

    # Course detail & enrollment
    path('<uuid:id>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('<uuid:id>/enrollment-status/', views.CourseEnrollmentStatusView.as_view(), name='enrollment-status'),
    path('<uuid:id>/enrolled-count/', views.CourseEnrolledCountView.as_view(), name='enrolled-count'),
    path('<uuid:id>/enroll/', views.EnrollView.as_view(), name='enroll'),

    # Reviews
    path('<uuid:id>/reviews/', views.CourseReviewListView.as_view(), name='course-reviews'),

    # Modules
    path('<uuid:id>/modules/', views.ModuleListView.as_view(), name='module-list'),
    path('<uuid:id>/modules/<uuid:module_id>/', views.ModuleDetailView.as_view(), name='module-detail'),

    # Lessons under modules
    path('<uuid:id>/modules/<uuid:module_id>/lessons/', views.LessonListView.as_view(), name='lesson-list'),
    path('<uuid:id>/modules/<uuid:module_id>/lessons/<uuid:lesson_id>/', views.LessonDetailView.as_view(), name='lesson-detail'),
]

# Standalone lesson & quiz URLs (registered separately in core/urls.py)
# path('lessons/<uuid:id>/', ...)
# path('lessons/<uuid:id>/complete/', ...)
# path('lessons/<uuid:id>/bookmark/', ...)
# path('quizzes/<uuid:id>/questions/', ...)
# path('quizzes/<uuid:id>/attempts/', ...)
# path('quizzes/<uuid:id>/attempts/<uuid:attempt_id>/', ...)
# path('quizzes/<uuid:id>/attempt/', ...)