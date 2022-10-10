from datetime import datetime
from django.urls import path
from django.contrib import admin
from app import forms, views


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
]
