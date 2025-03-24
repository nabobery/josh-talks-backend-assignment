"""
Views for the task_management app.
"""
from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
import logging

from .models import User, Task, TaskType, TaskAssignment
from .serializers import (
    UserSerializer, TaskSerializer, TaskTypeSerializer, 
    TaskCreateSerializer, TaskUpdateSerializer, TaskAssignmentCreateSerializer,
    UserTasksSerializer
)

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for listing and retrieving users."""
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['username', 'email', 'name', 'mobile']
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get tasks assigned to a specific user."""
        user = self.get_object()
        status_filter = request.query_params.get('status', None)
        
        tasks = user.assigned_tasks.all()
        if status_filter:
            tasks = tasks.filter(status=status_filter)
            
        serializer = UserTasksSerializer(tasks, many=True)
        return Response(serializer.data)

class TaskTypeViewSet(viewsets.ModelViewSet):
    """API endpoint for managing task types."""
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class TaskViewSet(viewsets.ModelViewSet):
    """API endpoint for managing tasks."""
    queryset = Task.objects.all().select_related('task_type').prefetch_related('assignees')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'task_type']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return the appropriate serializer based on the action."""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return TaskUpdateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Create a new task."""
        task = serializer.save()
        logger.info(f"Task created: {task.name} (ID: {task.id})")
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign task to one or multiple users."""
        task = self.get_object()
        serializer = TaskAssignmentCreateSerializer(
            data=request.data,
            context={'request': request, 'task': task}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Return the updated task with assignment details
            updated_task = Task.objects.get(id=task.id)
            response_serializer = TaskSerializer(updated_task)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as completed."""
        task = self.get_object()
        task.mark_completed()
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Mark a task as cancelled."""
        task = self.get_object()
        task.status = 'cancelled'
        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to the current user."""
        user = request.user
        status_filter = request.query_params.get('status', None)
        
        tasks = user.assigned_tasks.all()
        if status_filter:
            tasks = tasks.filter(status=status_filter)
            
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = UserTasksSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = UserTasksSerializer(tasks, many=True)
        return Response(serializer.data)