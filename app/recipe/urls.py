from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

ROUTERS = DefaultRouter()
ROUTERS.register('tags', views.TagViewset)

app_name = 'receipe'

urlpatterns = [
    path('', include(ROUTERS.urls))
]
