# Task Instance with Native AI Integration - Complete Documentation

## Overview

The enhanced Task Instance system provides a powerful collaborative workspace where each task has its own **native AI assistant** that can read task files, understand context, and help users complete their work. This creates a seamless integration between task management, file storage, and AI assistance.

---

## 🎯 Key Concepts

### **Task Instance**
A task instance is a complete workspace that includes:
- Task details (title, description, status, priority)
- Native AI assistant with file access
- Subtasks showing what others are working on
- Reference files with privilege management
- Collaboration team with role-based permissions
- Complete AI interaction logs
- Export capability for sharing

### **Native AI Integration**
Unlike traditional AI chatbots, the Task AI Assistant:
- **Reads all task files automatically**
- **Understands task context** (status, priority, subtasks)
- **Sees who's working on what**
- **Provides context-aware suggestions**
- **Logs all interactions** for future reference
- **Can be shared via email** with the entire task

---

## ✨ Core Features

### 1. **Native AI Assistant**

Each task has its own AI assistant that:
- Analyzes all attached files
- Provides insights and recommendations
- Answers questions about the task
- Suggests next steps and subtasks
- Tracks conversation history
- Works with task context (not just files)

**Example Interactions:**
```
User: "Can you review the requirements document?"
AI: "I've reviewed requirements.pdf. The document specifies user authentication, 
     data synchronization, and real-time notifications. The app must handle 
     10,000+ concurrent users. I recommend breaking this into 3 subtasks..."

User: "What are the next steps?"
AI: "Based on the current status and files, the next steps are:
     1. Complete data integration (Alex is working on this)
     2. Perform end-to-end testing
     3. Finalize user documentation..."
```

### 2. **Subtasks with Live Status**

**Features:**
- Create unlimited subtasks
- Assign to team members
- Real-time status tracking (To Do, In Progress, Done)
- See who's working on what
- Check off completed items
- Due dates and priorities

**Visual Indicators:**
- Blue dot (●) = Someone is actively working
- Checkboxes for completion
- Status badges (To Do, In Progress, Done)
- Assignee names displayed

**Permissions:**
- Viewers: Can see subtasks
- Editors: Can create and update subtasks
- Admins: Full control

### 3. **Reference Files with Privileges**

**File Management:**
- Attach files from file storage
- Mark files as "Reference" for AI
- Add notes to files
- View/Edit/Delete based on role
- AI automatically reads text content

**File Privileges:**
- **Viewer**: Can view files only (🔒 lock icon)
- **Editor**: Can add and edit files
- **Admin**: Can delete files

**AI Integration:**
- Files with extracted text show (👁️ eye icon)
- AI reads all reference files automatically
- AI can summarize, analyze, and answer questions about files
- File context included in all AI responses

### 4. **Collaboration & Permissions**

**Three Role Levels:**

**Viewer:**
- View task details
- See subtasks and files
- Use AI assistant
- Cannot modify anything

**Editor:**
- All Viewer permissions
- Add/edit files
- Create/update subtasks
- Full AI access

**Admin:**
- All Editor permissions
- Delete files
- Manage collaborators
- Export task data

**Permissions Matrix:**
| Permission | Viewer | Editor | Admin |
|------------|--------|--------|-------|
| View task | ✅ | ✅ | ✅ |
| Use AI | ✅ | ✅ | ✅ |
| Add files | ❌ | ✅ | ✅ |
| Edit files | ❌ | ✅ | ✅ |
| Delete files | ❌ | ❌ | ✅ |
| Add subtasks | ❌ | ✅ | ✅ |
| Manage team | ❌ | ❌ | ✅ |

### 5. **AI Interaction Logs**

**Complete History:**
- Every AI conversation is logged
- Timestamps for all interactions
- User who asked the question
- Files referenced in the response
- Action type (chat, analyze, summarize)
- Exportable for review

**Benefits:**
- Review past AI insights
- Track decision-making process
- Share AI recommendations
- Audit AI usage
- Learn from previous interactions

### 6. **Export & Email Sharing**

**Export Capabilities:**
- Complete task data (JSON format)
- All AI logs and conversations
- Subtask history
- File references
- Collaborator list
- Timestamps and metadata

