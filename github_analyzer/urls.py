from django.urls import path
from . import views

urlpatterns = [
    path("api/", views.repo_analysis, name="analysis"),
    path("", views.index, name="index")
]