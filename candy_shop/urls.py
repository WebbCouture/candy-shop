from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main app routes (includes /accounts/ for your combined account page)
    path('', include('main.urls')),

    # Built-in Django auth routes (password reset, change, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
]
