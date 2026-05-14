from django.urls import path
from . import views

urlpatterns = [
    path('api/test/', views.test_api, name='test_api'),
    path('api/reset/', views.reset_test, name='reset_test'),
]
