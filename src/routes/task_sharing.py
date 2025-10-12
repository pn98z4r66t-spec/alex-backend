from flask import Blueprint, request, jsonify
import secrets
import string
from datetime import datetime, timedelta
from flask_jwt_extended import get_jwt_identity
from ..models.models import db, Task, User, TaskShare
from ..middleware.auth import token_required
from ..utils.validation import (
    validate_request,
    TaskShareSchema,
    SharedTaskUpdateSchema,
    sanitize_string,
)
from ..utils.errors import APIError, ValidationError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

task_sharing_bp = Blueprint('task_sharing', __name__)

def generate_share_token(length=32, max_attempts=5):
    """Generate a secure, unique random token for task sharing"""
    alphabet = string.ascii_letters + string.digits

    for _ in range(max_attempts):
        token = ''.join(secrets.choice(alphabet) for _ in range(length))
        if not TaskShare.query.filter_by(share_token=token).first():
            return token

    raise APIError('Unable to generate unique share token', 500)

def send_task_invitation_email(recipient_email, task_title, share_link, sender_name):
    """Send task invitation email"""
    try:
        # Email configuration from environment variables
        smtp_server = os.getenv('SMTP_SERVER', 'localhost')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        from_email = os.getenv('FROM_EMAIL', 'noreply@alex.local')
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Task Assignment: {task_title}'
        msg['From'] = from_email
        msg['To'] = recipient_email
        
        # HTML email body
        html = f"""
        <html>
          <head>
            <style>
              body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
              .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
              .header {{ background-color: #000; color: #fff; padding: 20px; text-align: center; }}
              .content {{ background-color: #f9f9f9; padding: 30px; }}
              .button {{ display: inline-block; padding: 12px 30px; background-color: #000; 
                        color: #fff; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
              .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
          </head>
          <body>
            <div class="container">
              <div class="header">
                <h1>✨ Alex AI Workspace</h1>
              </div>
              <div class="content">
                <h2>You've been assigned a task!</h2>
                <p><strong>{sender_name}</strong> has assigned you the following task:</p>
                <h3>{task_title}</h3>
                <p>Click the button below to access your AI-enabled task board:</p>
                <a href="{share_link}" class="button">Open Task Board</a>
                <p style="margin-top: 30px; font-size: 14px; color: #666;">
                  Or copy and paste this link into your browser:<br>
                  <code>{share_link}</code>
                </p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <h4>What you can do:</h4>
                <ul>
                  <li>✅ View task details and progress</li>
                  <li>🤖 Get AI assistance for the task</li>
                  <li>💬 Collaborate with team members</li>
                  <li>📊 Track task status in real-time</li>
                </ul>
              </div>
              <div class="footer">
                <p>This is an automated message from Alex AI Workspace</p>
                <p>If you believe you received this email in error, please ignore it.</p>
              </div>
            </div>
          </body>
        </html>
        """
        
        # Plain text version
        text = f"""
        Alex AI Workspace - Task Assignment
        
        You've been assigned a task!
        
        {sender_name} has assigned you: {task_title}
        
        Access your AI-enabled task board here:
        {share_link}
        
        What you can do:
        - View task details and progress
        - Get AI assistance for the task
        - Collaborate with team members
        - Track task status in real-time
        
        ---
        This is an automated message from Alex AI Workspace
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        if smtp_username and smtp_password:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            # For development: just log the email
            print(f"[DEV MODE] Email would be sent to {recipient_email}")
            print(f"Share link: {share_link}")
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@task_sharing_bp.route('/share', methods=['POST'])
@token_required
@validate_request(TaskShareSchema)
def share_task():
    """Create a shareable link for a task and optionally send email invitations"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            raise APIError('Authentication required', 401)

        current_user = User.query.get(user_id)
        if not current_user:
            raise APIError('User not found', 401)

        data = getattr(request, 'validated_data', None) or request.get_json() or {}
        task_id = data.get('task_id')
        emails = data.get('emails', [])  # List of email addresses
        if emails:
            # Deduplicate emails in a case-insensitive manner while preserving order
            seen_emails = set()
            unique_emails = []
            for email in emails:
                key = email.lower()
                if key not in seen_emails:
                    seen_emails.add(key)
                    unique_emails.append(email)
            emails = unique_emails
        permission = data.get('permission', 'view')  # view, edit, or admin
        expires_in_days = data.get('expires_in_days', 30)
        
        # Get the task
        task = Task.query.get(task_id)
        if not task:
            raise APIError('Task not found', 404)
        
        # Check if user has permission to share
        if current_user.id not in {task.assignee_id, task.supervisor_id}:
            raise APIError('You do not have permission to share this task', 403)
        
        # Generate unique share token
        share_token = generate_share_token()
        
        # Calculate expiration date
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create task share record
        task_share = TaskShare(
            task_id=task_id,
            shared_by=current_user.id,
            share_token=share_token,
            permission=permission,
            expires_at=expires_at
        )
        
        db.session.add(task_share)
        db.session.commit()
        
        # Generate share link
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        share_link = f"{base_url}/task/{share_token}"
        
        # Send email invitations
        sent_emails = []
        failed_emails = []
        
        for email in emails:
            success = send_task_invitation_email(
                recipient_email=email,
                task_title=task.title,
                share_link=share_link,
                sender_name=current_user.name
            )
            if success:
                sent_emails.append(email)
            else:
                failed_emails.append(email)
        
        return jsonify({
            'message': 'Task shared successfully',
            'share_token': share_token,
            'share_link': share_link,
            'permission': permission,
            'expires_at': expires_at.isoformat(),
            'emails_sent': sent_emails,
            'emails_failed': failed_emails
        }), 201
        
    except APIError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise APIError(f'Error sharing task: {str(e)}', 500)

