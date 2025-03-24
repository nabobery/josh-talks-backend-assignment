# Josh Talks Backend Assignment

## Task Management API

A Django & Django REST Framework based API for task management, allowing users to create tasks, assign them to users, and track task status.

## Features

- Create, read, update, and delete tasks
- Assign tasks to one or multiple users
- Retrieve tasks assigned to a specific user
- Mark tasks as completed
- Task categorization with task types

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- virtualenv (recommended)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/nabobery/josh-talks-backend-assignment.git
   cd task-management-api
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   ```bash
   python manage.py makemigrations task_management
   python manage.py migrate
   ```

   **If you encounter issues with migrations (e.g., `OperationalError: no such table` or `InconsistentMigrationHistory`), try the following commands:**

   ```bash
   python manage.py migrate --fake admin 0001_initial
   python manage.py migrate task_management
   python manage.py migrate admin
   python manage.py migrate
   ```

   These commands help to resolve potential inconsistencies in migration history.

5. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:

   ```bash
   python manage.py runserver
   ```

7. Access the API at `http://127.0.0.1:8000/api/` and the admin interface at `http://127.0.0.1:8000/admin/`

## API Endpoints

### Authentication

The API uses token-based authentication. Include the token in the Authorization header:

```
Authorization: Token <your-token>
```

### User Endpoints

#### Get All Users

- **URL**: `/api/users/`
- **Method**: `GET`
- **Response Example**:

  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "name": "Admin User",
        "mobile": "1234567890"
      },
      {
        "id": 2,
        "username": "user1",
        "email": "user1@example.com",
        "name": "Test User",
        "mobile": "9876543210"
      }
    ]
  }
  ```

#### Get User Details

- **URL**: `/api/users/{id}/`
- **Method**: `GET`
- **Response Example**:

  ```json
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "name": "Admin User",
    "mobile": "1234567890"
  }
  ```

#### Get Tasks Assigned to a User

- **URL**: `/api/users/{id}/tasks/`
- **Method**: `GET`
- **Response Example**:

  ```json
  [
    {
      "id": 1,
      "name": "Implement API endpoints",
      "description": "Create the task management API endpoints",
      "created_at": "2023-04-15T10:30:00Z",
      "task_type_details": {
        "id": 1,
        "name": "Development",
        "description": "Software development tasks"
      },
      "completed_at": null,
      "status": "in_progress",
      "assignees": [
        {
          "id": 1,
          "username": "admin",
          "email": "admin@example.com",
          "name": "Admin User",
          "mobile": "1234567890"
        }
      ]
    }
  ]
  ```

### Task Endpoints

#### Get All Tasks

- **URL**: `/api/tasks/`
- **Method**: `GET`
- **Response Example**:

  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Implement API endpoints",
        "description": "Create the task management API endpoints",
        "created_at": "2023-04-15T10:30:00Z",
        "task_type": 1,
        "task_type_details": {
          "id": 1,
          "name": "Development",
          "description": "Software development tasks"
        },
        "completed_at": null,
        "status": "in_progress",
        "assignees": [
          {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "name": "Admin User",
            "mobile": "1234567890"
          }
        ]
      },
      {
        "id": 2,
        "name": "Write documentation",
        "description": "Document the API endpoints",
        "created_at": "2023-04-15T11:00:00Z",
        "task_type": 2,
        "task_type_details": {
          "id": 2,
          "name": "Documentation",
          "description": "Documentation tasks"
        },
        "completed_at": null,
        "status": "pending",
        "assignees": []
      }
    ]
  }
  ```

#### Create a Task

- **URL**: `/api/tasks/`
- **Method**: `POST`
- **Request Body Example**:

  ```json
  {
    "name": "Review code",
    "description": "Review the pull request",
    "task_type": 1,
    "status": "pending"
  }
  ```

- **Response Example**:

  ```json
  {
    "id": 3,
    "name": "Review code",
    "description": "Review the pull request",
    "created_at": "2023-04-15T12:00:00Z",
    "task_type": 1,
    "task_type_details": {
      "id": 1,
      "name": "Development",
      "description": "Software development tasks"
    },
    "completed_at": null,
    "status": "pending",
    "assignees": []
  }
  ```

#### Get Task Details

- **URL**: `/api/tasks/{id}/`
- **Method**: `GET`
- **Response Example**:

  ```json
  {
    "id": 1,
    "name": "Implement API endpoints",
    "description": "Create the task management API endpoints",
    "created_at": "2023-04-15T10:30:00Z",
    "task_type": 1,
    "task_type_details": {
      "id": 1,
      "name": "Development",
      "description": "Software development tasks"
    },
    "completed_at": null,
    "status": "in_progress",
    "assignees": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "name": "Admin User",
        "mobile": "1234567890"
      }
    ]
  }
  ```

