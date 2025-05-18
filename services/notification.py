from flask import current_app, flash
from flask_mail import Message
from extensions import mail, db
from models.user import User
from models.order import Order
from models.requirement import Requirement
from models.proposal import Proposal
from models.notification import Notification
from datetime import datetime

class NotificationService:
    @staticmethod
    def create_notification(user_id, title, message, notification_type, order_id=None):
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            order_id=order_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def send_email(to, subject, template):
        """Send an email"""
        try:
            msg = Message(
                subject,
                recipients=[to],
                html=template,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            # Create a notification instead
            flash('Unable to send email notification. Please check your email settings.', 'warning')

    @staticmethod
    def mark_as_read(notification_id):
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_user_notifications(user_id, unread_only=False):
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Notification.created_at.desc()).all()

    @staticmethod
    def send_flash(message, category='info'):
        """Send a flash message"""
        flash(message, category)

    @staticmethod
    def notify_order_confirmation(order):
        """Send order confirmation notification"""
        # Create in-app notification
        notification = NotificationService.create_notification(
            user_id=order.user_id,
            title="Order Confirmation",
            message=f"Your order #{order.id} has been confirmed.",
            notification_type="order_confirmation",
            order_id=order.id
        )
        
        # Try to send email
        email_template = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f9f9f9; }
                .order-details { margin: 20px 0; }
                .item { padding: 10px; border-bottom: 1px solid #ddd; }
                .total { font-size: 1.2em; font-weight: bold; margin-top: 20px; }
                .footer { text-align: center; margin-top: 20px; font-size: 0.9em; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Order Confirmation</h1>
                </div>
                <div class="content">
                    <p>Dear {customer_name},</p>
                    <p>Thank you for your order! We're excited to process your purchase.</p>
                    
                    <div class="order-details">
                        <h2>Order Details</h2>
                        <p><strong>Order ID:</strong> {order_id}</p>
                        <p><strong>Order Date:</strong> {order_date}</p>
                        <p><strong>Payment Method:</strong> {payment_method}</p>
                        <p><strong>Payment Status:</strong> {payment_status}</p>
                    </div>

                    <div class="order-details">
                        <h2>Shipping Information</h2>
                        <p>
                            {shipping_name}<br>
                            {shipping_address}<br>
                            {shipping_city}, {shipping_state} {shipping_zip}<br>
                            {shipping_country}
                        </p>
                    </div>

                    <div class="order-details">
                        <h2>Order Items</h2>
                        {items_html}
                        <div class="total">
                            <p>Total Amount: ${total_amount:.2f}</p>
                        </div>
                    </div>

                    <p>We will notify you when your order ships.</p>
                    
                    <div class="footer">
                        <p>Thank you for shopping with us!</p>
                        <p>If you have any questions, please contact our customer support.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Generate items HTML
        items_html = ""
        for item in order.items:
            items_html += f"""
            <div class="item">
                <p><strong>{item.product.name}</strong></p>
                <p>Quantity: {item.quantity}</p>
                <p>Price: ${item.price:.2f}</p>
                <p>Subtotal: ${item.price * item.quantity:.2f}</p>
            </div>
            """
        
        # Format email template
        formatted_email = email_template.format(
            customer_name=order.user.username,
            order_id=order.id,
            order_date=order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            shipping_name=order.shipping_name,
            shipping_address=order.shipping_address,
            shipping_city=order.shipping_city,
            shipping_state=order.shipping_state,
            shipping_zip=order.shipping_zip,
            shipping_country=order.shipping_country,
            items_html=items_html,
            total_amount=order.total_amount
        )
        
        # Send email
        NotificationService.send_email(
            to=order.user.email,
            subject=f"Order Confirmation - Order #{order.id}",
            template=formatted_email
        )
        
        # Send flash message
        NotificationService.send_flash(
            f"Order #{order.id} has been placed successfully!",
            'success'
        )

    @staticmethod
    def notify_shipping_update(order, shipping_status, tracking_number):
        """Create a notification for shipping status update"""
        message = f"Your order #{order.id} shipping status has been updated to {shipping_status}"
        if tracking_number:
            message += f" with tracking number: {tracking_number}"
        
        notification = Notification(
            user_id=order.user_id,
            message=message,
            order_id=order.id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(notification)
        db.session.commit()

    @staticmethod
    def notify_proposal_reply(requirement, proposal):
        """Send notification for C2B proposal reply"""
        email_template = """
        <h2>New Proposal for Your Requirement</h2>
        <p>You have received a new proposal for your requirement:</p>
        <ul>
            <li>Requirement: {requirement.title}</li>
            <li>Proposed Price: ${proposal.price:.2f}</li>
            <li>Seller: {proposal.seller.username}</li>
        </ul>
        <p>Details: {proposal.details}</p>
        """
        
        NotificationService.send_email(
            requirement.requester.email,
            "New Proposal Received",
            email_template.format(requirement=requirement, proposal=proposal)
        )
        
        NotificationService.send_flash(
            "A new proposal has been submitted for your requirement",
            'info'
        )

    @staticmethod
    def notify_payment_status(order, status):
        """Send payment status notification"""
        email_template = """
        <h2>Payment Status Update</h2>
        <p>Your payment for order #{order.id} has been updated:</p>
        <ul>
            <li>Status: {status}</li>
            <li>Amount: ${order.total_amount:.2f}</li>
        </ul>
        """
        
        NotificationService.send_email(
            order.user.email,
            f"Payment Status Update - Order #{order.id}",
            email_template.format(order=order, status=status)
        )
        
        NotificationService.send_flash(
            f"Payment status updated to {status}",
            'info'
        ) 