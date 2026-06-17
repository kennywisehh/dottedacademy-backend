from rest_framework import serializers
from .models import University, Faculty, Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'is_active']


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'is_active']


class FacultyWithDepartmentsSerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(many=True, read_only=True)

    class Meta:
        model = Faculty
        fields = ['id', 'name', 'is_active', 'departments']


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'abbreviation', 'logo', 'is_active']


class UniversityDetailSerializer(serializers.ModelSerializer):
    faculties = FacultySerializer(many=True, read_only=True)

    class Meta:
        model = University
        fields = ['id', 'name', 'abbreviation', 'logo', 'is_active', 'faculties']