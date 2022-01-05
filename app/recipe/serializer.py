from core.models import Tag
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'user')
        read_only_fields = ['id']
        extra_kwargs = {'user': {'required': False}}
