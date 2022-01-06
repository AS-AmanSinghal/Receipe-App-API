from core.models import Tag, Ingredient, Recipe
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializer import TagSerializer, IngredientSerializer, RecipeSerializer, RecipeDetailSerializer


# Create your views here.

class BaseRecipe(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return objects for current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new Tag"""
        serializer.save(user=self.request.user)


class TagViewset(BaseRecipe):
    """Manage tags in the database"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewset(BaseRecipe):
    """Manage ingredient in the database"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        else:
            return self.serializer_class