#### Update a Task

- **URL**: `/api/tasks/{id}/`
- **Method**: `PUT` or `PATCH`
- **Request Body Example** (PATCH):

  ```json
  {
    "status": "in_progress"
  }
  ```

- **Response Example**:

  ```json
  {
    "id": 1,
    "name": "Implement API endpoints",
    "description": "Create the task management API endpoints",
    "created_at": "2023-04-15T10:30:00Z",
    "task_type": 1,
    "task_type_details": {
      "id": 1,
      "name": "Development",
      "description": "Software development tasks"
    },
    "completed_at": null,
    "status": "in_progress",
    "assignees": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "name": "Admin User",
        "mobile": "1234567890"
      }
    ]
  }
  ```

#### Delete a Task

- **URL**: `/api/tasks/{id}/`
- **Method**: `DELETE`
- **Response**: `204 No Content`

#### Assign a Task to Users

- **URL**: `/api/tasks/{id}/assign/`
- **Method**: `POST`
- **Request Body Example**:

  ```json
  {
    "user_ids": [1, 2]
  }
  ```

- **Response Example**:

  ```json
  {
    "id": 1,
    "name": "Implement API endpoints",
    "description": "Create the task management API endpoints",
    "created_at": "2023-04-15T10:30:00Z",
    "task_type": 1,
    "task_type_details": {
      "id": 1,
      "name": "Development",
      "description": "Software development tasks"
    },
    "completed_at": null,
    "status": "in_progress",
    "assignees": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "name": "Admin User",
        "mobile": "1234567890"
      },
      {
        "id": 2,
        "username": "user1",
        "email": "user1@example.com",
        "name": "Test User",
        "mobile": "9876543210"
      }
    ]
  }
  ```

#### Mark a Task as Completed

- **URL**: `/api/tasks/{id}/complete/`
- **Method**: `POST`
- **Response Example**:

  ```json
  {
    "id": 1,
    "name": "Implement API endpoints",
    "description": "Create the task management API endpoints",
    "created_at": "2023-04-15T10:30:00Z",
    "task_type": 1,
    "task_type_details": {
      "id": 1,
      "name": "Development",
      "description": "Software development tasks"
    },
    "completed_at": "2023-04-15T14:00:00Z",
    "status": "completed",
    "assignees": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "name": "Admin User",
        "mobile": "1234567890"
      },
      {
        "id": 2,
        "username": "user1",
        "email": "user1@example.com",
        "name": "Test User",
        "mobile": "9876543210"
      }
    ]
  }
  ```

### Task Type Endpoints

#### Get All Task Types

- **URL**: `/api/task-types/`
- **Method**: `GET`
- **Response Example**:

  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Development",
        "description": "Software development tasks"
      },
      {
        "id": 2,
        "name": "Documentation",
        "description": "Documentation tasks"
      }
    ]
  }
  ```

#### Create a Task Type

- **URL**: `/api/task-types/`
- **Method**: `POST`
- **Request Body Example**:

  ```json
  {
    "name": "Testing",
    "description": "Software testing tasks"
  }
  ```

- **Response Example**:

  ```json
  {
    "id": 3,
    "name": "Testing",
    "description": "Software testing tasks"
  }
  ```

## Test Credentials

For testing purposes, you can use the superuser account created during setup. If you prefer to use test users, you can create them through the Django admin interface or by running:

```bash
python manage.py shell
```

Then in the shell:

```python
from task_management.models import User
User.objects.create_user(username='testuser', email='test@example.com', password='testpassword', name='Test User', mobile='1234567890')
```

## Project Structure

```
josh-talks-backend-assignment/
├── manage.py
├── requirements.txt
├── README.md
├── .env.example
├── task_management_project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── task_management/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_models.py
    │   ├── test_views.py
    │   └── test_serializers.py
    ├── urls.py
    └── views.py
```

## Additional Information

- The API uses Django REST Framework's built-in pagination with a default page size of 10.
- Authentication is required for all endpoints.
- When a task is marked as completed, the `completed_at` timestamp is automatically set.
- The `TaskAssignment` model tracks when a task was assigned to a user and by whom.

## Running Tests

To run the tests for the `task_management` app, use the following command:

```bash
python manage.py test task_management_project.task_management
```

This command will discover and run all tests located in the `task_management/tests/` directory. Ensure you have your virtual environment activated before running tests.
