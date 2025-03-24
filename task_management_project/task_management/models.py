"""
Models for the task management application.
Defines User, Task, TaskType, and TaskAssignment models.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class User(AbstractUser):
    """
    Custom User model with additional fields for name and mobile number.
    Extends Django's AbstractUser model.
    """
    name = models.CharField(max_length=255, blank=True, help_text="Full name of the user")
    mobile = models.CharField(max_length=15, blank=True, help_text="Mobile number of the user")
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["username"]
    
    def __str__(self):
        """String representation of the User model."""
        return self.email or self.username
    
    def get_assigned_tasks(self):
        """Get all tasks assigned to this user."""
        return self.assigned_tasks.all()
    
    def get_active_tasks(self):
        """Get all active (non-completed) tasks assigned to this user."""
        return self.assigned_tasks.exclude(status='completed')

class TaskType(models.Model):
    """
    Task type model for categorizing tasks.
    Examples: Bug, Feature, Documentation, etc.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the task type")
    description = models.TextField(blank=True, help_text="Description of the task type")
    
    class Meta:
        verbose_name = "Task Type"
        verbose_name_plural = "Task Types"
        ordering = ["name"]
    
    def __str__(self):
        """String representation of the TaskType model."""
        return self.name

class Task(models.Model):
    """
    Task model to store task information.
    A task can be assigned to multiple users through the TaskAssignment model.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    name = models.CharField(max_length=255, help_text="Name of the task")
    description = models.TextField(blank=True, help_text="Detailed description of the task")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the task was created")
    task_type = models.ForeignKey(
        TaskType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tasks',
        help_text="Type of the task"
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the task was marked as completed"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Current status of the task"
    )
    assignees = models.ManyToManyField(
        User,
        related_name='assigned_tasks',
        through='TaskAssignment',
        through_fields=('task', 'user'),
        help_text="Users assigned to this task"
    )
    
    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-created_at"]
    
    def __str__(self):
        """String representation of the Task model."""
        return self.name
    
    def mark_completed(self):
        """Mark the task as completed and set completed_at timestamp."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        logger.info(f"Task {self.id} marked as completed")
        return self
    
    def assign_to_users(self, user_ids, assigned_by=None):
        """
        Assign this task to the specified users.
        
        Args:
            user_ids: List of user IDs to assign the task to
            assigned_by: User who is making the assignment (optional)
            
        Returns:
            List of TaskAssignment objects created
        """
        assignments = []
        for user_id in user_ids:
            assignment, created = TaskAssignment.objects.get_or_create(
                task=self,
                user_id=user_id,
                defaults={'assigned_by': assigned_by}
            )
            assignments.append(assignment)
        
        logger.info(f"Task {self.id} assigned to users: {user_ids}")
        return assignments

class TaskAssignment(models.Model):
    """
    Through model to store additional information about task assignments.
    This allows us to track when a task was assigned to a user and by whom.
    """
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE,
        help_text="The task being assigned"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="The user the task is assigned to"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the task was assigned"
    )
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='task_assignments',
        help_text="User who made the assignment"
    )
    
    class Meta:
        verbose_name = "Task Assignment"
        verbose_name_plural = "Task Assignments"
        unique_together = ('task', 'user')
        ordering = ["-assigned_at"]
    
    def __str__(self):
        """String representation of the TaskAssignment model."""
        user_name = self.user.name or self.user.username
        return f"{self.task.name} assigned to {user_name}"