**Email Sharing:**
- Share entire task instance via email
- Recipients get unique access link
- Includes AI assistant access
- All logs and files included
- Permission-based access (View/Edit/Admin)
- Expiring links with revocation

---

## 🎨 User Interface Design

### **Layout**

The task instance view uses a **split-screen design**:

**Left Panel (1/3 width):**
- Three tabs: Subtasks, Files, Team
- Shows context and collaboration
- Quick access to task components
- Add buttons for new items

**Right Panel (2/3 width):**
- Native AI chat interface
- Gradient background (white to light gray)
- AI header with file count
- Insight box for latest suggestions
- Chat history with user/AI messages
- Input field at bottom

### **Visual Elements**

**AI Header:**
```
[Robot Icon] Task AI Assistant
             Analyzing 5 files
             
[Blue Insight Box]
Latest AI Insights: Based on the requirements document,
I recommend focusing on data synchronization first...
```

**Chat Interface:**
- User messages: Black bubbles, right-aligned
- AI messages: White bubbles with robot icon, left-aligned
- Action badges: Blue tags showing "analyze", "summarize", etc.
- Timestamps: Small gray text
- Loading indicator: Spinning loader for AI responses

**Subtasks Display:**
```
☐ Create wireframes          [To Do]
  Courtney To

☐ Review requirements        [In Progress]
  Sato ● In                  (blue dot = working)

☐ Implement features         [In Progress]
  Alex ● In

☑ Write documentation        [Done]
  Tanaka As
```

**Files Display:**
```
📄 requirements.pdf          👁️ 🔒
   2.5 MB • Reference
   Notes: Main requirements document

📄 design-mockups.png        👁️
   1.2 MB
   Uploaded by Sarah
```

---

## 🔧 Technical Implementation

### **Backend Models**

#### TaskInstance
```python
class TaskInstance(db.Model):
    id = Integer (Primary Key)
    title = String(255)
    description = Text
    status = String(50)  # todo, in_progress, review, done
    priority = String(50)  # low, medium, high, urgent
    owner_id = Integer (Foreign Key -> User)
    supervisor_id = Integer (Foreign Key -> User)
    assignee_id = Integer (Foreign Key -> User)
    due_date = DateTime
    ai_context = Text  # AI's understanding
    ai_suggestions = Text  # Latest suggestions
    ai_enabled = Boolean (default: True)
    created_at = DateTime
    updated_at = DateTime
```

#### SubTask
```python
class SubTask(db.Model):
    id = Integer (Primary Key)
    parent_task_id = Integer (Foreign Key -> TaskInstance)
    title = String(255)
    description = Text
    status = String(50)  # todo, in_progress, done
    assignee_id = Integer (Foreign Key -> User)
    created_by = Integer (Foreign Key -> User)
    due_date = DateTime
    completed_at = DateTime
    created_at = DateTime
```

#### TaskFile
```python
class TaskFile(db.Model):
    id = Integer (Primary Key)
    task_id = Integer (Foreign Key -> TaskInstance)
    file_id = Integer (Foreign Key -> File)
    uploaded_by = Integer (Foreign Key -> User)
    is_reference = Boolean  # For AI context
    notes = Text
    created_at = DateTime
```

#### TaskAILog
```python
class TaskAILog(db.Model):
    id = Integer (Primary Key)
    task_id = Integer (Foreign Key -> TaskInstance)
    user_id = Integer (Foreign Key -> User)
    user_message = Text
    ai_response = Text
    files_referenced = Text  # JSON array of file IDs
    action_taken = String(100)  # chat, analyze, summarize
    created_at = DateTime
```

#### TaskCollaborator
```python
class TaskCollaborator(db.Model):
    id = Integer (Primary Key)
    task_id = Integer (Foreign Key -> TaskInstance)
    user_id = Integer (Foreign Key -> User)
    role = String(50)  # viewer, editor, admin
    can_edit_files = Boolean
    can_add_files = Boolean
    can_delete_files = Boolean
    can_use_ai = Boolean
    can_add_subtasks = Boolean
    added_by = Integer (Foreign Key -> User)
    added_at = DateTime
```

### **API Endpoints**

#### Task Instance Management
```
POST   /api/task-instances              Create new task instance
GET    /api/task-instances/:id          Get task with full details
PUT    /api/task-instances/:id          Update task
DELETE /api/task-instances/:id          Delete task
GET    /api/task-instances              List all tasks (paginated)
```

