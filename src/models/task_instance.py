"""
Enhanced Task Instance Models with Native AI Integration
"""
from datetime import datetime
from ..models.models import db


class TaskInstance(db.Model):
    """
    Enhanced Task model with native AI integration
    Each task has its own AI assistant, files, logs, and subtasks
    """
    __tablename__ = 'task_instances'
    __table_args__ = (
        db.Index('idx_task_owner', 'owner_id'),
        db.Index('idx_task_status', 'status'),
        db.Index('idx_task_priority', 'priority'),
        db.Index('idx_task_created', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='todo')  # todo, in_progress, review, done
    priority = db.Column(db.String(50), default='medium')  # low, medium, high, urgent
    
    # Ownership and assignment
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Dates
    due_date = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI Integration
    ai_context = db.Column(db.Text)  # AI's understanding of the task
    ai_suggestions = db.Column(db.Text)  # Latest AI suggestions
    ai_enabled = db.Column(db.Boolean, default=True)
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_tasks')
    supervisor = db.relationship('User', foreign_keys=[supervisor_id], backref='supervised_tasks')
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_tasks')
    
    subtasks = db.relationship('SubTask', backref='parent_task', lazy='dynamic', cascade='all, delete-orphan')
    task_files = db.relationship('TaskFile', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    ai_logs = db.relationship('TaskAILog', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    collaborators = db.relationship('TaskCollaborator', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_details=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'owner_id': self.owner_id,
            'supervisor_id': self.supervisor_id,
            'assignee_id': self.assignee_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ai_enabled': self.ai_enabled,
        }
        
        if include_details:
            data.update({
                'owner': self.owner.to_dict() if self.owner else None,
                'supervisor': self.supervisor.to_dict() if self.supervisor else None,
                'assignee': self.assignee.to_dict() if self.assignee else None,
                'subtasks': [st.to_dict() for st in self.subtasks.all()],
                'files': [tf.to_dict() for tf in self.task_files.all()],
                'collaborators': [c.to_dict() for c in self.collaborators.all()],
                'ai_context': self.ai_context,
                'ai_suggestions': self.ai_suggestions,
            })
        
        return data


class SubTask(db.Model):
    """
    Subtasks within a task instance
    Shows what others are working on
    """
    __tablename__ = 'subtasks'
    __table_args__ = (
        db.Index('idx_subtask_parent', 'parent_task_id'),
        db.Index('idx_subtask_assignee', 'assignee_id'),
        db.Index('idx_subtask_status', 'status'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('task_instances.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='todo')  # todo, in_progress, done
    
    # Assignment
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Dates
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='subtasks')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_subtasks')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'parent_task_id': self.parent_task_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'assignee_id': self.assignee_id,
            'assignee': self.assignee.to_dict() if self.assignee else None,
            'created_by': self.created_by,
            'creator': self.creator.to_dict() if self.creator else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class TaskFile(db.Model):
    """
    Files attached to a task with privilege management
    """
    __tablename__ = 'task_files'
    __table_args__ = (
        db.Index('idx_taskfile_task', 'task_id'),
        db.Index('idx_taskfile_file', 'file_id'),
        db.Index('idx_taskfile_uploaded', 'uploaded_by'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task_instances.id'), nullable=False, index=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False, index=True)
    
    # Privilege management
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    is_reference = db.Column(db.Boolean, default=False)  # Reference file for AI
    
    # Metadata
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    file = db.relationship('File', backref='task_attachments')
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_task_files')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'file_id': self.file_id,
            'file': self.file.to_dict() if self.file else None,
            'uploaded_by': self.uploaded_by,
            'uploader': self.uploader.to_dict() if self.uploader else None,
            'is_reference': self.is_reference,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TaskAILog(db.Model):
    """
    AI interaction logs for a task
    Tracks all AI conversations and suggestions
    """
    __tablename__ = 'task_ai_logs'
    __table_args__ = (
        db.Index('idx_ailog_task', 'task_id'),
        db.Index('idx_ailog_user', 'user_id'),
        db.Index('idx_ailog_created', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task_instances.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Conversation
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    
    # Context
    files_referenced = db.Column(db.Text)  # JSON array of file IDs
    action_taken = db.Column(db.String(100))  # summarize, analyze, suggest, etc.
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='ai_interactions')
    
    def to_dict(self):
        """Convert to dictionary"""
        import json
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'files_referenced': json.loads(self.files_referenced) if self.files_referenced else [],
            'action_taken': self.action_taken,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TaskCollaborator(db.Model):
    """
    Collaborators on a task with privilege levels
    """
    __tablename__ = 'task_collaborators'
    __table_args__ = (
        db.Index('idx_collab_task', 'task_id'),
        db.Index('idx_collab_user', 'user_id'),
        db.UniqueConstraint('task_id', 'user_id', name='unique_task_collaborator'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task_instances.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Privileges
    role = db.Column(db.String(50), default='viewer')  # viewer, editor, admin
    can_edit_files = db.Column(db.Boolean, default=False)
    can_add_files = db.Column(db.Boolean, default=False)
    can_delete_files = db.Column(db.Boolean, default=False)
    can_use_ai = db.Column(db.Boolean, default=True)
    can_add_subtasks = db.Column(db.Boolean, default=False)
    
    # Metadata
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='collaborations')
    added_by_user = db.relationship('User', foreign_keys=[added_by], backref='added_collaborators')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'role': self.role,
            'permissions': {
                'can_edit_files': self.can_edit_files,
                'can_add_files': self.can_add_files,
                'can_delete_files': self.can_delete_files,
                'can_use_ai': self.can_use_ai,
                'can_add_subtasks': self.can_add_subtasks,
            },
            'added_by': self.added_by,
            'added_at': self.added_at.isoformat() if self.added_at else None,
        }
    
    @staticmethod
    def set_role_permissions(role):
        """Get default permissions for a role"""
        permissions = {
            'viewer': {
                'can_edit_files': False,
                'can_add_files': False,
                'can_delete_files': False,
                'can_use_ai': True,
                'can_add_subtasks': False,
            },
            'editor': {
                'can_edit_files': True,
                'can_add_files': True,
                'can_delete_files': False,
                'can_use_ai': True,
                'can_add_subtasks': True,
            },
            'admin': {
                'can_edit_files': True,
                'can_add_files': True,
                'can_delete_files': True,
                'can_use_ai': True,
                'can_add_subtasks': True,
            },
        }
        return permissions.get(role, permissions['viewer'])