@task_sharing_bp.route('/access/<share_token>', methods=['GET'])
def access_shared_task(share_token):
    """Access a shared task using the share token (no authentication required)"""
    try:
        # Find the task share
        task_share = TaskShare.query.filter_by(share_token=share_token).first()
        
        if not task_share:
            raise APIError('Invalid or expired share link', 404)
        
        # Check if expired
        if task_share.expires_at and task_share.expires_at < datetime.utcnow():
            raise APIError('This share link has expired', 410)
        
        # Check if revoked
        if task_share.revoked:
            raise APIError('This share link has been revoked', 403)
        
        # Get the task
        task = Task.query.get(task_share.task_id)
        if not task:
            raise APIError('Task not found', 404)
        
        # Update access count and last accessed
        task_share.access_count += 1
        task_share.last_accessed = datetime.utcnow()
        db.session.commit()
        
        # Get shared by user info
        shared_by_user = User.query.get(task_share.shared_by)
        
        return jsonify({
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'urgent': task.urgent,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None
            },
            'share_info': {
                'permission': task_share.permission,
                'shared_by': shared_by_user.name if shared_by_user else 'Unknown',
                'shared_at': task_share.created_at.isoformat() if task_share.created_at else None,
                'expires_at': task_share.expires_at.isoformat() if task_share.expires_at else None,
                'access_count': task_share.access_count
            }
        }), 200

    except APIError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise APIError(f'Error accessing shared task: {str(e)}', 500)

@task_sharing_bp.route('/update/<share_token>', methods=['PUT'])
@validate_request(SharedTaskUpdateSchema)
def update_shared_task(share_token):
    """Update a shared task (requires edit or admin permission)"""
    try:
        data = getattr(request, 'validated_data', None) or {}

        if not data:
            raise ValidationError('No update fields provided')

        # Find the task share
        task_share = TaskShare.query.filter_by(share_token=share_token).first()

        if not task_share or task_share.revoked:
            raise APIError('Invalid or revoked share link', 403)
        
        if task_share.expires_at and task_share.expires_at < datetime.utcnow():
            raise APIError('This share link has expired', 410)
        
        # Check permission
        if task_share.permission not in ['edit', 'admin']:
            raise APIError('You do not have permission to edit this task', 403)
        
        # Get the task
        task = Task.query.get(task_share.task_id)
        if not task:
            raise APIError('Task not found', 404)
        
        # Update allowed fields
        updated = False

        if 'status' in data:
            task.status = data['status']
            updated = True

        if 'description' in data:
            if task_share.permission != 'admin':
                raise APIError('You do not have permission to edit this task description', 403)
            task.description = sanitize_string(data['description'])
            updated = True

        if not updated:
            raise ValidationError('No valid fields to update')

        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None
            }
        }), 200

    except APIError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise APIError(f'Error updating task: {str(e)}', 500)

@task_sharing_bp.route('/revoke/<share_token>', methods=['DELETE'])
@token_required
def revoke_share(share_token):
    """Revoke a share link"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            raise APIError('Authentication required', 401)

        current_user = User.query.get(user_id)
        if not current_user:
            raise APIError('User not found', 401)

        task_share = TaskShare.query.filter_by(share_token=share_token).first()

        if not task_share:
            raise APIError('Share link not found', 404)

        # Check if user has permission to revoke
        if task_share.shared_by != current_user.id:
            raise APIError('You do not have permission to revoke this share link', 403)

        task_share.revoked = True
        db.session.commit()

        return jsonify({
            'message': 'Share link revoked successfully'
        }), 200

    except APIError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise APIError(f'Error revoking share: {str(e)}', 500)

@task_sharing_bp.route('/list/<int:task_id>', methods=['GET'])
@token_required
def list_task_shares(task_id):
    """List all share links for a task"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            raise APIError('Authentication required', 401)

        current_user = User.query.get(user_id)
        if not current_user:
            raise APIError('User not found', 401)

        task = Task.query.get(task_id)
        if not task:
            raise APIError('Task not found', 404)

        if current_user.id not in {task.assignee_id, task.supervisor_id}:
            raise APIError('You do not have permission to view shares for this task', 403)
        
        shares = TaskShare.query.filter_by(task_id=task_id).all()
        
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        
        return jsonify({
            'shares': [{
                'share_token': share.share_token,
                'share_link': f"{base_url}/task/{share.share_token}",
                'permission': share.permission,
                'created_at': share.created_at.isoformat() if share.created_at else None,
                'expires_at': share.expires_at.isoformat() if share.expires_at else None,
                'access_count': share.access_count,
                'last_accessed': share.last_accessed.isoformat() if share.last_accessed else None,
                'revoked': share.revoked
            } for share in shares]
        }), 200
        
    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f'Error listing shares: {str(e)}', 500)