#### AI Integration
```
POST   /api/task-instances/:id/ai/chat      Chat with task AI
POST   /api/task-instances/:id/ai/analyze   AI analyzes all files
```

#### Subtasks
```
POST   /api/task-instances/:id/subtasks           Create subtask
GET    /api/task-instances/:id/subtasks           List subtasks
PUT    /api/task-instances/:id/subtasks/:sid      Update subtask
DELETE /api/task-instances/:id/subtasks/:sid      Delete subtask
```

#### Files
```
POST   /api/task-instances/:id/files              Attach file
GET    /api/task-instances/:id/files              List files
DELETE /api/task-instances/:id/files/:fid         Remove file
```

#### Collaborators
```
POST   /api/task-instances/:id/collaborators      Add collaborator
GET    /api/task-instances/:id/collaborators      List collaborators
PUT    /api/task-instances/:id/collaborators/:cid Update permissions
DELETE /api/task-instances/:id/collaborators/:cid Remove collaborator
```

#### Export & Sharing
```
GET    /api/task-instances/:id/export             Export task data
POST   /api/task-instances/:id/share              Share via email
```

### **AI Context Building**

When AI is called, the system builds comprehensive context:

```python
def _build_file_context(task, detailed=False):
    context = ""
    for task_file in task.task_files:
        file = task_file.file
        context += f"\n--- File: {file.filename} ---\n"
        
        if task_file.notes:
            context += f"Notes: {task_file.notes}\n"
        
        if file.extracted_text:
            # Limit text length
            text = file.extracted_text[:2000]  # or 5000 for detailed
            context += f"{text}\n"
    
    return context

def _call_task_ai(task, user_message):
    # Build full context
    prompt = f"""You are an AI assistant for a specific task.

Task: {task.title}
Description: {task.description}
Status: {task.status}
Priority: {task.priority}

"""
    
    # Add file context
    file_context = _build_file_context(task)
    if file_context:
        prompt += f"Reference Files:\n{file_context}\n\n"
    
    # Add subtasks context
    subtasks = task.subtasks.all()
    if subtasks:
        prompt += "Subtasks:\n"
        for st in subtasks:
            assignee = st.assignee.name if st.assignee else "Unassigned"
            prompt += f"- [{st.status}] {st.title} (Assigned to: {assignee})\n"
        prompt += "\n"
    
    prompt += f"User Question: {user_message}\n\nProvide helpful response."
    
    # Call AI API
    return call_ai_api(prompt)
```

---

## 🚀 Use Cases

### Use Case 1: **Software Development Task**

**Scenario:** Build a new authentication feature

**Setup:**
1. Create task: "Implement OAuth 2.0 Authentication"
2. Attach files:
   - requirements.pdf (Reference)
   - api-spec.yaml (Reference)
   - design-mockup.png
3. Add subtasks:
   - Set up OAuth provider (Assigned to Alex)
   - Implement login flow (Assigned to Sarah)
   - Add token refresh (Unassigned)
   - Write tests (Assigned to Mike)
4. Add collaborators:
   - Alex (Editor)
   - Sarah (Editor)
   - Mike (Editor)
   - Product Manager (Viewer)

**AI Interactions:**
```
Alex: "Can you review the API spec and suggest implementation approach?"
AI: "Based on api-spec.yaml, I recommend using the Authorization Code flow
     with PKCE. The spec requires JWT tokens with 1-hour expiration and
     refresh tokens. I suggest implementing in this order:
     1. OAuth provider configuration
     2. Authorization endpoint
     3. Token endpoint
     4. Refresh mechanism..."

Sarah: "What's the status of Alex's subtask?"
AI: "Alex is currently working on 'Set up OAuth provider' (In Progress).
     Once completed, you can begin implementing the login flow which depends
     on the OAuth configuration."

Mike: "What test cases should I write?"
AI: "Based on the requirements document, you should test:
     1. Successful authentication flow
     2. Invalid credentials handling
     3. Token expiration and refresh
     4. PKCE challenge verification
     5. Error responses per OAuth 2.0 spec..."
```

