from django.contrib import admin
from .models import User,AuditUserLog

admin.site.register(User)

@admin.register(AuditUserLog)
class AdminAuditUserLog(admin.ModelAdmin):
    list_display = ['name','action','timestamp']
    search_fields = ['name','action']
    list_filter = ['timestamp']