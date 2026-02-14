from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailAPIView


urlpatterns = [    path('send-email/', EmailAPIView.as_view(), name='send-email'),
]