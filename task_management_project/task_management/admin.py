"""
Admin configuration for the task_management app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Task, TaskType, TaskAssignment

class CustomUserAdmin(UserAdmin):
    """Custom admin for User model"""
    list_display = ('username', 'email', 'name', 'mobile', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('name', 'mobile')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('name', 'mobile')}),
    )
    search_fields = ('username', 'email', 'name', 'mobile')

class TaskAssignmentInline(admin.TabularInline):
    """Inline admin for TaskAssignment model"""
    model = TaskAssignment
    extra = 1
    raw_id_fields = ('user', 'assigned_by')

class TaskAdmin(admin.ModelAdmin):
    """Admin for Task model"""
    list_display = ('id', 'name', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'task_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'completed_at')
    inlines = [TaskAssignmentInline]
    
    def get_queryset(self, request):
        """Optimize query by prefetching related objects"""
        return super().get_queryset(request).prefetch_related('assignees')

class TaskTypeAdmin(admin.ModelAdmin):
    """Admin for TaskType model"""
    list_display = ('id', 'name', 'description')
    search_fields = ('name', 'description')

class TaskAssignmentAdmin(admin.ModelAdmin):
    """Admin for TaskAssignment model"""
    list_display = ('id', 'task', 'user', 'assigned_at', 'assigned_by')
    list_filter = ('assigned_at',)
    search_fields = ('task__name', 'user__username', 'user__email')
    raw_id_fields = ('task', 'user', 'assigned_by')

# Register models with the admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskType, TaskTypeAdmin)
admin.site.register(TaskAssignment, TaskAssignmentAdmin)