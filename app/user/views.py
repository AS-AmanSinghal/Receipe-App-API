from django.shortcuts import render
from rest_framework import generics
from .serializers import UserSerializer
from django.contrib.auth import get_user_model


# Create your views here.

class UserViewSet(generics.CreateAPIView):
    """Create new user in a system"""
    serializer_class = UserSerializer
