# Alex AI Workspace - API Documentation

**Version:** 2.0.0  
**Base URL:** `http://localhost:5000/api`  
**Authentication:** JWT Bearer Token

---

## Table of Contents

1. [Authentication](#authentication)
2. [Tasks](#tasks)
3. [Task Chat](#task-chat)
4. [AI Assistant](#ai-assistant)
5. [Emails](#emails)
6. [Team](#team)
7. [Files](#files)
8. [AI Features](#ai-features)
9. [Error Handling](#error-handling)

---

## Authentication

### Login

**POST** `/auth/login`

Authenticate user and receive JWT tokens.

**Request:**
```json
{
  "email": "admin@alex.local",
  "password": "admin123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "user": {
    "id": 1,
    "name": "Admin User",
    "email": "admin@alex.local",
    "role": "Manager",
    "online": true,
    "created_at": "2025-10-15T22:39:42.685713",
    "last_login": "2025-10-17T15:00:00.000000"
  },
  "message": "Login successful"
}
```

### Register

**POST** `/auth/register`

Create a new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "role": "user"
}
```

**Response:** `201 Created`
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 5,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

### Get Current User

**GET** `/users/me`

Get authenticated user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Admin User",
  "email": "admin@alex.local",
  "role": "Manager",
  "online": true,
  "created_at": "2025-10-15T22:39:42.685713",
  "last_login": "2025-10-17T15:00:00.000000"
}
```

---

## Tasks

### List Tasks

**GET** `/tasks`

Get paginated list of tasks.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `status` (optional): Filter by status (todo, in-progress, done)
- `urgent` (optional): Filter urgent tasks (true/false)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Complete Q4 Financial Report",
      "description": "Prepare comprehensive financial report for Q4",
      "status": "in-progress",
      "urgent": true,
      "deadline": "2025-10-16T03:39:42.687916",
      "assignee_id": 1,
      "supervisor_id": 2,
      "collaborators": ["3", "4"],
      "created_at": "2025-10-15T22:39:42.692789",
      "updated_at": "2025-10-15T22:39:42.692791",
      "assignee": {
        "id": 1,
        "name": "Admin User",
        "email": "admin@alex.local",
        "role": "Manager"
      },
      "supervisor": {
        "id": 2,
        "name": "Sarah Johnson",
        "email": "sarah.j@alex.local",
        "role": "Manager"
      }
    }
  ],
  "total": 5,
  "pages": 1,
  "current_page": 1,
  "per_page": 20,
  "has_next": false,
  "has_prev": false
}
```

### Create Task

**POST** `/tasks`

Create a new task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "title": "Design Landing Page",
  "description": "Create responsive landing page for new product",
  "assignee_id": 3,
  "supervisor_id": 2,
  "status": "todo",
  "urgent": false,
  "deadline": "2025-10-25T12:00:00Z"
}
```

**Response:** `201 Created`
```json
{
  "id": 6,
  "title": "Design Landing Page",
  "description": "Create responsive landing page for new product",
  "status": "todo",
  "urgent": false,
  "deadline": "2025-10-25T12:00:00Z",
  "assignee_id": 3,
  "supervisor_id": 2,
  "collaborators": [],
  "created_at": "2025-10-17T15:30:00.000000",
  "updated_at": "2025-10-17T15:30:00.000000"
}
```

### Get Task

**GET** `/tasks/:id`

Get a specific task by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Complete Q4 Financial Report",
  "description": "Prepare comprehensive financial report for Q4",
  "status": "in-progress",
  "urgent": true,
  "deadline": "2025-10-16T03:39:42.687916",
  "assignee_id": 1,
  "supervisor_id": 2,
  "collaborators": ["3", "4"],
  "created_at": "2025-10-15T22:39:42.692789",
  "updated_at": "2025-10-15T22:39:42.692791"
}
```

### Update Task

**PUT** `/tasks/:id`

Update an existing task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "status": "done",
  "description": "Updated description"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Complete Q4 Financial Report",
  "description": "Updated description",
  "status": "done",
  "updated_at": "2025-10-17T16:00:00.000000"
}
```

### Delete Task

**DELETE** `/tasks/:id`

Delete a task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "message": "Task deleted successfully"
}
```

---

## Task Chat

### Create/Get Task Chat

**POST/GET** `/tasks/:id/chat`

Create or retrieve group chat for a task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK` or `201 Created`
```json
{
  "id": 1,
  "task_id": 3,
  "created_at": "2025-10-17T15:00:00.000000",
  "participants": [
    {
      "id": 1,
      "user_id": 1,
      "role": "admin",
      "joined_at": "2025-10-17T15:00:00.000000",
      "user": {
        "id": 1,
        "name": "Admin User",
        "email": "admin@alex.local"
      }
    }
  ]
}
```

### Get Chat Messages

**GET** `/tasks/:id/chat/messages`

Get paginated chat messages for a task.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 50)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "messages": [
    {
      "id": 1,
      "chat_id": 1,
      "user_id": 1,
      "message": "Hello team! Ready to collaborate.",
      "created_at": "2025-10-17T15:05:00.000000",
      "updated_at": "2025-10-17T15:05:00.000000",
      "is_deleted": false,
      "user": {
        "id": 1,
        "name": "Admin User",
        "email": "admin@alex.local"
      }
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 50,
  "pages": 1
}
```

### Send Chat Message

**POST** `/tasks/:id/chat/messages`

Send a message in task chat.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "message": "I'll start working on this today."
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "chat_id": 1,
  "user_id": 1,
  "message": "I'll start working on this today.",
  "created_at": "2025-10-17T15:10:00.000000",
  "updated_at": "2025-10-17T15:10:00.000000",
  "is_deleted": false
}
```

### Update Chat Message

**PUT** `/tasks/:id/chat/messages/:message_id`

Edit a chat message.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "message": "Updated message content"
}
```

**Response:** `200 OK`
```json
{
  "id": 2,
  "message": "Updated message content",
  "updated_at": "2025-10-17T15:15:00.000000"
}
```

### Delete Chat Message

**DELETE** `/tasks/:id/chat/messages/:message_id`

Soft delete a chat message.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "message": "Message deleted successfully"
}
```

### Get Chat Participants

**GET** `/tasks/:id/chat/participants`

Get list of chat participants.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "participants": [
    {
      "id": 1,
      "user_id": 1,
      "role": "admin",
      "joined_at": "2025-10-17T15:00:00.000000",
      "last_read_at": "2025-10-17T15:20:00.000000",
      "user": {
        "id": 1,
        "name": "Admin User",
        "email": "admin@alex.local",
        "online": true
      }
    }
  ],
  "total": 1
}
```

---

## AI Assistant

### Create/Get AI Chat

**POST/GET** `/tasks/:id/ai-chat`

Create or retrieve private AI assistant chat for a task.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK` or `201 Created`
```json
{
  "id": 1,
  "task_id": 3,
  "user_id": 1,
  "context_synced_at": "2025-10-17T15:00:00.000000",
  "created_at": "2025-10-17T15:00:00.000000"
}
```

### Get AI Chat Messages

**GET** `/tasks/:id/ai-chat/messages`

Get AI conversation history.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 50)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "messages": [
    {
      "id": 1,
      "ai_chat_id": 1,
      "role": "assistant",
      "content": "Hello! I'm your AI assistant for this task. How can I help?",
      "created_at": "2025-10-17T15:00:00.000000"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 50
}
```

### Send Message to AI

**POST** `/tasks/:id/ai-chat/messages`

Send a message to AI assistant.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "message": "Can you summarize the team discussion?"
}
```

**Response:** `201 Created`
```json
{
  "user_message": {
    "id": 2,
    "role": "user",
    "content": "Can you summarize the team discussion?",
    "created_at": "2025-10-17T15:25:00.000000"
  },
  "ai_response": {
    "id": 3,
    "role": "assistant",
    "content": "Based on the group chat, the team discussed...",
    "created_at": "2025-10-17T15:25:01.000000"
  }
}
```

### Sync Group Chat Context

**POST** `/tasks/:id/ai-chat/sync`

Sync group chat messages to AI context.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "message": "Context synced successfully",
  "messages_synced": 5,
  "synced_at": "2025-10-17T15:30:00.000000"
}
```

---

## Emails

### List Emails

**GET** `/emails`

Get paginated list of emails.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `priority` (optional): Filter by priority
- `is_read` (optional): Filter by read status (true/false)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "emails": [
    {
      "id": 1,
      "subject": "Q4 Planning Meeting",
      "sender": "sarah@company.com",
      "recipient": "admin@alex.local",
      "body": "Let's schedule a meeting...",
      "priority": "high",
      "is_read": false,
      "received_at": "2025-10-17T10:00:00.000000",
      "created_at": "2025-10-17T10:00:00.000000"
    }
  ],
  "total": 2,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

### Get Email

**GET** `/emails/:id`

Get a specific email.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "subject": "Q4 Planning Meeting",
  "sender": "sarah@company.com",
  "recipient": "admin@alex.local",
  "body": "Let's schedule a meeting to discuss Q4 planning...",
  "priority": "high",
  "is_read": true,
  "received_at": "2025-10-17T10:00:00.000000",
  "created_at": "2025-10-17T10:00:00.000000"
}
```

