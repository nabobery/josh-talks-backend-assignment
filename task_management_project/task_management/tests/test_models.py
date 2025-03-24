"""
Tests for the models in the task_management app.
"""
from django.test import TestCase
from django.utils import timezone
from django.db.utils import IntegrityError
from django.db import transaction
from ..models import User, Task, TaskType, TaskAssignment

class UserModelTests(TestCase):
    """Test cases for the User model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            name='Test User',
            mobile='1234567890'
        )
    
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.name, 'Test User')
        self.assertEqual(self.user.mobile, '1234567890')
    
    def test_user_str_method(self):
        """Test the __str__ method of the User model."""
        self.assertEqual(str(self.user), 'test@example.com')
        
        # Test with no email
        self.user.email = ''
        self.user.save()
        self.assertEqual(str(self.user), 'testuser')

class TaskTypeModelTests(TestCase):
    """Test cases for the TaskType model."""
    
    def setUp(self):
        """Set up test data."""
        self.task_type = TaskType.objects.create(
            name='Bug',
            description='A software bug that needs fixing'
        )
    
    def test_task_type_creation(self):
        """Test task type creation."""
        self.assertEqual(self.task_type.name, 'Bug')
        self.assertEqual(self.task_type.description, 'A software bug that needs fixing')
    
    def test_task_type_str_method(self):
        """Test the __str__ method of the TaskType model."""
        self.assertEqual(str(self.task_type), 'Bug')
    
    def test_task_type_unique_name(self):
        """Test that task type names must be unique."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TaskType.objects.create(name='Bug')

class TaskModelTests(TestCase):
    """Test cases for the Task model."""
    
    def setUp(self):
        """Set up test data."""
        self.task_type = TaskType.objects.create(name='Feature')
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        
        self.task = Task.objects.create(
            name='Implement API',
            description='Create RESTful API endpoints',
            task_type=self.task_type,
            status='pending'
        )
    
    def test_task_creation(self):
        """Test task creation."""
        self.assertEqual(self.task.name, 'Implement API')
        self.assertEqual(self.task.description, 'Create RESTful API endpoints')
        self.assertEqual(self.task.task_type, self.task_type)
        self.assertEqual(self.task.status, 'pending')
        self.assertIsNone(self.task.completed_at)
    
    def test_task_str_method(self):
        """Test the __str__ method of the Task model."""
        self.assertEqual(str(self.task), 'Implement API')
    
    def test_mark_completed(self):
        """Test marking a task as completed."""
        self.task.mark_completed()
        self.assertEqual(self.task.status, 'completed')
        self.assertIsNotNone(self.task.completed_at)
        
        # Make sure the task has been saved
        refreshed_task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(refreshed_task.status, 'completed')
        self.assertIsNotNone(refreshed_task.completed_at)
    
    def test_assign_to_users(self):
        """Test assigning a task to users."""
        # Assign to two users
        assignments = self.task.assign_to_users([self.user1.id, self.user2.id], self.user1)
        
        self.assertEqual(len(assignments), 2)
        self.assertEqual(self.task.assignees.count(), 2)
        self.assertTrue(self.user1 in self.task.assignees.all())
        self.assertTrue(self.user2 in self.task.assignees.all())
        
        # Verify the assignment details
        assignment1 = TaskAssignment.objects.get(task=self.task, user=self.user1)
        self.assertEqual(assignment1.assigned_by, self.user1)
        
        # Test idempotence - assigning again doesn't create duplicates
        assignments = self.task.assign_to_users([self.user1.id], self.user2)
        self.assertEqual(len(assignments), 1)
        self.assertEqual(self.task.assignees.count(), 2)
        
        # But the assigned_by field doesn't change for existing assignments
        assignment1.refresh_from_db()
        self.assertEqual(assignment1.assigned_by, self.user1)

class TaskAssignmentModelTests(TestCase):
    """Test cases for the TaskAssignment model."""
    
    def setUp(self):
        """Set up test data."""
        self.task = Task.objects.create(name='Test Task')
        self.user = User.objects.create_user(username='assignee', password='password')
        self.assigner = User.objects.create_user(username='assigner', password='password')
        
        self.assignment = TaskAssignment.objects.create(
            task=self.task,
            user=self.user,
            assigned_by=self.assigner
        )
    
    def test_task_assignment_creation(self):
        """Test task assignment creation."""
        self.assertEqual(self.assignment.task, self.task)
        self.assertEqual(self.assignment.user, self.user)
        self.assertEqual(self.assignment.assigned_by, self.assigner)
        self.assertIsNotNone(self.assignment.assigned_at)
    
    def test_task_assignment_str_method(self):
        """Test the __str__ method of the TaskAssignment model."""
        expected = f"Test Task assigned to assignee"
        self.assertEqual(str(self.assignment), expected)
    
    def test_unique_together_constraint(self):
        """Test that a user can only be assigned to a task once."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TaskAssignment.objects.create(
                    task=self.task,
                    user=self.user,
                    assigned_by=self.assigner
                )