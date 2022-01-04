from django.urls import path

from . import views

app_name = 'user'

urlpatterns = [
    path('create/', views.UserViewSet.as_view(), name='create'),
    path('token/', views.CreateAuthToken.as_view(), name='token'),
]
