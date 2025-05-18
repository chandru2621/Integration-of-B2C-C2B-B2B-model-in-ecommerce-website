from datetime import datetime
from extensions import db
from models.notification import Notification

class NotificationService:
    @staticmethod
    def notify_shipping_update(order, shipping_status, tracking_number=None):
        """Create a notification for shipping status update"""
        message = f"Order #{order.id} shipping status updated to {shipping_status}"
        if tracking_number:
            message += f". Tracking number: {tracking_number}"
        
        notification = Notification(
            user_id=order.user_id,
            order_id=order.id,
            message=message
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification 