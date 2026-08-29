from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..decorators import admin_required, get_current_user
from ..exceptions import NotFoundError, ValidationError
from ..extensions import db
from ..models import Channel, User, UserReport, now_utc
from ..serializers import channel_dict

moderation_bp = Blueprint("moderation", __name__, url_prefix="/api")


@moderation_bp.post("/reports")
@jwt_required()
def report_user():
    reporter = get_current_user()
    body = request.get_json(silent=True) or {}
    reported_user_id, reason = body.get("reportedUserId"), str(body.get("reason", "")).strip()
    if not reported_user_id or not reason:
        raise ValidationError("reportedUserId and reason are required")
    if reported_user_id == reporter.id or not db.session.get(User, reported_user_id):
        raise ValidationError("The reported user is invalid")
    report = UserReport(
        reporter_id=reporter.id,
        reported_user_id=reported_user_id,
        message_id=body.get("messageId"),
        reason=reason,
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({"id": str(report.id), "status": report.status.value}), 201


@moderation_bp.get("/admin/channels")
@jwt_required()
@admin_required
def admin_channels():
    return jsonify([channel_dict(channel) for channel in db.session.scalars(select(Channel)).all()])


@moderation_bp.get("/admin/reports")
@jwt_required()
@admin_required
def admin_reports():
    reports = db.session.scalars(
        select(UserReport)
        .options(selectinload(UserReport.reporter), selectinload(UserReport.reported_user))
        .order_by(UserReport.created_at.desc())
    ).all()
    return jsonify([
        {
            "id": str(report.id),
            "reason": report.reason,
            "status": report.status.value,
            "createdAt": report.created_at.isoformat(),
            "reporter": {"id": report.reporter.id, "name": report.reporter.display_name},
            "reportedUser": {
                "id": report.reported_user.id,
                "name": report.reported_user.display_name,
                "isBanned": report.reported_user.is_banned,
            },
        }
        for report in reports
    ])


@moderation_bp.patch("/admin/users/<user_id>/ban")
@jwt_required()
@admin_required
def ban_user(user_id):
    admin = get_current_user()
    user = db.session.get(User, user_id)
    if not user or user.id == admin.id:
        raise ValidationError("User cannot be banned")
    user.is_banned, user.banned_at = True, now_utc()
    db.session.commit()
    return jsonify({"id": user.id, "isBanned": True})


@moderation_bp.patch("/admin/users/<user_id>/unban")
@jwt_required()
@admin_required
def unban_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    user.is_banned, user.banned_at = False, None
    db.session.commit()
    return jsonify({"id": user.id, "isBanned": False})
