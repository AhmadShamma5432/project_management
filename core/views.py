from django.shortcuts import render
from rest_framework.mixins import RetrieveModelMixin,UpdateModelMixin,ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser
from .models import User
from .serializers import UserSerializer,UserUpdateSerializer
# Create your views here.

class UserView(ListModelMixin,RetrieveModelMixin,UpdateModelMixin,GenericViewSet):
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        elif self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer

class UsersView(ListModelMixin,GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]