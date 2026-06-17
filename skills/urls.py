from django.urls import path
from . import views

urlpatterns = [
    # Industries
    path('industries/', views.IndustryListView.as_view(), name='industry-list'),
    path('industries/search/', views.IndustrySearchView.as_view(), name='industry-search'),
    path('industries/<uuid:id>/', views.IndustryDetailView.as_view(), name='industry-detail'),
    path('industries/<uuid:id>/categories/', views.IndustryCategoryListView.as_view(), name='industry-category-list'),
    path('industries/<uuid:id>/categories/<uuid:category_id>/', views.IndustryCategoryDetailView.as_view(), name='industry-category-detail'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/search/', views.CategorySearchView.as_view(), name='category-search'),
    path('categories/<uuid:id>/', views.CategoryDetailView.as_view(), name='category-detail'),
]