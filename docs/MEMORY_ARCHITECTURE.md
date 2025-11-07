# AI Memory Architecture

## Overview

The Alex AI Workspace implements a sophisticated memory system that provides unlimited context windows through a combination of short-term (session-based) and long-term (persistent) memory storage.

## Memory Types

### 1. Short-Term Memory (Session Memory)
**Purpose:** Maintain context within a single conversation or work session.

**Storage:** In-memory cache with database backup
**Retention:** Current session only (cleared on logout)
**Capacity:** Last 50 messages or 100,000 tokens

**Contents:**
- Current conversation history
- Recent task updates
- Active context and topics
- Temporary preferences

### 2. Long-Term Memory (Persistent Memory)
**Purpose:** Remember user patterns, preferences, and historical context across sessions.

**Storage:** Database (SQLite/PostgreSQL)
**Retention:** Permanent (with user control)
**Capacity:** Unlimited

**Contents:**
- User profile and preferences
- Work patterns and habits
- Historical decisions and rationale
- Project context and goals
- Key insights and learnings
- Important conversations

### 3. Semantic Memory (Knowledge Base)
**Purpose:** Store structured knowledge about the user's business, projects, and domain.

**Storage:** Vector database (for future enhancement)
**Retention:** Permanent
**Capacity:** Unlimited

**Contents:**
- Business domain knowledge
- Project documentation
- Decision frameworks
- Best practices
- Lessons learned

## Database Schema

### ConversationHistory Table
```sql
CREATE TABLE conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id VARCHAR(255),
    role VARCHAR(50) NOT NULL,  -- 'user' or 'assistant'
    message TEXT NOT NULL,
    tokens_used INTEGER,
    context_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### UserMemory Table
```sql
CREATE TABLE user_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    memory_type VARCHAR(50) NOT NULL,  -- 'preference', 'pattern', 'insight', 'goal'
    key VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, memory_type, key)
);
```

### ContextSummary Table
```sql
CREATE TABLE context_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    summary_type VARCHAR(50) NOT NULL,  -- 'daily', 'weekly', 'project'
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    metadata JSON,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Memory Management

### Context Window Strategy

1. **Recent Context (Last 10 messages)**
   - Full message history
   - Highest priority in AI prompt

2. **Session Summary (11-50 messages)**
   - Summarized key points
   - Medium priority

3. **Long-Term Context**
   - User preferences
   - Relevant past decisions
   - Project context
   - Low priority but always included

### Memory Retrieval Algorithm

```python
def build_ai_context(user_id, current_message):
    context = []
    
    # 1. Add user profile and preferences
    context.append(get_user_profile(user_id))
    
    # 2. Add relevant long-term memories
    relevant_memories = search_memories(user_id, current_message)
    context.extend(relevant_memories)
    
    # 3. Add recent conversation history
    recent_history = get_recent_history(user_id, limit=10)
    context.extend(recent_history)
    
    # 4. Add current tasks and projects
    active_tasks = get_active_tasks(user_id)
    context.append(format_tasks_context(active_tasks))
    
    # 5. Add current message
    context.append(current_message)
    
    return context
```

### Memory Formation

**Automatic Memory Creation:**
- User preferences detected from conversations
- Work patterns identified from task history
- Important insights extracted from AI responses
- Decision rationale captured automatically

**Manual Memory Creation:**
- User can explicitly save important information
- Mark conversations as "important"
- Add notes and context to tasks

### Memory Pruning

**Short-Term Memory:**
- Cleared on session end
- Summarized and moved to long-term if important

**Long-Term Memory:**
- Never automatically deleted
- User can manually delete
- Low-confidence memories flagged for review

## Privacy and Control

### User Controls
- View all stored memories
- Delete specific memories
- Export memory data
- Clear all history
- Opt-out of memory storage

### Data Protection
- Memories encrypted at rest
- Access control per user
- Audit log of memory access
- GDPR-compliant data handling

## Implementation Benefits

### For Users
- AI remembers past conversations and decisions
- Personalized recommendations based on history
- No need to repeat context
- Continuous learning about user preferences
- Faster, more relevant responses

### For AI Quality
- Better context understanding
- More accurate recommendations
- Consistent personality and tone
- Ability to reference past work
- Improved decision support

## Example Use Cases

### Use Case 1: Project Continuity
**Scenario:** User asks about Q4 launch after 2 weeks

**Without Memory:**
"What Q4 launch are you referring to?"

**With Memory:**
"Based on our previous conversations about the AI-powered analytics feature launch in Q4, here's an update on the timeline we discussed..."

### Use Case 2: Preference Learning
**Scenario:** User consistently prefers detailed analysis

**Without Memory:**
Provides brief responses each time

**With Memory:**
Automatically provides detailed, data-driven analysis knowing the user's preference

### Use Case 3: Decision Context
**Scenario:** User asks why they chose option A

**Without Memory:**
"I don't have context about that decision"

**With Memory:**
"On October 15th, you chose option A because of the following factors: [lists reasons from past conversation]"

## Future Enhancements

1. **Vector Search**
   - Semantic search across all memories
   - Find similar past situations
   - Better context retrieval

2. **Memory Graphs**
   - Connect related memories
   - Build knowledge graphs
   - Visualize decision trees

3. **Collaborative Memory**
   - Team-shared context
   - Project memory pools
   - Cross-user insights

4. **AI Memory Curation**
   - AI suggests important memories
   - Automatic summarization
   - Memory quality scoring

