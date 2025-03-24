"""
Tests for the views of the task_management app.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from ..models import User, Task, TaskType, TaskAssignment

class UserViewSetTest(APITestCase):
    """Tests for the UserViewSet."""

    def setUp(self):
        """Set up test data."""
        # Create users
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1pass',
            name='User One',
            mobile='1111111111'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user2pass'
        )

        # Set up client
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

        # URLs
        self.users_url = reverse('user-list')
        self.user1_url = reverse('user-detail', kwargs={'pk': self.user1.id})
        self.user1_tasks_url = reverse('user-tasks', kwargs={'pk': self.user1.id})

    def test_get_users_list(self):
        """Test that authenticated users can get the list of users."""
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that all users are returned
        self.assertEqual(len(response.data['results']), 3)

    def test_get_user_detail(self):
        """Test that authenticated users can get details of a specific user."""
        response = self.client.get(self.user1_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the correct user is returned
        self.assertEqual(response.data['id'], self.user1.id)
        self.assertEqual(response.data['username'], self.user1.username)

    def test_get_user_tasks(self):
        """Test that authenticated users can get tasks assigned to a specific user."""
        # Create task type
        task_type = TaskType.objects.create(name='Development')
        # Create tasks
        task1 = Task.objects.create(name='Task 1', task_type=task_type)
        task2 = Task.objects.create(name='Task 2', task_type=task_type)
        # Assign tasks to user1
        TaskAssignment.objects.create(task=task1, user=self.user1)
        TaskAssignment.objects.create(task=task2, user=self.user1)

        response = self.client.get(self.user1_tasks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that two tasks are returned
        self.assertEqual(len(response.data), 2)
        # Check that the tasks are assigned to user1
        for task_data in response.data:
            task = Task.objects.get(id=task_data['id'])
            self.assertTrue(self.user1 in task.assignees.all())

    def test_get_users_list_unauthenticated(self):
        """Test that unauthenticated users cannot get the list of users."""
        self.client.logout()
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_detail_unauthenticated(self):
        """Test that unauthenticated users cannot get details of a specific user."""
        self.client.logout()
        response = self.client.get(self.user1_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_tasks_unauthenticated(self):
        """Test that unauthenticated users cannot get tasks assigned to a specific user."""
        self.client.logout()
        response = self.client.get(self.user1_tasks_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)