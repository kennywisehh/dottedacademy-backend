#from django.contrib import admin
#from django.urls import path, include

#urlpatterns = [
#    path('admin/', admin.site.urls),
#    path('api/auth/', include('accounts.urls')),
#    path('api/user/', include('accounts.user_urls')),
#    path('api/onboarding/', include('onboarding.urls')),
#    path('api/universities/', include('universities.urls')),
#    path('api/skills/', include('skills.urls')),
#    path('api/courses/', include('courses.urls')),
#    path('api/lessons/', include('courses.lesson_urls')),
#    path('api/quizzes/', include('courses.quiz_urls')),
#    path('api/subscriptions/', include('subscriptions.urls')),
#    path('api/payments/', include('payments.urls')),
#    path('api/learner/', include('learner.urls')),
#    path('api/instructor/', include('instructor.urls')),
#    path('api/admin/', include('accounts.admin_urls')),
#]

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/onboarding/', include('onboarding.urls')),
    path('api/universities/', include('universities.urls')),
    path('api/skills/', include('skills.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/lessons/', include('courses.lesson_urls')),
    path('api/quizzes/', include('courses.quiz_urls')),
    path('api/learner/', include('learner.urls')),
]