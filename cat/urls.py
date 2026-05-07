from django.urls import path
from . import views

urlpatterns = [
    path("student/<int:student_id>/", views.student),
    path("all/", views.all_students),
]