**Benefits:**
- Everyone sees real-time progress
- AI provides context-aware guidance
- Files are centralized and accessible
- No need to read all documents manually
- Complete audit trail of decisions

### Use Case 2: **Client Project Review**

**Scenario:** Client needs to review deliverables

**Setup:**
1. Create task: "Q4 Marketing Campaign Review"
2. Attach files:
   - campaign-strategy.pdf (Reference)
   - creative-assets.zip
   - budget-breakdown.xlsx (Reference)
   - timeline.pdf
3. Add client as Viewer
4. Share via email

**Client Interactions:**
```
Client: "Can you summarize the campaign strategy?"
AI: "The Q4 campaign focuses on three channels: social media, email, and
     paid search. Budget allocation is 40% social, 35% email, 25% search.
     Timeline spans October-December with weekly content releases. Key
     metrics are engagement rate, conversion rate, and ROI..."

Client: "What's the total budget?"
AI: "According to budget-breakdown.xlsx, the total campaign budget is
     $125,000, broken down as: Social Media $50,000, Email Marketing
     $43,750, Paid Search $31,250..."

Client: "When does the campaign launch?"
AI: "Per timeline.pdf, the campaign launches October 1st with initial
     social media posts. Email sequences begin October 5th, and paid
     search campaigns start October 8th..."
```

**Benefits:**
- Client has instant AI assistance
- No need to schedule meetings for simple questions
- All files in one place
- Client can review at their own pace
- Complete conversation log for reference

### Use Case 3: **Research Project Collaboration**

**Scenario:** Academic research with multiple contributors

**Setup:**
1. Create task: "Climate Change Impact Analysis"
2. Attach files:
   - research-proposal.pdf (Reference)
   - dataset-2024.csv (Reference)
   - literature-review.docx (Reference)
   - methodology.pdf (Reference)
3. Add subtasks:
   - Data cleaning (Assigned to Research Assistant)
   - Statistical analysis (Assigned to Data Scientist)
   - Write findings (Assigned to Lead Researcher)
   - Create visualizations (Assigned to Designer)
4. Add collaborators with appropriate roles

**Team Interactions:**
```
Research Assistant: "What data cleaning steps are needed?"
AI: "Based on methodology.pdf and dataset-2024.csv, you should:
     1. Remove duplicate entries (approximately 150 found)
     2. Handle missing values in temperature columns (use interpolation)
     3. Standardize date formats
     4. Filter outliers beyond 3 standard deviations
     5. Validate geographic coordinates..."

Data Scientist: "What statistical methods should I use?"
AI: "The research proposal specifies using:
     1. Linear regression for trend analysis
     2. ANOVA for regional comparisons
     3. Time series analysis for seasonal patterns
     The literature review suggests adding Mann-Kendall test for
     trend significance..."

Lead Researcher: "Summarize the key findings so far"
AI: "Based on completed subtasks and analysis files:
     1. Temperature increased 1.2°C over study period
     2. Significant regional variations (p < 0.05)
     3. Seasonal patterns show accelerating summer warming
     4. Data quality is high (95% complete)
     Current status: Data cleaning done, analysis in progress..."
```

**Benefits:**
- Distributed team stays coordinated
- AI provides methodology guidance
- Everyone sees progress in real-time
- Research decisions are documented
- Easy to export for publication

---

## 📊 Workflow Examples

### Workflow 1: **Creating and Working on a Task**

```
1. Create Task Instance
   ↓
2. Add Reference Files (AI reads them automatically)
   ↓
3. AI Analyzes Files & Provides Initial Suggestions
   ↓
4. Create Subtasks Based on AI Recommendations
   ↓
5. Assign Subtasks to Team Members
   ↓
6. Team Members Work & Update Status
   ↓
7. Use AI for Questions & Guidance
   ↓
8. Complete Subtasks
   ↓
9. Export Task with AI Logs
   ↓
10. Share with Stakeholders via Email
```

### Workflow 2: **AI-Assisted Task Completion**

```
User Opens Task
   ↓
AI Shows Latest Insights
   ↓
User Asks: "What should I do first?"
   ↓
AI Reviews Files, Subtasks, Status
   ↓
AI Suggests: "Start with subtask X because..."
   ↓
User Works on Subtask
   ↓
User Asks: "How do I implement Y?"
   ↓
AI References Relevant Files
   ↓
AI Provides Step-by-Step Guidance
   ↓
User Completes Subtask
   ↓
AI Logs All Interactions
```

