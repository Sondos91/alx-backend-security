from django.contrib import admin
from .models import RequestLog, BlockedIP, SuspiciousIP


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    """
    Admin interface for RequestLog model.
    """
    list_display = ('ip_address', 'country', 'city', 'path', 'timestamp')
    list_filter = ('timestamp', 'country', 'city', 'ip_address')
    search_fields = ('ip_address', 'path', 'country', 'city')
    readonly_fields = ('ip_address', 'path', 'timestamp', 'country', 'city')
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request):
        """Prevent manual addition of request logs through admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of request logs through admin."""
        return False


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    """
    Admin interface for BlockedIP model.
    """
    list_display = ('ip_address', 'reason', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('ip_address', 'reason')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('IP Information', {
            'fields': ('ip_address', 'is_active')
        }),
        ('Details', {
            'fields': ('reason', 'created_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make created_at readonly for existing objects."""
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_at',)
        return self.readonly_fields


@admin.register(SuspiciousIP)
class SuspiciousIPAdmin(admin.ModelAdmin):
    """
    Admin interface for SuspiciousIP model.
    """
    list_display = ('ip_address', 'reason', 'request_count', 'is_active', 'detected_at')
    list_filter = ('is_active', 'detected_at')
    search_fields = ('ip_address', 'reason')
    readonly_fields = ('detected_at',)
    ordering = ('-detected_at',)
    
    fieldsets = (
        ('IP Information', {
            'fields': ('ip_address', 'is_active')
        }),
        ('Detection Details', {
            'fields': ('reason', 'request_count', 'detected_at')
        }),
        ('Sensitive Paths', {
            'fields': ('sensitive_paths',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make detected_at readonly for existing objects."""
        if obj:  # editing an existing object
            return self.readonly_fields + ('detected_at',)
        return self.readonly_fields
