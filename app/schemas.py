from marshmallow import Schema, fields, validate, ValidationError
import re


def validate_channel_id(value):
    """Validate channel ID format."""
    if not re.match(r'^[a-z0-9-]+$', value):
        raise ValidationError("Only lowercase letters, numbers, and hyphens allowed")
    return value


class UserRegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=100),
        load_only=True
    )
    display_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    avatar_url = fields.Url(allow_none=True)


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class ChannelCreateSchema(Schema):
    id = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=80), validate_channel_id]
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    description = fields.Str(
        validate=validate.Length(max=500),
        allow_none=True
    )
    category = fields.Str(
        required=True,
        validate=validate.OneOf([
            'True Crime', 'Comedy', 'Music Lab', 'Tech & Dev', 
            'Culture', 'Sports Room', 'General'
        ])
    )
    is_private = fields.Bool(missing=True)


class ChannelUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500), allow_none=True)
    category = fields.Str(validate=validate.OneOf([
        'True Crime', 'Comedy', 'Music Lab', 'Tech & Dev',
        'Culture', 'Sports Room', 'General'
    ]))
    is_private = fields.Bool()


class MessageCreateSchema(Schema):
    channel_id = fields.Str(required=True)
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=2000)
    )
    type = fields.Str(
        missing='text',
        validate=validate.OneOf(['text', 'image', 'episode-share'])
    )
    subtitle = fields.Str(validate=validate.Length(max=255), allow_none=True)
    image_url = fields.Url(allow_none=True)
    image_caption = fields.Str(validate=validate.Length(max=255), allow_none=True)


class MessageUpdateSchema(Schema):
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=2000)
    )


class PaginationSchema(Schema):
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=50, validate=validate.Range(min=1, max=100))
    sort = fields.Str(missing='created_at')
    order = fields.Str(missing='desc', validate=validate.OneOf(['asc', 'desc']))