### Update Email

**PUT** `/emails/:id`

Update email (mark as read, change priority, etc.).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "is_read": true,
  "priority": "normal"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "is_read": true,
  "priority": "normal",
  "updated_at": "2025-10-17T15:30:00.000000"
}
```

---

## Team

### List Team Members

**GET** `/team/members`

Get paginated list of team members.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `role` (optional): Filter by role

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "members": [
    {
      "id": 1,
      "name": "Admin User",
      "email": "admin@alex.local",
      "role": "Manager",
      "online": true,
      "created_at": "2025-10-15T22:39:42.685713",
      "last_login": "2025-10-17T15:00:00.000000"
    }
  ],
  "total": 8,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

### Get Team Statistics

**GET** `/team/stats`

Get team statistics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "total_members": 8,
  "online_members": 5,
  "roles": {
    "Manager": 2,
    "Developer": 3,
    "Designer": 3
  },
  "active_tasks": 5,
  "completed_tasks": 12
}
```

---

## Files

### List Files

**GET** `/files/list`

Get paginated list of files.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "files": [],
  "total": 0,
  "page": 1,
  "per_page": 20
}
```

### Upload File

**POST** `/files/upload`

Upload a file.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request:**
```
file: <binary data>
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "filename": "document.pdf",
  "size": 1024000,
  "mime_type": "application/pdf",
  "uploaded_at": "2025-10-17T15:30:00.000000"
}
```

---

## AI Features

### Chat with AI

**POST** `/ai/chat`

Send a message to AI assistant.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "message": "Help me prioritize my tasks",
  "context": {
    "task_id": 1
  }
}
```

