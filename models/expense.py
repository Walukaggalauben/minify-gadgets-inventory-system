from utils.timezone import utc_now_naive
from db import db


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    expense_number = db.Column(db.String(40), unique=True, nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False, default="Cash")
    reference = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now_naive)

    user = db.relationship("User", backref=db.backref("expenses", lazy=True))

    def __repr__(self):
        return f"<Expense {self.expense_number}>"
