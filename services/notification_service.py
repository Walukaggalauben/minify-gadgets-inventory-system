from datetime import datetime

from db import db
from models.notification import Notification


class NotificationService:

    @staticmethod
    def create(
        user_id,
        title,
        message,
        notification_type="info",
        link=None,
    ):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            is_read=False,
            created_at=utc_now_naive(),
        )

        db.session.add(notification)
        db.session.commit()

        return notification

    @staticmethod
    def get_for_user(
        user_id,
        limit=20,
        unread_only=False,
    ):
        query = Notification.query.filter_by(user_id=user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def unread_count(user_id):
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False,
        ).count()

    @staticmethod
    def mark_read(
        notification_id,
        user_id,
    ):
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id,
        ).first()

        if not notification:
            return None

        notification.mark_as_read()

        db.session.commit()

        return notification

    @staticmethod
    def mark_all_read(user_id):
        notifications = Notification.query.filter_by(
            user_id=user_id,
            is_read=False,
        ).all()

        now = utc_now_naive()

        for notification in notifications:
            notification.is_read = True
            notification.read_at = now

        db.session.commit()

        return len(notifications)

    @staticmethod
    def delete(
        notification_id,
        user_id,
    ):
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id,
        ).first()

        if not notification:
            return False

        db.session.delete(notification)
        db.session.commit()

        return True
