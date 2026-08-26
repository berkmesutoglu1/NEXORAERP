from datetime import datetime
from app import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False) # CRITICAL_STOCK, EXPIRING_LOT, PENDING_SHIPMENT, OVERDUE_PAYMENT, SYSTEM
    level = db.Column(db.String(20), default='info')    # danger, warning, info, success
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Notification {self.title} - Level:{self.level}>'
