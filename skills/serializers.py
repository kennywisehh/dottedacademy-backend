from rest_framework import serializers
from .models import Industry, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'is_active']


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'name', 'icon', 'is_active']


class IndustryWithCategoriesSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Industry
        fields = ['id', 'name', 'icon', 'is_active', 'categories']