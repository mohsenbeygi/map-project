from django.urls import path, include
from . import views

urlpatterns = [
    path('<data>/', views.display_path, name='path'),
    path('', views.index, name='index'),
]
