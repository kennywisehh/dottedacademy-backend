from rest_framework import generics
from rest_framework.exceptions import NotFound
from .models import University, Faculty, Department
from .serializers import (
    UniversitySerializer,
    UniversityDetailSerializer,
    FacultySerializer,
    FacultyWithDepartmentsSerializer,
    DepartmentSerializer,
)


class UniversityListView(generics.ListAPIView):
    """GET /api/universities/ — list all active universities"""
    serializer_class = UniversitySerializer

    def get_queryset(self):
        return University.objects.filter(is_active=True)


class UniversitySearchView(generics.ListAPIView):
    """GET /api/universities/search/?q={query}"""
    serializer_class = UniversitySerializer

    def get_queryset(self):
        q = self.request.query_params.get('q', '').strip()
        if not q:
            return University.objects.filter(is_active=True)
        return University.objects.filter(is_active=True, name__icontains=q)


class UniversityDetailView(generics.RetrieveAPIView):
    """GET /api/universities/{id}/"""
    serializer_class = UniversityDetailSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return University.objects.filter(is_active=True)


class FacultyListView(generics.ListAPIView):
    """GET /api/universities/{id}/faculties/"""
    serializer_class = FacultySerializer

    def get_queryset(self):
        university_id = self.kwargs['id']
        if not University.objects.filter(id=university_id, is_active=True).exists():
            raise NotFound('University not found.')
        return Faculty.objects.filter(university_id=university_id, is_active=True)


class FacultyDetailView(generics.RetrieveAPIView):
    """GET /api/universities/{id}/faculties/{faculty_id}/"""
    serializer_class = FacultyWithDepartmentsSerializer

    def get_object(self):
        university_id = self.kwargs['id']
        faculty_id = self.kwargs['faculty_id']
        if not University.objects.filter(id=university_id, is_active=True).exists():
            raise NotFound('University not found.')
        try:
            return Faculty.objects.get(id=faculty_id, university_id=university_id, is_active=True)
        except Faculty.DoesNotExist:
            raise NotFound('Faculty not found.')


class DepartmentListView(generics.ListAPIView):
    """GET /api/universities/{id}/faculties/{faculty_id}/departments/"""
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        university_id = self.kwargs['id']
        faculty_id = self.kwargs['faculty_id']
        if not University.objects.filter(id=university_id, is_active=True).exists():
            raise NotFound('University not found.')
        if not Faculty.objects.filter(id=faculty_id, university_id=university_id, is_active=True).exists():
            raise NotFound('Faculty not found.')
        return Department.objects.filter(faculty_id=faculty_id, is_active=True)


class DepartmentDetailView(generics.RetrieveAPIView):
    """GET /api/universities/{id}/faculties/{faculty_id}/departments/{department_id}/"""
    serializer_class = DepartmentSerializer

    def get_object(self):
        university_id = self.kwargs['id']
        faculty_id = self.kwargs['faculty_id']
        department_id = self.kwargs['department_id']
        if not University.objects.filter(id=university_id, is_active=True).exists():
            raise NotFound('University not found.')
        if not Faculty.objects.filter(id=faculty_id, university_id=university_id, is_active=True).exists():
            raise NotFound('Faculty not found.')
        try:
            return Department.objects.get(id=department_id, faculty_id=faculty_id, is_active=True)
        except Department.DoesNotExist:
            raise NotFound('Department not found.')