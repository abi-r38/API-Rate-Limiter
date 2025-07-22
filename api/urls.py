from django.urls import path
from . import views

urlpatterns = [
    path('resource/', views.get_resource, name='api_resource'),
    path('', views.serve_home, name='home'),
]