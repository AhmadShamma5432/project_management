from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Board,BoardMember

@receiver(post_save,sender=Board)
def create_board_member(sender,instance,created,**kwargs):
    if created:
        BoardMember.objects.create(board=instance,user=instance.board_owner,role='BoardOwner')