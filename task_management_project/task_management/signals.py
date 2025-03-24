"""
Signal handlers for the task_management app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Task, TaskAssignment
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance, **kwargs):
    """
    Signal handler that runs before a Task is saved.
    Used to track status changes.
    """
    if instance.pk:
        try:
            old_instance = Task.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                logger.info(f"Task {instance.pk} status changed from {old_instance.status} to {instance.status}")
                
                # If the task is being marked as completed and completed_at isn't set
                if instance.status == 'completed' and not instance.completed_at:
                    instance.mark_completed()
        except Task.DoesNotExist:
            pass

@receiver(post_save, sender=TaskAssignment)
def task_assignment_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a TaskAssignment is saved.
    Used to log new assignments.
    """
    if created:
        user_name = instance.user.name or instance.user.username
        assigned_by = "unknown"
        if instance.assigned_by:
            assigned_by = instance.assigned_by.name or instance.assigned_by.username
            
        logger.info(f"Task '{instance.task.name}' assigned to {user_name} by {assigned_by}")