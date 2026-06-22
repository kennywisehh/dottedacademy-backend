from django.urls import path
from .views import (
    AdminDashboardView,
    AdminUserListView, AdminUserDetailView,
    AdminUniversityListView, AdminUniversityDetailView,
    AdminFacultyListView, AdminFacultyDetailView,
    AdminDepartmentListView, AdminDepartmentDetailView,
    AdminIndustryListView, AdminIndustryDetailView,
    AdminCategoryListView, AdminCategoryDetailView,
    AdminCourseListView, AdminCourseDetailView,
    AdminModuleListView, AdminModuleDetailView,
    AdminLessonListView, AdminLessonDetailView,
    AdminQuizView, AdminQuestionListView, AdminQuestionDetailView,
    AdminOptionListView, AdminOptionDetailView,
    AdminReviewListView, AdminReviewDetailView,
    AdminRevenueSummaryView,
)

urlpatterns = [
    # Dashboard
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),

    # Users
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<uuid:id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),

    # Universities
    path('universities/', AdminUniversityListView.as_view(), name='admin-university-list'),
    path('universities/<uuid:id>/', AdminUniversityDetailView.as_view(), name='admin-university-detail'),
    path('universities/<uuid:university_id>/faculties/', AdminFacultyListView.as_view(), name='admin-faculty-list'),
    path('universities/<uuid:university_id>/faculties/<uuid:faculty_id>/', AdminFacultyDetailView.as_view(), name='admin-faculty-detail'),
    path('universities/<uuid:university_id>/faculties/<uuid:faculty_id>/departments/', AdminDepartmentListView.as_view(), name='admin-department-list'),
    path('universities/<uuid:university_id>/faculties/<uuid:faculty_id>/departments/<uuid:department_id>/', AdminDepartmentDetailView.as_view(), name='admin-department-detail'),

    # Skills
    path('industries/', AdminIndustryListView.as_view(), name='admin-industry-list'),
    path('industries/<uuid:id>/', AdminIndustryDetailView.as_view(), name='admin-industry-detail'),
    path('industries/<uuid:industry_id>/categories/', AdminCategoryListView.as_view(), name='admin-category-list'),
    path('industries/<uuid:industry_id>/categories/<uuid:category_id>/', AdminCategoryDetailView.as_view(), name='admin-category-detail'),

    # Courses
    path('courses/', AdminCourseListView.as_view(), name='admin-course-list'),
    path('courses/<uuid:id>/', AdminCourseDetailView.as_view(), name='admin-course-detail'),
    path('courses/<uuid:course_id>/modules/', AdminModuleListView.as_view(), name='admin-module-list'),
    path('courses/<uuid:course_id>/modules/<uuid:module_id>/', AdminModuleDetailView.as_view(), name='admin-module-detail'),
    path('courses/<uuid:course_id>/modules/<uuid:module_id>/lessons/', AdminLessonListView.as_view(), name='admin-lesson-list'),
    path('courses/<uuid:course_id>/modules/<uuid:module_id>/lessons/<uuid:lesson_id>/', AdminLessonDetailView.as_view(), name='admin-lesson-detail'),

    # Quizzes
    path('lessons/<uuid:lesson_id>/quiz/', AdminQuizView.as_view(), name='admin-quiz'),
    path('lessons/<uuid:lesson_id>/quiz/questions/', AdminQuestionListView.as_view(), name='admin-question-list'),
    path('lessons/<uuid:lesson_id>/quiz/questions/<uuid:question_id>/', AdminQuestionDetailView.as_view(), name='admin-question-detail'),
    path('lessons/<uuid:lesson_id>/quiz/questions/<uuid:question_id>/options/', AdminOptionListView.as_view(), name='admin-option-list'),
    path('lessons/<uuid:lesson_id>/quiz/questions/<uuid:question_id>/options/<uuid:option_id>/', AdminOptionDetailView.as_view(), name='admin-option-detail'),

    # Reviews
    path('reviews/', AdminReviewListView.as_view(), name='admin-review-list'),
    path('reviews/<uuid:id>/', AdminReviewDetailView.as_view(), name='admin-review-detail'),

    # Revenue
    path('revenue/summary/', AdminRevenueSummaryView.as_view(), name='admin-revenue-summary'),
]