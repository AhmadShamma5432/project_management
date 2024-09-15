from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer,UserSerializer as BaseUserSerializer
from .models import User
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ['id','username','email','password']

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['id','username','email']

class UserUpdateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['id','email']

class SimpleUserSerializer(BaseUserSerializer):
    id = serializers.IntegerField()
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['id','username']