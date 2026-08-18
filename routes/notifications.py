from flask import Blueprint, jsonify, session, request

from services.notification_service import NotificationService


notifications_bp = Blueprint(
    "notifications",
    __name__,
    url_prefix="/api/notifications",
)


def get_current_user_id():
    return session.get("user_id")


@notifications_bp.route("/", methods=["GET"])
def index():

    user_id = get_current_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Authentication required.",
        }), 401

    unread_only = (
        request.args.get("unread_only", "false").lower()
        == "true"
    )

    try:
        limit = int(request.args.get("limit", 20))
    except (TypeError, ValueError):
        limit = 20

    limit = max(1, min(limit, 100))

    notifications = NotificationService.get_for_user(
        user_id=user_id,
        limit=limit,
        unread_only=unread_only,
    )

    return jsonify({
        "success": True,
        "notifications": [
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "link": notification.link,
                "is_read": notification.is_read,
                "created_at": (
                    notification.created_at.isoformat()
                    if notification.created_at
                    else None
                ),
                "read_at": (
                    notification.read_at.isoformat()
                    if notification.read_at
                    else None
                ),
            }
            for notification in notifications
        ],
    })


@notifications_bp.route("/unread-count", methods=["GET"])
def unread_count():

    user_id = get_current_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Authentication required.",
        }), 401

    count = NotificationService.unread_count(user_id)

    return jsonify({
        "success": True,
        "unread_count": count,
    })


@notifications_bp.route(
    "/<int:notification_id>/read",
    methods=["POST"],
)
def mark_read(notification_id):

    user_id = get_current_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Authentication required.",
        }), 401

    notification = NotificationService.mark_read(
        notification_id=notification_id,
        user_id=user_id,
    )

    if notification is None:
        return jsonify({
            "success": False,
            "message": "Notification not found.",
        }), 404

    return jsonify({
        "success": True,
        "message": "Notification marked as read.",
    })


@notifications_bp.route(
    "/read-all",
    methods=["POST"],
)
def mark_all_read():

    user_id = get_current_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Authentication required.",
        }), 401

    count = NotificationService.mark_all_read(user_id)

    return jsonify({
        "success": True,
        "message": "Notifications marked as read.",
        "updated": count,
    })


@notifications_bp.route(
    "/<int:notification_id>",
    methods=["DELETE"],
)
def delete(notification_id):

    user_id = get_current_user_id()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Authentication required.",
        }), 401

    deleted = NotificationService.delete(
        notification_id=notification_id,
        user_id=user_id,
    )

    if not deleted:
        return jsonify({
            "success": False,
            "message": "Notification not found.",
        }), 404

    return jsonify({
        "success": True,
        "message": "Notification deleted.",
    })