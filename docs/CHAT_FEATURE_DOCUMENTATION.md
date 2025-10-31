# AI Group Chat Feature Documentation

**Version:** 1.0  
**Date:** October 15, 2025  
**Author:** Manus AI

---

## Overview

This document describes the AI Group Chat feature implementation for the Alex AI Workspace. The feature provides two complementary chat systems:

1. **Group Chat** - Multi-user chat for task collaboration
2. **AI Assistant** - Private 1-to-1 AI chat that can read group chat history

---

## Features

### Group Chat

- **Task-based Chat Rooms** - Each task has its own dedicated chat room
- **Automatic Participant Management** - All task members (assignee, supervisor, collaborators) are automatically added
- **Rich Messaging** - Support for text messages, file attachments, and system notifications
- **Message Management** - Edit and delete your own messages
- **Read Tracking** - Track when users last read messages
- **Role-based Access** - Admin, member, and viewer roles
- **Pagination** - Efficient message loading with pagination

### AI Assistant

- **Private Conversations** - Each user has their own AI assistant per task
- **Group Context Awareness** - AI can read and reference group chat history
- **Contextual Responses** - AI provides task-specific assistance based on full context
- **Conversation History** - Full history of user-AI interactions
- **Performance Tracking** - Monitor AI response times and token usage
- **Auto-sync** - Group chat context automatically included in AI responses

---

## Database Schema

### TaskChat Model

```python
class TaskChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), unique=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean)
```

### ChatMessage Model

```python
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('task_chats.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    message_type = db.Column(db.String(20))  # text, file, system
    created_at = db.Column(db.DateTime)
    edited_at = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean)
    message_metadata = db.Column(db.JSON)
```

### ChatParticipant Model

```python
class ChatParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('task_chats.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role = db.Column(db.String(20))  # admin, member, viewer
    joined_at = db.Column(db.DateTime)
    last_read_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean)
```

### AIChat Model

```python
class AIChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean)
    context_summary = db.Column(db.Text)
    last_sync_at = db.Column(db.DateTime)
```

### AIChatMessage Model

```python
class AIChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ai_chat_id = db.Column(db.Integer, db.ForeignKey('ai_chats.id'))
    role = db.Column(db.String(20))  # user, assistant, system
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    model = db.Column(db.String(50))
    tokens_used = db.Column(db.Integer)
    response_time = db.Column(db.Float)
    group_chat_context = db.Column(db.JSON)
```

---

## API Endpoints

### Group Chat Endpoints

#### Create/Get Task Chat

```http
POST /api/tasks/{task_id}/chat
GET /api/tasks/{task_id}/chat
Authorization: Bearer <token>
```

**Response:**
```json
{
    "id": 1,
    "task_id": 3,
    "created_at": "2025-10-15T22:29:53.352875",
    "updated_at": "2025-10-15T22:29:53.352879",
    "is_active": true,
    "message_count": 0,
    "participant_count": 4
}
```

#### Get Chat Messages

```http
GET /api/tasks/{task_id}/chat/messages?page=1&per_page=50
Authorization: Bearer <token>
```

**Response:**
```json
{
    "messages": [
        {
            "id": 1,
            "chat_id": 1,
            "user_id": 1,
            "message": "Hello team!",
            "message_type": "text",
            "created_at": "2025-10-15T22:30:14.271997",
            "edited_at": null,
            "is_deleted": false,
            "user": {
                "id": 1,
                "name": "Admin User",
                "email": "admin@alex.local",
                "role": "Manager"
            }
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 50,
        "total": 2,
        "pages": 1,
        "has_next": false,
        "has_prev": false
    }
}
```

#### Send Message

```http
POST /api/tasks/{task_id}/chat/messages
Authorization: Bearer <token>
Content-Type: application/json

{
    "message": "Hello team!",
    "message_type": "text",
    "metadata": {}
}
```

#### Edit Message

```http
PUT /api/tasks/{task_id}/chat/messages/{message_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "message": "Updated message"
}
```

#### Delete Message

```http
DELETE /api/tasks/{task_id}/chat/messages/{message_id}
Authorization: Bearer <token>
```

#### Get Participants

```http
GET /api/tasks/{task_id}/chat/participants
Authorization: Bearer <token>
```

#### Add Participant

```http
POST /api/tasks/{task_id}/chat/participants
Authorization: Bearer <token>
Content-Type: application/json

{
    "user_id": 5,
    "role": "member"
}
```

#### Remove Participant

```http
DELETE /api/tasks/{task_id}/chat/participants/{user_id}
Authorization: Bearer <token>
```

---

### AI Assistant Endpoints

#### Create/Get AI Chat

```http
POST /api/tasks/{task_id}/ai-chat
GET /api/tasks/{task_id}/ai-chat
Authorization: Bearer <token>
```

**Response:**
```json
{
    "id": 1,
    "user_id": 1,
    "task_id": 3,
    "created_at": "2025-10-15T22:30:14.400035",
    "updated_at": "2025-10-15T22:30:14.400038",
    "is_active": true,
    "last_sync_at": null,
    "message_count": 1
}
```

#### Get AI Chat Messages

