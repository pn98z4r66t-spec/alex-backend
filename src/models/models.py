"""
Database models for Alex Backend
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """User model with authentication support"""
    __tablename__ = 'users'
    __table_args__ = (
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_online', 'online'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(50), nullable=False)
    online = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    tasks_assigned = db.relationship('Task', foreign_keys='Task.assignee_id', 
                                    backref='assignee', lazy='dynamic')
    tasks_supervised = db.relationship('Task', foreign_keys='Task.supervisor_id', 
                                      backref='supervisor', lazy='dynamic')
    emails = db.relationship('Email', backref='user', lazy='dynamic')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id',
                                   backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id',
                                       backref='receiver', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'online': self.online,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        return data


class Task(db.Model):
    """Task model with indexing for performance"""
    __tablename__ = 'tasks'
    __table_args__ = (
        db.Index('idx_task_status', 'status'),
        db.Index('idx_task_urgent', 'urgent'),
        db.Index('idx_task_assignee', 'assignee_id'),
        db.Index('idx_task_deadline', 'deadline'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='todo', index=True)
    urgent = db.Column(db.Boolean, default=False, index=True)
    deadline = db.Column(db.DateTime, index=True)
    
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    collaborators = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_relations=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'urgent': self.urgent,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'assignee_id': self.assignee_id,
            'supervisor_id': self.supervisor_id,
            'collaborators': self.collaborators.split(',') if self.collaborators else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            data['assignee'] = self.assignee.to_dict() if self.assignee else None
            data['supervisor'] = self.supervisor.to_dict() if self.supervisor else None
        
        return data


class Email(db.Model):
    """Email model with indexing"""
    __tablename__ = 'emails'
    __table_args__ = (
        db.Index('idx_email_priority', 'priority'),
        db.Index('idx_email_read', 'read'),
        db.Index('idx_email_user', 'user_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text)
    priority = db.Column(db.String(20), default='normal', index=True)
    read = db.Column(db.Boolean, default=False, index=True)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'sender': self.sender,
            'subject': self.subject,
            'body': self.body,
            'priority': self.priority,
            'read': self.read,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'user_id': self.user_id
        }


class ReferenceFile(db.Model):
    """Reference file model"""
    __tablename__ = 'reference_files'
    __table_args__ = (
        db.Index('idx_file_type', 'file_type'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(10), nullable=False, index=True)
    file_path = db.Column(db.String(500))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'file_type': self.file_type,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Message(db.Model):
    """Message model for team communication"""
    __tablename__ = 'messages'
    __table_args__ = (
        db.Index('idx_message_sender', 'sender_id'),
        db.Index('idx_message_receiver', 'receiver_id'),
        db.Index('idx_message_read', 'read'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, include_users=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_users:
            data['sender'] = self.sender.to_dict() if self.sender else None
            data['receiver'] = self.receiver.to_dict() if self.receiver else None
        
        return data




class TaskShare(db.Model):
    """Model for task sharing and access control via email links"""
    __tablename__ = 'task_shares'
    __table_args__ = (
        db.Index('idx_share_token', 'share_token'),
        db.Index('idx_share_task', 'task_id'),
        db.Index('idx_share_expires', 'expires_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    shared_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    share_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    permission = db.Column(db.String(20), default='view')  # view, edit, admin
    expires_at = db.Column(db.DateTime, nullable=True, index=True)
    access_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, nullable=True)
    revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    task = db.relationship('Task', backref=db.backref('shares', lazy='dynamic'))
    sharer = db.relationship('User', foreign_keys=[shared_by])
    
    def __repr__(self):
        return f'<TaskShare {self.share_token} for Task {self.task_id}>'
    
    def is_valid(self):
        """Check if share link is still valid"""
        if self.revoked:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'shared_by': self.shared_by,
            'share_token': self.share_token,
            'permission': self.permission,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'revoked': self.revoked,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }




class File(db.Model):
    """Model for file storage and management"""
    __tablename__ = 'files'
    __table_args__ = (
        db.Index('idx_file_uploader', 'uploaded_by'),
        db.Index('idx_file_category', 'category'),
        db.Index('idx_file_task', 'task_id'),
        db.Index('idx_file_hash', 'file_hash'),
        db.Index('idx_file_public', 'is_public'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    mime_type = db.Column(db.String(100))
    file_hash = db.Column(db.String(64), index=True)  # SHA256 hash
    category = db.Column(db.String(50), index=True)  # images, documents, etc.
    thumbnail_path = db.Column(db.String(500))
    description = db.Column(db.Text)
    extracted_text = db.Column(db.Text)  # For AI processing
    
    # Relationships
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True, index=True)
    
    # Access control
    is_public = db.Column(db.Boolean, default=False, index=True)
    
    # Metadata
    download_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_files')
    task = db.relationship('Task', foreign_keys=[task_id], backref='files')
    
    def __repr__(self):
        return f'<File {self.filename}>'
    
    def to_dict(self, include_uploader=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_size_formatted': self.format_file_size(),
            'mime_type': self.mime_type,
            'category': self.category,
            'description': self.description,
            'has_thumbnail': self.thumbnail_path is not None,
            'has_extracted_text': self.extracted_text is not None,
            'is_public': self.is_public,
            'download_count': self.download_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'uploaded_by': self.uploaded_by,
            'task_id': self.task_id
        }
        
        if include_uploader and self.uploader:
            data['uploader'] = {
                'id': self.uploader.id,
                'name': self.uploader.name,
                'email': self.uploader.email
            }
        
        return data
    
    def format_file_size(self):
        """Format file size in human-readable format"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

