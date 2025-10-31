# Task Sharing via Email - Feature Documentation

## Overview

The Task Sharing feature allows users to assign tasks via email and provide recipients with a unique link to access an AI-enabled task board for that specific task. Recipients don't need an account - they simply click the link to access their personalized task board.

## Key Features

### ✉️ **Email-Based Task Assignment**
- Send task invitations to multiple email addresses
- Recipients receive a beautifully formatted HTML email
- No account required for recipients
- Secure, unique access links

### 🔒 **Permission Levels**
- **View**: Recipients can view task details and use AI assistant
- **Edit**: Recipients can update status, add notes, and use AI assistant
- **Admin**: Recipients have full control including editing description

### ⏰ **Expiration Control**
- Set link expiration (1 day to 1 year)
- Links can be manually revoked at any time
- Automatic expiration handling

### 🤖 **AI-Enabled Task Board**
- Each shared task has its own AI assistant
- Context-aware AI help specific to the task
- Real-time task updates
- Collaborative features

---

## Backend Implementation

### Database Model: `TaskShare`

```python
class TaskShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    shared_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    share_token = db.Column(db.String(64), unique=True, index=True)
    permission = db.Column(db.String(20), default='view')
    expires_at = db.Column(db.DateTime, nullable=True)
    access_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime)
    revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### API Endpoints

#### 1. Share Task (`POST /api/tasks/share`)
**Authentication**: Required  
**Purpose**: Create a shareable link and send email invitations

**Request Body**:
```json
{
  "task_id": 1,
  "emails": ["colleague@example.com", "manager@example.com"],
  "permission": "edit",
  "expires_in_days": 30
}
```

**Response**:
```json
{
  "message": "Task shared successfully",
  "share_token": "abc123xyz789...",
  "share_link": "http://localhost:5173/task/abc123xyz789...",
  "permission": "edit",
  "expires_at": "2025-11-10T00:00:00",
  "emails_sent": ["colleague@example.com"],
  "emails_failed": []
}
```

#### 2. Access Shared Task (`GET /api/tasks/access/{share_token}`)
**Authentication**: Not required  
**Purpose**: Access task details using share token

**Response**:
```json
{
  "task": {
    "id": 1,
    "title": "Complete Q4 Report",
    "description": "Prepare comprehensive quarterly report",
    "status": "in-progress",
    "priority": "high",
    "due_date": "2025-10-15T00:00:00",
    "created_at": "2025-10-01T00:00:00",
    "updated_at": "2025-10-10T00:00:00"
  },
  "share_info": {
    "permission": "edit",
    "shared_by": "John Doe",
    "shared_at": "2025-10-10T00:00:00",
    "expires_at": "2025-11-10T00:00:00",
    "access_count": 5
  }
}
```

#### 3. Update Shared Task (`PUT /api/tasks/update/{share_token}`)
**Authentication**: Not required (uses share token)  
**Purpose**: Update task status or add notes

**Request Body**:
```json
{
  "status": "done",
  "notes": "Completed ahead of schedule"
}
```

#### 4. Revoke Share (`DELETE /api/tasks/revoke/{share_token}`)
**Authentication**: Required  
**Purpose**: Revoke access to a shared task

#### 5. List Task Shares (`GET /api/tasks/list/{task_id}`)
**Authentication**: Required  
**Purpose**: View all share links for a task

---

## Frontend Implementation

### Components

#### 1. **TaskShareModal** (`/src/components/modals/TaskShareModal.jsx`)
Modal for sharing tasks via email

**Features**:
- Multiple email input fields
- Permission level selection
- Expiration date selection
- Copy share link to clipboard
- Success/failure feedback

**Usage**:
```jsx
import TaskShareModal from './components/modals/TaskShareModal';

<TaskShareModal 
  task={selectedTask}
  onClose={() => setShowShareModal(false)}
  onShared={(response) => console.log('Task shared:', response)}
/>
```

#### 2. **SharedTaskBoard** (`/src/components/SharedTaskBoard.jsx`)
Standalone task board for shared task access

**Features**:
- View task details
- Update task status (if permitted)
- Add notes (if permitted)
- AI assistant chat
- Access tracking
- Permission-based UI

**Route**:
```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SharedTaskBoard from './components/SharedTaskBoard';

<Route path="/task/:shareToken" element={<SharedTaskBoard />} />
```

### API Service Methods

```javascript
import api from './services/api';

// Share a task
const response = await api.tasks.share({
  task_id: 1,
  emails: ['user@example.com'],
  permission: 'edit',
  expires_in_days: 30
});

// Access shared task (no auth)
const taskData = await api.tasks.accessShared(shareToken);

// Update shared task (no auth)
const updated = await api.tasks.updateShared(shareToken, {
  status: 'done'
});

// Get all shares for a task
const shares = await api.tasks.getShares(taskId);

// Revoke a share
await api.tasks.revokeShare(shareToken);
```

---

## Email Configuration

### Environment Variables

Add to `.env` file:

```env
# Email Server Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@alex.local

