#  rate_limiter_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This line tells Django to look at api/urls.py for any URL
    # that starts with 'api/'.
    path('api/', include('api.urls')),

    # This is the MOST IMPORTANT line for fixing your current issue.
    # It tells Django to also look at api/urls.py for the main
    # homepage URL (the empty path '').
    path('', include('api.urls')),
]