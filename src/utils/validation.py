"""
Input validation utilities
"""
from marshmallow import Schema, fields, validate, ValidationError
from functools import wraps
from flask import request, jsonify
import bleach


def sanitize_string(text):
    """
    Sanitize string input to prevent XSS attacks
    """
    if not text:
        return text
    return bleach.clean(str(text), tags=[], strip=True)


def validate_request(schema_class):
    """
    Decorator to validate request data against a marshmallow schema
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            schema = schema_class()
            try:
                validated_data = schema.load(request.json or {})
                request.validated_data = validated_data
                return f(*args, **kwargs)
            except ValidationError as err:
                return jsonify({'errors': err.messages}), 400
        return decorated
    return decorator


# Validation Schemas

class TaskSchema(Schema):
    """Task validation schema"""
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Title is required'}
    )
    description = fields.Str(validate=validate.Length(max=1000))
    status = fields.Str(validate=validate.OneOf(['todo', 'in-progress', 'done']))
    urgent = fields.Bool()
    deadline = fields.DateTime(allow_none=True)
    assignee_id = fields.Int(required=True)
    supervisor_id = fields.Int(allow_none=True)
    collaborators = fields.List(fields.Int())


class EmailSchema(Schema):
    """Email validation schema"""
    sender = fields.Email(required=True)
    subject = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    body = fields.Str(validate=validate.Length(max=10000))
    priority = fields.Str(validate=validate.OneOf(['priority', 'normal']))
    user_id = fields.Int(required=True)


class MessageSchema(Schema):
    """Message validation schema"""
    sender_id = fields.Int(required=True)
    receiver_id = fields.Int(required=True)
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5000)
    )


class AIPromptSchema(Schema):
    """AI prompt validation schema"""
    message = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5000),
        error_messages={'required': 'Message is required'}
    )
    context = fields.Str(validate=validate.Length(max=10000))


class FileSchema(Schema):
    """Reference file validation schema"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    file_type = fields.Str(
        required=True,
        validate=validate.OneOf(['pdf', 'doc', 'docx', 'txt', 'xlsx', 'csv'])
    )
    content = fields.Str(validate=validate.Length(max=100000))


class LoginSchema(Schema):
    """Login validation schema"""
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=100)
    )


class RegisterSchema(Schema):
    """Registration validation schema"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=100)
    )
    role = fields.Str(validate=validate.OneOf(['Manager', 'Developer', 'Designer', 'Analyst']))




class TaskShareSchema(Schema):
    """Task sharing validation schema"""
    task_id = fields.Int(required=True, error_messages={'required': 'Task ID is required'})
    emails = fields.List(
        fields.Email(),
        validate=validate.Length(min=0, max=50),
        missing=[]
    )
    permission = fields.Str(
        validate=validate.OneOf(['view', 'edit', 'admin']),
        missing='view'
    )
    expires_in_days = fields.Int(
        validate=validate.Range(min=1, max=365),
        missing=30
    )
    status = fields.Str(validate=validate.OneOf(['todo', 'in-progress', 'done']))
    notes = fields.Str(validate=validate.Length(max=1000))


class EmailInviteSchema(Schema):
    """Email invitation validation schema"""
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})
    task_id = fields.Int(required=True, error_messages={'required': 'Task ID is required'})
    permission = fields.Str(
        validate=validate.OneOf(['view', 'edit', 'admin']),
        missing='view'
    )
    message = fields.Str(validate=validate.Length(max=500))