**Response:** `200 OK`
```json
{
  "response": "Based on your tasks, I recommend...",
  "timestamp": "2025-10-17T15:30:00.000000"
}
```

**Note:** Requires Ollama service to be running.

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "error": "Error message",
  "status_code": 400,
  "details": {}
}
```

### Common Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Authentication Errors

**401 Unauthorized:**
```json
{
  "error": "Authentication failed: Token expired",
  "status_code": 401
}
```

### Validation Errors

**400 Bad Request:**
```json
{
  "errors": {
    "title": ["Missing data for required field."],
    "assignee_id": ["Missing data for required field."]
  },
  "status_code": 400
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. Recommended for production:
- 100 requests per minute per user
- 1000 requests per hour per user

---

## Pagination

All list endpoints support pagination with these parameters:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

Response includes:
- `total`: Total number of items
- `pages`: Total number of pages
- `current_page`: Current page number
- `has_next`: Boolean indicating if there's a next page
- `has_prev`: Boolean indicating if there's a previous page

---

## Changelog

### Version 2.0.0 (2025-10-17)
- Added task group chat feature
- Added AI assistant chat feature
- Improved authentication system
- Added security headers
- Enhanced error handling

### Version 1.0.0 (2025-10-15)
- Initial release
- Basic task management
- Email management
- Team management
- File management

---

## Support

For issues or questions:
- GitHub: https://github.com/pn98z4r66t-spec/alex-backend
- Documentation: See README.md


