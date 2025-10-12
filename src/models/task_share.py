from datetime import datetime
from . import db

class TaskShare(db.Model):
    """Model for task sharing and access control"""
    __tablename__ = 'task_shares'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    shared_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    share_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    permission = db.Column(db.String(20), default='view')  # view, edit, admin
    expires_at = db.Column(db.DateTime, nullable=True)
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

