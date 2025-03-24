"""
Serializers for the task_management app.
"""
from rest_framework import serializers
from django.db import transaction
from .models import User, Task, TaskType, TaskAssignment

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'mobile']
        read_only_fields = ['id']

class TaskTypeSerializer(serializers.ModelSerializer):
    """Serializer for the TaskType model."""
    class Meta:
        model = TaskType
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class TaskAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for the TaskAssignment model."""
    user_details = UserSerializer(source='user', read_only=True)
    assigned_by_details = UserSerializer(source='assigned_by', read_only=True)
    
    class Meta:
        model = TaskAssignment
        fields = ['id', 'user', 'user_details', 'assigned_at', 'assigned_by', 'assigned_by_details']
        read_only_fields = ['id', 'assigned_at', 'assigned_by', 'assigned_by_details']

class TaskSerializer(serializers.ModelSerializer):
    """Serializer for the Task model with detailed information."""
    task_type_details = TaskTypeSerializer(source='task_type', read_only=True)
    assignees = UserSerializer(many=True, read_only=True)
    assignments = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'created_at', 
            'task_type', 'task_type_details', 'completed_at', 
            'status', 'assignees', 'assignments'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at', 'assignees', 'assignments']
    
    def get_assignments(self, obj):
        """Get details of all task assignments."""
        assignments = TaskAssignment.objects.filter(task=obj)
        return TaskAssignmentSerializer(assignments, many=True).data

class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a Task."""
    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'task_type', 'status']
        read_only_fields = ['id']
    
    def validate_status(self, value):
        """Validate the status field."""
        if value == 'completed':
            raise serializers.ValidationError("Cannot create a task with 'completed' status. Create it first, then mark as completed.")
        return value

class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a Task."""
    class Meta:
        model = Task
        fields = ['name', 'description', 'task_type', 'status']
    
    def validate(self, data):
        """Validate the update data."""
        if 'status' in data and data['status'] == 'completed':
            # Set completed_at timestamp when status is changed to completed
            self.instance.mark_completed()
        return data

class TaskAssignmentCreateSerializer(serializers.Serializer):
    """Serializer for assigning a task to multiple users."""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_user_ids(self, value):
        """Validate the user_ids field."""
        existing_users = User.objects.filter(id__in=value)
        if len(existing_users) != len(value):
            found_ids = [user.id for user in existing_users]
            missing_ids = [id for id in value if id not in found_ids]
            raise serializers.ValidationError(f"Users with these IDs do not exist: {missing_ids}")
        return value
    
    def create(self, validated_data):
        """Create task assignments for the specified users."""
        task = self.context['task']
        user_ids = validated_data['user_ids']
        assigned_by = self.context['request'].user
        
        with transaction.atomic():
            # Remove existing assignments that are not in the new list
            TaskAssignment.objects.filter(task=task).exclude(user_id__in=user_ids).delete()
            
            # Create new assignments
            for user_id in user_ids:
                TaskAssignment.objects.get_or_create(
                    task=task,
                    user_id=user_id,
                    defaults={'assigned_by': assigned_by}
                )
        
        return {'task_id': task.id, 'user_ids': user_ids}

class UserTasksSerializer(serializers.ModelSerializer):
    """Serializer for listing tasks assigned to a user."""
    task_type_details = TaskTypeSerializer(source='task_type', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'created_at', 
            'task_type', 'task_type_details', 'completed_at', 
            'status'
        ]
        read_only_fields = fields