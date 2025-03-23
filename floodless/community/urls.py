# community/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('report/', views.emergency_report, name='emergency_report'),
    path('report-list/', views.report_list, name='report_list'),
    path('authority/', views.authority_dashboard, name='authority_dashboard'),
    path('disaster/<int:report_id>/', views.disaster_chat, name='disaster_chat'),
    path('disaster/<int:report_id>/send/', views.send_message, name='disaster_chat_send'),
]