```http
GET /api/tasks/{task_id}/ai-chat/messages?limit=50
Authorization: Bearer <token>
```

#### Send Message to AI

```http
POST /api/tasks/{task_id}/ai-chat/messages
Authorization: Bearer <token>
Content-Type: application/json

{
    "message": "Can you summarize the group chat?",
    "include_group_context": true
}
```

**Response:**
```json
{
    "user_message": {
        "id": 2,
        "ai_chat_id": 1,
        "role": "user",
        "message": "Can you summarize the group chat?",
        "created_at": "2025-10-15T22:30:14.465123"
    },
    "ai_response": {
        "id": 3,
        "ai_chat_id": 1,
        "role": "assistant",
        "message": "Based on the group chat...",
        "created_at": "2025-10-15T22:30:14.476269",
        "model": "phi3",
        "tokens_used": 150,
        "response_time": 0.8,
        "group_chat_context": {
            "chat_id": 1,
            "message_count": 2,
            "messages": [...]
        }
    }
}
```

#### Sync Group Chat Context

```http
POST /api/tasks/{task_id}/ai-chat/sync
Authorization: Bearer <token>
```

**Response:**
```json
{
    "message": "Group chat context synced successfully",
    "synced": true,
    "message_count": 2,
    "last_sync_at": "2025-10-15T22:30:14.432730"
}
```

#### Get AI Context Understanding

```http
GET /api/tasks/{task_id}/ai-chat/context
Authorization: Bearer <token>
```

---

## Usage Examples

### Example 1: Basic Group Chat Flow

```javascript
// 1. Create chat for task
const chatResponse = await fetch('/api/tasks/3/chat', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
const chat = await chatResponse.json();

// 2. Send message
const messageResponse = await fetch('/api/tasks/3/chat/messages', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: 'Hello team!',
        message_type: 'text'
    })
});

// 3. Get messages
const messagesResponse = await fetch('/api/tasks/3/chat/messages', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
const messages = await messagesResponse.json();
```

### Example 2: AI Assistant with Group Context

```javascript
// 1. Create AI chat
const aiChatResponse = await fetch('/api/tasks/3/ai-chat', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

// 2. Sync group chat context
await fetch('/api/tasks/3/ai-chat/sync', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

// 3. Ask AI about group chat
const aiResponse = await fetch('/api/tasks/3/ai-chat/messages', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: 'What are the main topics discussed in the group chat?',
        include_group_context: true
    })
});
```

---

## Security & Access Control

### Authentication
- All endpoints require valid JWT token
- Token must be included in `Authorization: Bearer <token>` header

### Authorization
- Users can only access chats for tasks they're assigned to
- Task assignee, supervisor, and collaborators have access
- Chat admins can add/remove participants
- Users can only edit/delete their own messages

### Data Privacy
- AI chats are private to each user
- Group chats are scoped to task participants
- Deleted messages are soft-deleted (marked as deleted but not removed)

---

## Performance Considerations

### Database Indexes
- `idx_task_chat_task` - Fast lookup of chat by task
- `idx_chat_msg_chat` - Fast message retrieval
- `idx_chat_msg_created` - Efficient pagination
- `idx_chat_participant_chat` - Quick participant lookup
- `idx_ai_chat_user` - Fast AI chat lookup by user
- `idx_ai_chat_task` - Fast AI chat lookup by task

### Pagination
- Messages are paginated (default 50 per page, max 100)
- Newest messages first for better UX
- `before` parameter for infinite scroll

### AI Context Optimization
- Only last 50 group messages included in context
- Context summary cached in database
- Automatic sync on AI message send

---

## Future Enhancements

1. **Real-time Updates** - WebSocket/SSE for live message delivery
2. **File Attachments** - Upload and share files in chat
3. **Mentions** - @mention users in messages
4. **Reactions** - React to messages with emojis
5. **Threading** - Reply to specific messages
6. **Search** - Full-text search across chat history
7. **AI Summaries** - AI-generated chat summaries
8. **Voice Messages** - Audio message support
9. **Message Formatting** - Markdown support
10. **Notifications** - Push notifications for new messages

---

## Testing

All endpoints have been tested and verified:

✅ Group chat creation  
✅ Message sending and retrieval  
✅ Message editing and deletion  
✅ Participant management  
✅ Read tracking  
✅ AI chat creation  
✅ Group context syncing  
✅ AI message generation  
✅ Context-aware AI responses  

---

## Troubleshooting

### Issue: 404 Not Found on chat endpoints
**Solution:** Ensure blueprints are registered in `main.py`:
```python
app.register_blueprint(task_chat_bp, url_prefix="/api")
app.register_blueprint(ai_chat_bp, url_prefix="/api")
```

### Issue: AI service unavailable
**Solution:** Ensure Ollama is running:
```bash
ollama serve
```

### Issue: Collaborators access error
**Solution:** The system handles both string and object collaborators automatically.

---

## Conclusion

The AI Group Chat feature provides a comprehensive collaboration platform with intelligent AI assistance. The dual-chat system allows teams to collaborate effectively while giving each member access to a private AI assistant that understands the full context of team discussions.

**Status:** ✅ Production Ready  
**Test Coverage:** All endpoints tested  
**Documentation:** Complete

