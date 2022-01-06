from core.models import Tag, Ingredient, Recipe
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredient.objects.all())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'ingredient', 'tags', 'link']
        read_only_fields = ['id', 'price']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer the recipe detail"""
    ingredient = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
