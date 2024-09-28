from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from core.models import AuditUserLog

User = get_user_model()

@receiver(post_save,sender=User)
def log_user(sender,instance,created,**kwargs):
    if created :
        action = f"Created User {instance.username}"
    else:
        action = f"Updated User {instance.username}"
    
    AuditUserLog.objects.create(action=action,name=instance.username,user=instance)

@receiver(pre_delete,sender=User)
def delete_user(sender,instance,**kwargs):
    action = f"The user {instance.username} has been deleted"
    AuditUserLog.objects.create(action=action,name=instance.username,user=instance)