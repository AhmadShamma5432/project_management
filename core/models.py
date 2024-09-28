from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

ROLE_CHOICES = [
        ('Admin','Admin'),
        ('Member', 'Member'),
    ]

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=100,choices=ROLE_CHOICES,default='Member')

    def save(self,*args,**kwargs):
        if self.is_superuser or self.is_staff:
            self.role = 'Admin'
        else:
            self.role = 'Member'

        super().save(*args,**kwargs)



class AuditUserLog(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='user_log',null=True)
    name = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self) :
        return f"{self.action} at {self.timestamp}"