# Frontend URL for share links
FRONTEND_URL=http://localhost:5173
```

### Gmail Setup (Example)

1. Enable 2-factor authentication on your Google account
2. Generate an "App Password" in Google Account settings
3. Use the app password as `SMTP_PASSWORD`

### Development Mode

If SMTP credentials are not provided, emails will be logged to console instead:

```
[DEV MODE] Email would be sent to colleague@example.com
Share link: http://localhost:5173/task/abc123xyz789...
```

---

## Email Template

Recipients receive a professional HTML email with:

- **Header**: Alex AI Workspace branding
- **Task Assignment**: Who assigned it and task title
- **Call-to-Action**: Large button to access task board
- **Features List**: What they can do with the link
- **Footer**: Automated message disclaimer

---

## Security Features

### 🔐 Token Generation
- 32-character random tokens using `secrets` module
- Cryptographically secure
- Unique per share

### ⏰ Expiration Handling
- Automatic expiration checks on access
- Returns 410 (Gone) for expired links
- Configurable expiration periods

### 🚫 Revocation
- Instant revocation by task owner
- Returns 403 (Forbidden) for revoked links
- Cannot be un-revoked

### 📊 Access Tracking
- Track number of accesses
- Record last access time
- View access analytics

### 🔒 Permission Enforcement
- Server-side permission checks
- View-only users cannot edit
- Edit users cannot change core details
- Admin users have full control

---

## User Flow

### For Task Owner:

1. Click "Share" button on a task
2. Enter email addresses of recipients
3. Select permission level (view/edit/admin)
4. Set expiration period
5. Click "Send Invitations"
6. Copy share link for additional distribution
7. Track access and revoke if needed

### For Task Recipient:

1. Receive email invitation
2. Click "Open Task Board" button
3. Access AI-enabled task board (no login required)
4. View task details
5. Use AI assistant for help
6. Update status/add notes (if permitted)
7. Collaborate in real-time

---

## Use Cases

### 1. **External Contractor Assignment**
- Share task with contractor email
- Set "edit" permission
- 30-day expiration
- Contractor updates progress without account

### 2. **Client Review**
- Share task with client for approval
- Set "view" permission
- 7-day expiration
- Client sees progress and provides feedback

### 3. **Team Collaboration**
- Share with multiple team members
- Set "admin" permission
- 90-day expiration
- Everyone can update and collaborate

### 4. **Temporary Access**
- Share with temporary worker
- Set "edit" permission
- 1-day expiration
- Auto-expires after work is done

---

## Testing

### Manual Testing Steps

1. **Create a task** in the main interface
2. **Click share button** and enter your email
3. **Check your inbox** for the invitation
4. **Click the link** in the email
5. **Verify** you can access the task board
6. **Try updating** status (if you have edit permission)
7. **Use AI assistant** to ask about the task
8. **Check access count** in the share info section

### API Testing with cURL

```bash
# Share a task
curl -X POST http://localhost:5000/api/tasks/share \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "emails": ["test@example.com"],
    "permission": "edit",
    "expires_in_days": 30
  }'

# Access shared task
curl http://localhost:5000/api/tasks/access/SHARE_TOKEN

# Update shared task
curl -X PUT http://localhost:5000/api/tasks/update/SHARE_TOKEN \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

---

## Database Migration

Run this SQL to add the `task_shares` table:

```sql
CREATE TABLE task_shares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    shared_by INTEGER NOT NULL,
    share_token VARCHAR(64) UNIQUE NOT NULL,
    permission VARCHAR(20) DEFAULT 'view',
    expires_at DATETIME,
    access_count INTEGER DEFAULT 0,
    last_accessed DATETIME,
    revoked BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (shared_by) REFERENCES users(id)
);

CREATE INDEX idx_share_token ON task_shares(share_token);
CREATE INDEX idx_share_task ON task_shares(task_id);
CREATE INDEX idx_share_expires ON task_shares(expires_at);
```

---

## Troubleshooting

### Email Not Sending

**Problem**: Emails not being delivered  
**Solutions**:
- Check SMTP credentials in `.env`
- Verify SMTP server and port
- Check spam folder
- Enable "Less secure apps" (Gmail)
- Use app-specific password (Gmail)

### Link Not Working

**Problem**: Share link returns error  
**Solutions**:
- Check if link has expired
- Verify link hasn't been revoked
- Ensure `FRONTEND_URL` is correct in backend
- Check browser console for errors

### Permission Denied

**Problem**: Cannot update task  
**Solutions**:
- Verify permission level (view/edit/admin)
- Check if link has expired
- Ensure task still exists
- Try refreshing the page

---

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Email notifications for task updates
- [ ] Bulk sharing to multiple tasks
- [ ] Share templates for common scenarios
- [ ] Analytics dashboard for shares
- [ ] QR code generation for shares
- [ ] Mobile app deep linking
- [ ] Integration with calendar apps
- [ ] Slack/Teams integration
- [ ] Custom email templates

---

## Summary

The Task Sharing feature provides a seamless way to collaborate on tasks with external parties without requiring them to create accounts. It combines email invitations, secure access links, permission management, and AI assistance into a powerful collaboration tool.

**Key Benefits**:
- ✅ No account required for recipients
- ✅ Secure, expiring links
- ✅ AI-powered assistance
- ✅ Flexible permissions
- ✅ Easy to use
- ✅ Professional email invitations
- ✅ Real-time collaboration

**Perfect for**: External contractors, client reviews, temporary workers, team collaboration, and any scenario where you need to share task access without creating full user accounts.

