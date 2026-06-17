from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:id>/questions/', views.QuizQuestionsView.as_view(), name='quiz-questions'),
    path('<uuid:id>/attempts/', views.QuizAttemptsView.as_view(), name='quiz-attempts'),
    path('<uuid:id>/attempts/<uuid:attempt_id>/', views.QuizAttemptDetailView.as_view(), name='quiz-attempt-detail'),
    path('<uuid:id>/attempt/', views.SubmitQuizView.as_view(), name='quiz-submit'),
]