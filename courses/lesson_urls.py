from django.urls import path
from courses import views

urlpatterns = [
    path('<uuid:id>/', views.StandaloneLessonDetailView.as_view(), name='lesson-detail'),
    path('<uuid:id>/complete/', views.LessonCompleteView.as_view(), name='lesson-complete'),
    path('<uuid:id>/bookmark/', views.LessonBookmarkView.as_view(), name='lesson-bookmark'),
]