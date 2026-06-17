from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.exceptions import NotFound
from .models import Industry, Category
from .serializers import (
    IndustrySerializer,
    IndustryWithCategoriesSerializer,
    CategorySerializer,
)


# --- Industry Views ---

class IndustryListView(generics.ListAPIView):
    """GET /api/skills/industries/"""
    serializer_class = IndustrySerializer

    def get_queryset(self):
        return Industry.objects.filter(is_active=True)


class IndustrySearchView(generics.ListAPIView):
    """GET /api/skills/industries/search/?q={query}"""
    serializer_class = IndustrySerializer

    def get_queryset(self):
        q = self.request.query_params.get('q', '').strip()
        if not q:
            return Industry.objects.filter(is_active=True)
        return Industry.objects.filter(is_active=True, name__icontains=q)


class IndustryDetailView(generics.RetrieveAPIView):
    """GET /api/skills/industries/{id}/"""
    serializer_class = IndustryWithCategoriesSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Industry.objects.filter(is_active=True)


class IndustryCategoryListView(generics.ListAPIView):
    """GET /api/skills/industries/{id}/categories/"""
    serializer_class = CategorySerializer

    def get_queryset(self):
        industry_id = self.kwargs['id']
        if not Industry.objects.filter(id=industry_id, is_active=True).exists():
            raise NotFound('Industry not found.')
        return Category.objects.filter(industry_id=industry_id, is_active=True)


class IndustryCategoryDetailView(generics.RetrieveAPIView):
    """GET /api/skills/industries/{id}/categories/{category_id}/"""
    serializer_class = CategorySerializer

    def get_object(self):
        industry_id = self.kwargs['id']
        category_id = self.kwargs['category_id']
        if not Industry.objects.filter(id=industry_id, is_active=True).exists():
            raise NotFound('Industry not found.')
        try:
            return Category.objects.get(id=category_id, industry_id=industry_id, is_active=True)
        except Category.DoesNotExist:
            raise NotFound('Category not found.')


# --- Category Views ---

class CategoryListView(generics.ListAPIView):
    """GET /api/skills/categories/"""
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class CategorySearchView(generics.ListAPIView):
    """GET /api/skills/categories/search/?q={query}"""
    serializer_class = CategorySerializer

    def get_queryset(self):
        q = self.request.query_params.get('q', '').strip()
        if not q:
            return Category.objects.filter(is_active=True)
        return Category.objects.filter(is_active=True, name__icontains=q)


class CategoryDetailView(generics.RetrieveAPIView):
    """GET /api/skills/categories/{id}/"""
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)