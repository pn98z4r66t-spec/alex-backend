"""
File Storage Model
"""
from datetime import datetime
from . import db


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

