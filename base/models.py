from typing import Iterable
from django.db import models,transaction
from django.core.exceptions import ValidationError
from core.models import User

User_role_choiches = [
    ('BoardOwner','BoardOwner'),
    ('Admin','Admin'),
    ('Manager','Manager'),
    ('Member','Member')
]


class Board(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True,null=True)
    board_owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_board')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class List(models.Model):
    name = models.CharField(max_length=255)
    board = models.ForeignKey(Board,on_delete=models.CASCADE,related_name='lists')
    position = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def delete(self,*args,**kwargs):
        with transaction.atomic():
            lists_to_update = List.objects.filter(position__gt=self.position)
            super().delete(*args,**kwargs)
            for item in lists_to_update:
                item.position -= 1 
                item.save()


class Card(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    position = models.PositiveIntegerField()
    starts_Date = models.DateTimeField(blank=True,null=True)
    finish_Date = models.DateTimeField(blank=True,null=True)
    list = models.ForeignKey(List,on_delete=models.CASCADE,related_name='cards')

    def delete(self,*args,**kwargs):
        with transaction.atomic():
            cards_to_update = Card.objects.filter(position__gt=self.position)
            super().delete(*args,**kwargs)
            for items in cards_to_update:
                items.position -= 1 
                items.save()

class BoardMember(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='board_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='board_memberships')
    role = models.CharField(max_length=255,choices=User_role_choiches)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['board','user'],name='unique_board_members')
        ]



class CardMember(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='card_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='card_memberships')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['card','user'],name='unique_card_members')
        ]

class CardFile(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='card_files')
    file = models.FileField(upload_to='base/')

class CardComment(models.Model):
    text = models.TextField()
    card = models.ForeignKey(Card,on_delete=models.CASCADE,related_name='card_comments')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)


class Profile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_profile')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['first_name','last_name'],name='unique_first_last_name')
        ]
        

