from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

ROUTERS = DefaultRouter()
ROUTERS.register('tags', views.TagViewset)
ROUTERS.register('ingredient', views.IngredientViewset)
ROUTERS.register('recipe', views.RecipeViewset)

app_name = 'recipe'

urlpatterns = [
    path('', include(ROUTERS.urls))
]
