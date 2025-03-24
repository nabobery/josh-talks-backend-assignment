"""
Tests for the serializers of the task_management app.
"""
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from ..models import User, Task, TaskType, TaskAssignment
from ..serializers import (
    UserSerializer, TaskSerializer, TaskTypeSerializer,
    TaskCreateSerializer, TaskUpdateSerializer, TaskAssignmentCreateSerializer
)

class UserSerializerTest(TestCase):
    """Tests for the UserSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'name': 'Test User',
            'mobile': '1234567890'
        }
        self.user = User.objects.create_user(**self.user_data, password='password123')
        self.serializer = UserSerializer(instance=self.user)
    
    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'username', 'email', 'name', 'mobile']))
    
    def test_field_content(self):
        """Test that the serializer fields contain the correct data."""
        data = self.serializer.data
        self.assertEqual(data['username'], self.user_data['username'])
        self.assertEqual(data['email'], self.user_data['email'])
        self.assertEqual(data['name'], self.user_data['name'])
        self.assertEqual(data['mobile'], self.user_data['mobile'])

class TaskTypeSerializerTest(TestCase):
    """Tests for the TaskTypeSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.task_type_data = {
            'name': 'Bug',
            'description': 'Bug fixing task'
        }
        self.task_type = TaskType.objects.create(**self.task_type_data)
        self.serializer = TaskTypeSerializer(instance=self.task_type)
    
    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'name', 'description']))
    
    def test_field_content(self):
        """Test that the serializer fields contain the correct data."""
        data = self.serializer.data
        self.assertEqual(data['name'], self.task_type_data['name'])
        self.assertEqual(data['description'], self.task_type_data['description'])
    
    def test_create_task_type(self):
        """Test creating a task type with the serializer."""
        serializer = TaskTypeSerializer(data={
            'name': 'Feature',
            'description': 'New feature implementation'
        })
        self.assertTrue(serializer.is_valid())
        task_type = serializer.save()
        self.assertEqual(task_type.name, 'Feature')
        self.assertEqual(task_type.description, 'New feature implementation')

class TaskCreateSerializerTest(TestCase):
    """Tests for the TaskCreateSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.task_type = TaskType.objects.create(name='Bug', description='Bug fixing task')
        self.task_data = {
            'name': 'Fix login bug',
            'description': 'Fix the bug in the login form',
            'task_type': self.task_type.id,
            'status': 'pending'
        }
    
    def test_valid_data(self):
        """Test that the serializer validates valid data."""
        serializer = TaskCreateSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())
    
    def test_create_task(self):
        """Test creating a task with the serializer."""
        serializer = TaskCreateSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.name, self.task_data['name'])
        self.assertEqual(task.description, self.task_data['description'])
        self.assertEqual(task.task_type.id, self.task_data['task_type'])
        self.assertEqual(task.status, self.task_data['status'])
    
    def test_invalid_status(self):
        """Test that the serializer rejects completed status for new tasks."""
        data = self.task_data.copy()
        data['status'] = 'completed'
        serializer = TaskCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)

class TaskUpdateSerializerTest(TestCase):
    """Tests for the TaskUpdateSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.task_type = TaskType.objects.create(name='Bug', description='Bug fixing task')
        self.task = Task.objects.create(
            name='Fix login bug',
            description='Fix the bug in the login form',
            task_type=self.task_type,
            status='pending'
        )
    
    def test_update_task_status(self):
        """Test updating a task's status with the serializer."""
        serializer = TaskUpdateSerializer(self.task, data={'status': 'in_progress'}, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_task = serializer.save()
        self.assertEqual(updated_task.status, 'in_progress')
    
    def test_mark_task_completed(self):
        """Test marking a task as completed with the serializer."""
        self.assertIsNone(self.task.completed_at)
        
        serializer = TaskUpdateSerializer(self.task, data={'status': 'completed'}, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_task = serializer.save()
        
        self.assertEqual(updated_task.status, 'completed')
        self.assertIsNotNone(updated_task.completed_at)

class TaskAssignmentCreateSerializerTest(TestCase):
    """Tests for the TaskAssignmentCreateSerializer."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com')
        self.admin = User.objects.create_user(username='admin', email='admin@example.com', is_staff=True)
        
        # Create a task
        self.task_type = TaskType.objects.create(name='Bug', description='Bug fixing task')
        self.task = Task.objects.create(
            name='Fix login bug',
            description='Fix the bug in the login form',
            task_type=self.task_type
        )
        
        # Set up serializer
        self.serializer = TaskAssignmentCreateSerializer(
            data={'user_ids': [self.user1.id, self.user2.id]},
            context={'task': self.task, 'request': type('obj', (object,), {'user': self.admin})}
        )
    
    def test_valid_data(self):
        """Test that the serializer validates valid data."""
        self.assertTrue(self.serializer.is_valid())
    
    def test_invalid_user_ids(self):
        """Test that the serializer rejects non-existent user IDs."""
        serializer = TaskAssignmentCreateSerializer(
            data={'user_ids': [999, 998]},
            context={'task': self.task, 'request': type('obj', (object,), {'user': self.admin})}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_ids', serializer.errors)
    
    def test_create_assignments(self):
        """Test creating task assignments with the serializer."""
        self.assertTrue(self.serializer.is_valid())
        result = self.serializer.save()
        
        self.assertEqual(result['task_id'], self.task.id)
        self.assertEqual(set(result['user_ids']), {self.user1.id, self.user2.id})
        
        # Check that the task has the correct assignees
        assignees = self.task.assignees.all()
        self.assertEqual(assignees.count(), 2)
        self.assertIn(self.user1, assignees)
        self.assertIn(self.user2, assignees)
        
        # Check the TaskAssignment objects
        assignment1 = TaskAssignment.objects.get(task=self.task, user=self.user1)
        self.assertEqual(assignment1.assigned_by, self.admin)
        
        assignment2 = TaskAssignment.objects.get(task=self.task, user=self.user2)
        self.assertEqual(assignment2.assigned_by, self.admin)

class TaskSerializerTest(TestCase):
    """Tests for the TaskSerializer."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com')
        
        # Create a task type
        self.task_type = TaskType.objects.create(name='Bug', description='Bug fixing task')
        
        # Create a task
        self.task = Task.objects.create(
            name='Fix login bug',
            description='Fix the bug in the login form',
            task_type=self.task_type,
            status='in_progress'
        )
        
        # Assign the task to users
        self.task.assignees.add(self.user1, self.user2)
        
        # Instantiate the serializer
        self.serializer = TaskSerializer(instance=self.task)
    
    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id', 'name', 'description', 'created_at', 
            'task_type', 'task_type_details', 'completed_at', 
            'status', 'assignees', 'assignments'
        }
        self.assertEqual(set(data.keys()), expected_fields)
    
    def test_field_content(self):
        """Test that the serializer fields contain the correct data."""
        data = self.serializer.data
        
        # Basic fields
        self.assertEqual(data['name'], self.task.name)
        self.assertEqual(data['description'], self.task.description)
        self.assertEqual(data['status'], self.task.status)
        
        # Task type details
        self.assertEqual(data['task_type'], self.task_type.id)
        self.assertEqual(data['task_type_details']['name'], self.task_type.name)
        self.assertEqual(data['task_type_details']['description'], self.task_type.description)
        
        # Assignees
        self.assertEqual(len(data['assignees']), 2)
        user_ids = [user['id'] for user in data['assignees']]
        self.assertIn(self.user1.id, user_ids)
        self.assertIn(self.user2.id, user_ids)
        
        # Assignments
        self.assertEqual(len(data['assignments']), 2)