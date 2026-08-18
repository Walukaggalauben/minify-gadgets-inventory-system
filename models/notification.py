from db import db
from utils.timezone import utc_now_naive


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )

    title = db.Column(db.String(150), nullable=False)

    message = db.Column(db.Text, nullable=False)

    notification_type = db.Column(db.String(50), nullable=False, default="info")

    link = db.Column(db.String(255), nullable=True)

    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)

    created_at = db.Column(
        db.DateTime, nullable=False, default=utc_now_naive, index=True
    )

    read_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref=db.backref("notifications", lazy=True))

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = utc_now_naive()

    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"
