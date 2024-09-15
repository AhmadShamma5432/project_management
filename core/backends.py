from typing import Any
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from .models import User as User_model

User = get_user_model 

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self,request,username=None,password=None,**kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            if '@' in username:
                user = User_model.objects.get(email=username)
                print("Done")
            else:
                print("username")
                user = User_model.objects.get(username=username)
        except:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
        