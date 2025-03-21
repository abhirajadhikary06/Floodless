from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_docs, name='api_docs'),
    path('download/', views.download_dataset, name='download_dataset'),
]