### Workflow 3: **External Collaboration**

```
Internal Team Creates Task
   ↓
Attach All Relevant Files
   ↓
AI Analyzes & Summarizes
   ↓
Share Task via Email to External Collaborator
   ↓
Collaborator Receives Link
   ↓
Collaborator Opens Task (No Account Needed)
   ↓
Collaborator Sees Files, Subtasks, AI Insights
   ↓
Collaborator Asks AI Questions
   ↓
AI Provides Context-Aware Answers
   ↓
Collaborator Adds Comments/Updates
   ↓
Internal Team Sees Updates in Real-Time
   ↓
Export Complete Interaction Log
```

---

## 🔐 Security & Privacy

### **Access Control**
- Task owner has full control
- Role-based permissions (Viewer/Editor/Admin)
- Granular file permissions
- AI access can be restricted per user
- Audit trail of all actions

### **Data Protection**
- All file access is logged
- AI interactions are private to task
- Export requires authentication
- Email shares use secure tokens
- Links can expire and be revoked

### **AI Privacy**
- AI only accesses files attached to task
- AI context is task-specific
- No cross-task data leakage
- AI logs can be deleted
- AI can be disabled per task

---

## 📈 Performance Considerations

### **Optimization Tips**

**File Context:**
- Limit extracted text to 5,000 characters
- Cache file content for repeated AI calls
- Use reference flag to prioritize important files

**AI Responses:**
- Set reasonable timeout (30 seconds)
- Stream responses for better UX
- Cache common queries

**Database:**
- Index task_id, user_id, status fields
- Paginate AI logs (show latest 50)
- Eager load relationships

**Frontend:**
- Lazy load AI logs
- Debounce AI input
- Show loading states
- Cache task data

---

## 🐛 Troubleshooting

### **AI Not Responding**

**Problem**: AI chat returns error

**Solutions**:
1. Check AI service is running (Ollama/LM Studio)
2. Verify AI_API_URL in .env
3. Ensure files have extracted text
4. Check network connectivity
5. Review AI logs for errors

### **Files Not Accessible to AI**

**Problem**: AI says it can't read files

**Solutions**:
1. Verify files have extracted_text field
2. Check file is marked as "Reference"
3. Ensure file type supports text extraction
4. Re-upload file if corrupted
5. Check file permissions

### **Subtasks Not Updating**

**Problem**: Subtask status not changing

**Solutions**:
1. Check user has Editor or Admin role
2. Verify network connection
3. Refresh page
4. Check browser console for errors
5. Ensure subtask belongs to task

### **Export Fails**

**Problem**: Export returns empty or error

**Solutions**:
1. Verify user has access to task
2. Check task has data to export
3. Ensure browser allows downloads
4. Try different browser
5. Check server logs

---

## 🔮 Future Enhancements

- [ ] Real-time WebSocket updates for subtasks
- [ ] Voice commands for AI
- [ ] AI-generated subtask suggestions
- [ ] Automatic file categorization
- [ ] Task templates with AI
- [ ] Integration with calendar
- [ ] Mobile app support
- [ ] Offline AI access
- [ ] Custom AI agents per task type
- [ ] AI-powered task prioritization
- [ ] Automated status updates based on subtasks
- [ ] Integration with version control (Git)
- [ ] AI code review for development tasks
- [ ] Natural language task creation

---

## 📝 Summary

The Task Instance with Native AI Integration provides a **complete collaborative workspace** where:

✅ **Each task has its own AI assistant** that reads files and understands context  
✅ **Subtasks show real-time progress** of what team members are working on  
✅ **Files are governed by role-based permissions** (Viewer/Editor/Admin)  
✅ **All AI interactions are logged** for future reference and export  
✅ **Tasks can be shared via email** with complete AI access  
✅ **No separate AI chat needed** - AI is native to the task  
✅ **Perfect for external collaboration** - no account required for shared tasks  

**This creates a seamless experience where AI, files, tasks, and collaboration are unified in a single interface.**

---

**Version**: 2.0.0  
**Last Updated**: October 11, 2025  
**Status**: Production Ready

