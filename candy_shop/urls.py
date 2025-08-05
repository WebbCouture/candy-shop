"""
URL configuration for candy_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include  # include is used to include other URLconfs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),  # Includes your main app's URLs at the root
    path('accounts/', include('django.contrib.auth.urls')),  # Enables Django's built-in auth URLs (login, logout, password management)
]
