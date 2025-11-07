"""
Memory Service for AI Context Management
Handles short-term and long-term memory storage and retrieval
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import desc

from src.models.models import db, ConversationHistory, UserMemory, ContextSummary, Task


class MemoryService:
    """Service for managing AI memory and context"""
    
    def __init__(self):
        self.session_cache = {}  # In-memory cache for active sessions
    
    # ==================== Short-Term Memory (Conversation History) ====================
    
    def save_conversation(self, user_id: int, role: str, message: str, 
                         session_id: Optional[str] = None, tokens_used: int = 0) -> ConversationHistory:
        """Save a conversation message to history"""
        if not session_id:
            session_id = self._get_or_create_session(user_id)
        
        conversation = ConversationHistory(
            user_id=user_id,
            session_id=session_id,
            role=role,
            message=message,
            tokens_used=tokens_used
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        return conversation
    
    def get_recent_conversations(self, user_id: int, limit: int = 10, 
                                session_id: Optional[str] = None) -> List[Dict]:
        """Get recent conversation history"""
        query = ConversationHistory.query.filter_by(user_id=user_id)
        
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        conversations = query.order_by(desc(ConversationHistory.created_at)).limit(limit).all()
        
        # Return in chronological order
        return [conv.to_dict() for conv in reversed(conversations)]
    
    def get_session_history(self, user_id: int, session_id: str) -> List[Dict]:
        """Get all conversations for a specific session"""
        conversations = ConversationHistory.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).order_by(ConversationHistory.created_at).all()
        
        return [conv.to_dict() for conv in conversations]
    
    def clear_session(self, user_id: int, session_id: str):
        """Clear a specific session's conversation history"""
        ConversationHistory.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).delete()
        db.session.commit()
    
    def _get_or_create_session(self, user_id: int) -> str:
        """Get or create a session ID for the user"""
        if user_id not in self.session_cache:
            self.session_cache[user_id] = str(uuid.uuid4())
        return self.session_cache[user_id]
    
    # ==================== Long-Term Memory (User Memory) ====================
    
    def save_memory(self, user_id: int, memory_type: str, key: str, 
                   value: str, confidence: float = 1.0) -> UserMemory:
        """Save or update a long-term memory"""
        # Try to find existing memory
        memory = UserMemory.query.filter_by(
            user_id=user_id,
            memory_type=memory_type,
            key=key
        ).first()
        
        if memory:
            # Update existing memory
            memory.value = value
            memory.confidence = confidence
            memory.updated_at = datetime.utcnow()
        else:
            # Create new memory
            memory = UserMemory(
                user_id=user_id,
                memory_type=memory_type,
                key=key,
                value=value,
                confidence=confidence
            )
            db.session.add(memory)
        
        db.session.commit()
        return memory
    
    def get_memory(self, user_id: int, memory_type: str, key: str) -> Optional[Dict]:
        """Get a specific memory"""
        memory = UserMemory.query.filter_by(
            user_id=user_id,
            memory_type=memory_type,
            key=key
        ).first()
        
        if memory:
            # Update access tracking
            memory.last_accessed = datetime.utcnow()
            memory.access_count += 1
            db.session.commit()
            
            return memory.to_dict()
        
        return None
    
    def get_memories_by_type(self, user_id: int, memory_type: str) -> List[Dict]:
        """Get all memories of a specific type"""
        memories = UserMemory.query.filter_by(
            user_id=user_id,
            memory_type=memory_type
        ).order_by(desc(UserMemory.updated_at)).all()
        
        return [memory.to_dict() for memory in memories]
    
    def get_all_memories(self, user_id: int) -> Dict[str, List[Dict]]:
        """Get all memories organized by type"""
        memories = UserMemory.query.filter_by(user_id=user_id).all()
        
        organized = {
            'preferences': [],
            'patterns': [],
            'insights': [],
            'goals': []
        }
        
        for memory in memories:
            memory_type = memory.memory_type
            if memory_type in organized:
                organized[memory_type].append(memory.to_dict())
        
        return organized
    
    def delete_memory(self, user_id: int, memory_id: int) -> bool:
        """Delete a specific memory"""
        memory = UserMemory.query.filter_by(
            id=memory_id,
            user_id=user_id
        ).first()
        
        if memory:
            db.session.delete(memory)
            db.session.commit()
            return True
        
        return False
    
    def search_memories(self, user_id: int, query: str, limit: int = 5) -> List[Dict]:
        """Search memories by keyword (simple text search)"""
        # Simple keyword search - can be enhanced with vector search later
        memories = UserMemory.query.filter(
            UserMemory.user_id == user_id,
            db.or_(
                UserMemory.key.contains(query),
                UserMemory.value.contains(query)
            )
        ).order_by(desc(UserMemory.confidence)).limit(limit).all()
        
        return [memory.to_dict() for memory in memories]
    
    # ==================== Context Building ====================
    
    def build_ai_context(self, user_id: int, current_message: str, 
                        session_id: Optional[str] = None) -> Dict:
        """Build comprehensive context for AI from all memory sources"""
        context = {
            'user_profile': self._get_user_profile_context(user_id),
            'preferences': self._get_preferences_context(user_id),
            'recent_conversations': self._get_conversation_context(user_id, session_id),
            'active_tasks': self._get_tasks_context(user_id),
            'relevant_memories': self._get_relevant_memories(user_id, current_message),
            'current_message': current_message
        }
        
        return context
    
    def _get_user_profile_context(self, user_id: int) -> Dict:
        """Get user profile information"""
        from src.models.models import User
        user = User.query.get(user_id)
        if user:
            return {
                'name': user.name,
                'role': user.role,
                'email': user.email
            }
        return {}
    
    def _get_preferences_context(self, user_id: int) -> List[str]:
        """Get user preferences as context"""
        preferences = self.get_memories_by_type(user_id, 'preference')
        return [f"{p['key']}: {p['value']}" for p in preferences]
    
    def _get_conversation_context(self, user_id: int, session_id: Optional[str]) -> List[Dict]:
        """Get recent conversation context"""
        return self.get_recent_conversations(user_id, limit=10, session_id=session_id)
    
    def _get_tasks_context(self, user_id: int) -> List[Dict]:
        """Get active tasks as context"""
        tasks = Task.query.filter_by(
            assignee_id=user_id
        ).filter(
            Task.status.in_(['todo', 'in-progress'])
        ).order_by(desc(Task.urgent), Task.deadline).limit(10).all()
        
        return [task.to_dict() for task in tasks]
    
    def _get_relevant_memories(self, user_id: int, message: str) -> List[Dict]:
        """Get memories relevant to the current message"""
        # Extract keywords from message (simple approach)
        keywords = [word.lower() for word in message.split() if len(word) > 4]
        
        relevant = []
        for keyword in keywords[:3]:  # Check top 3 keywords
            memories = self.search_memories(user_id, keyword, limit=2)
            relevant.extend(memories)
        
        # Remove duplicates
        seen = set()
        unique_memories = []
        for memory in relevant:
            if memory['id'] not in seen:
                seen.add(memory['id'])
                unique_memories.append(memory)
        
        return unique_memories[:5]  # Return top 5 relevant memories
    
    def format_context_for_ai(self, context: Dict) -> str:
        """Format context dictionary into a string for AI prompt"""
        parts = []
        
        # User profile
        if context.get('user_profile'):
            profile = context['user_profile']
            parts.append(f"User: {profile.get('name')} ({profile.get('role')})")
        
        # Preferences
        if context.get('preferences'):
            parts.append("\nUser Preferences:")
            for pref in context['preferences']:
                parts.append(f"- {pref}")
        
        # Active tasks
        if context.get('active_tasks'):
            parts.append("\nActive Tasks:")
            for task in context['active_tasks'][:5]:
                status_emoji = "🔴" if task.get('urgent') else "🟢"
                parts.append(f"{status_emoji} {task['title']} ({task['status']})")
        
        # Relevant memories
        if context.get('relevant_memories'):
            parts.append("\nRelevant Past Context:")
            for memory in context['relevant_memories']:
                parts.append(f"- {memory['key']}: {memory['value']}")
        
        # Recent conversation
        if context.get('recent_conversations'):
            parts.append("\nRecent Conversation:")
            for conv in context['recent_conversations'][-5:]:  # Last 5 messages
                role = conv['role'].capitalize()
                message = conv['message'][:100]  # Truncate long messages
                parts.append(f"{role}: {message}")
        
        return "\n".join(parts)
    
    # ==================== Context Summaries ====================
    
    def create_summary(self, user_id: int, summary_type: str, title: str, 
                      summary: str, metadata: Optional[Dict] = None, 
                      date: Optional[datetime] = None) -> ContextSummary:
        """Create a context summary"""
        if not date:
            date = datetime.utcnow().date()
        
        context_summary = ContextSummary(
            user_id=user_id,
            summary_type=summary_type,
            title=title,
            summary=summary,
            meta_data=json.dumps(metadata) if metadata else None,
            date=date
        )
        
        db.session.add(context_summary)
        db.session.commit()
        
        return context_summary
    
    def get_summaries(self, user_id: int, summary_type: Optional[str] = None, 
                     days: int = 30) -> List[Dict]:
        """Get context summaries"""
        query = ContextSummary.query.filter_by(user_id=user_id)
        
        if summary_type:
            query = query.filter_by(summary_type=summary_type)
        
        start_date = datetime.utcnow().date() - timedelta(days=days)
        query = query.filter(ContextSummary.date >= start_date)
        
        summaries = query.order_by(desc(ContextSummary.date)).all()
        
        return [summary.to_dict() for summary in summaries]
    
    # ==================== Memory Analytics ====================
    
    def get_memory_stats(self, user_id: int) -> Dict:
        """Get statistics about user's memory"""
        total_conversations = ConversationHistory.query.filter_by(user_id=user_id).count()
        total_memories = UserMemory.query.filter_by(user_id=user_id).count()
        total_summaries = ContextSummary.query.filter_by(user_id=user_id).count()
        
        memory_by_type = {}
        for memory_type in ['preference', 'pattern', 'insight', 'goal']:
            count = UserMemory.query.filter_by(
                user_id=user_id,
                memory_type=memory_type
            ).count()
            memory_by_type[memory_type] = count
        
        return {
            'total_conversations': total_conversations,
            'total_memories': total_memories,
            'total_summaries': total_summaries,
            'memory_by_type': memory_by_type
        }

