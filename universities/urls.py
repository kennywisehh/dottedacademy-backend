from django.urls import path
from . import views

urlpatterns = [
    # University
    path('', views.UniversityListView.as_view(), name='university-list'),
    path('search/', views.UniversitySearchView.as_view(), name='university-search'),
    path('<uuid:id>/', views.UniversityDetailView.as_view(), name='university-detail'),

    # Faculties
    path('<uuid:id>/faculties/', views.FacultyListView.as_view(), name='faculty-list'),
    path('<uuid:id>/faculties/<uuid:faculty_id>/', views.FacultyDetailView.as_view(), name='faculty-detail'),

    # Departments
    path('<uuid:id>/faculties/<uuid:faculty_id>/departments/', views.DepartmentListView.as_view(), name='department-list'),
    path('<uuid:id>/faculties/<uuid:faculty_id>/departments/<uuid:department_id>/', views.DepartmentDetailView.as_view(), name='department-detail'),
]