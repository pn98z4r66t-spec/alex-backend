"""
Chat Models for Group Chat and AI Assistant
Implements task-based group chat and private AI assistant functionality
"""
from datetime import datetime
from ..models.models import db


class TaskChat(db.Model):
    """
    Group chat room associated with a task
    Allows all task participants to communicate
    """
    __tablename__ = 'task_chats'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    task = db.relationship('Task', backref='chat', lazy=True)
    messages = db.relationship('ChatMessage', backref='chat', lazy='dynamic', cascade='all, delete-orphan', order_by='ChatMessage.created_at')
    participants = db.relationship('ChatParticipant', backref='chat', lazy='dynamic', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_task_chat_task', 'task_id'),
        db.Index('idx_task_chat_active', 'is_active'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'message_count': self.messages.count(),
            'participant_count': self.participants.filter_by(is_active=True).count()
        }


class ChatMessage(db.Model):
    """
    Individual messages in the group chat
    Supports text, files, system notifications, and AI responses
    """
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('task_chats.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, file, system, ai_response
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Metadata for attachments, mentions, etc.
    message_metadata = db.Column(db.JSON, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='chat_messages', lazy=True)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_chat_msg_chat', 'chat_id'),
        db.Index('idx_chat_msg_user', 'user_id'),
        db.Index('idx_chat_msg_created', 'created_at'),
        db.Index('idx_chat_msg_type', 'message_type'),
    )
    
    def to_dict(self, include_user=True):
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'message': self.message if not self.is_deleted else '[Message deleted]',
            'message_type': self.message_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'is_deleted': self.is_deleted,
            'message_metadata': self.message_metadata
        }
        
        if include_user and self.user:
            result['user'] = {
                'id': self.user.id,
                'name': self.user.name,
                'email': self.user.email,
                'role': self.user.role
            }
        
        return result


class ChatParticipant(db.Model):
    """
    Manages who can access each chat room
    Tracks participation, roles, and read status
    """
    __tablename__ = 'chat_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('task_chats.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # admin, member, viewer
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_read_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='chat_participations', lazy=True)
    
    # Indexes
    __table_args__ = (
        db.UniqueConstraint('chat_id', 'user_id', name='uq_chat_participant'),
        db.Index('idx_chat_participant_chat', 'chat_id'),
        db.Index('idx_chat_participant_user', 'user_id'),
    )
    
    def to_dict(self, include_user=True):
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_read_at': self.last_read_at.isoformat() if self.last_read_at else None,
            'is_active': self.is_active
        }
        
        if include_user and self.user:
            result['user'] = {
                'id': self.user.id,
                'name': self.user.name,
                'email': self.user.email,
                'role': self.user.role,
                'online': self.user.online
            }
        
        return result


class AIChat(db.Model):
    """
    Private 1-to-1 chat between user and AI assistant
    AI has access to group chat context for better assistance
    """
    __tablename__ = 'ai_chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # AI Context
    context_summary = db.Column(db.Text, nullable=True)  # Summary of group chat for AI
    last_sync_at = db.Column(db.DateTime, nullable=True)  # Last time group chat was synced
    
    # Relationships
    user = db.relationship('User', backref='ai_chats', lazy=True)
    task = db.relationship('Task', backref='ai_chats', lazy=True)
    messages = db.relationship('AIChatMessage', backref='ai_chat', lazy='dynamic', cascade='all, delete-orphan', order_by='AIChatMessage.created_at')
    
    # Indexes
    __table_args__ = (
        db.UniqueConstraint('user_id', 'task_id', name='uq_user_task_ai_chat'),
        db.Index('idx_ai_chat_user', 'user_id'),
        db.Index('idx_ai_chat_task', 'task_id'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'message_count': self.messages.count()
        }


class AIChatMessage(db.Model):
    """
    Messages in the AI assistant chat
    Tracks conversation history and AI performance metrics
    """
    __tablename__ = 'ai_chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    ai_chat_id = db.Column(db.Integer, db.ForeignKey('ai_chats.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI Metadata
    model = db.Column(db.String(50), nullable=True)  # AI model used
    tokens_used = db.Column(db.Integer, nullable=True)
    response_time = db.Column(db.Float, nullable=True)  # in seconds
    
    # Context tracking - references to group chat messages
    group_chat_context = db.Column(db.JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_ai_msg_chat', 'ai_chat_id'),
        db.Index('idx_ai_msg_role', 'role'),
        db.Index('idx_ai_msg_created', 'created_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'ai_chat_id': self.ai_chat_id,
            'role': self.role,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'model': self.model,
            'tokens_used': self.tokens_used,
            'response_time': self.response_time,
            'group_chat_context': self.group_chat_context
        }

