"""
Application configuration for the task_management app.
"""
from django.apps import AppConfig


class TaskManagementConfig(AppConfig):
    """Configuration for the task_management app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_management_project.task_management'
    
    def ready(self):
        """
        Initialize app when ready.
        Import signals module to register signal handlers.
        """
        import task_management_project.task_management.signals  # noqa