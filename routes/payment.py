from flask import Blueprint, jsonify, request, current_app, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models.order import Order
from models.payment import Payment
from extensions import db
import stripe
import os

payment_bp = Blueprint('payment', __name__)

# Initialize Stripe with your secret key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'your_stripe_test_key')

@payment_bp.route('/process/<int:order_id>', methods=['GET'])
@login_required
def process_payment(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Check if order belongs to current user
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if payment already exists
    if hasattr(order, 'payment') and order.payment:
        if order.payment.status == 'completed':
            flash('Payment has already been processed.', 'info')
            return redirect(url_for('order.view', order_id=order_id))
    
    # Determine if B2B or B2C based on user role
    is_b2b = current_user.role == 'business'
    
    return render_template('payment/process.html', 
                         order=order,
                         is_b2b=is_b2b,
                         stripe_public_key=os.getenv('STRIPE_PUBLIC_KEY', 'your_stripe_public_test_key'))

@payment_bp.route('/create-payment-intent/<int:order_id>', methods=['POST'])
@login_required
def create_payment_intent(order_id):
    order = Order.query.get_or_404(order_id)
    
    try:
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),  # Convert to cents
            currency='usd',
            metadata={
                'order_id': order_id,
                'customer_email': current_user.email
            }
        )
        
        return jsonify({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@payment_bp.route('/create-invoice/<int:order_id>', methods=['POST'])
@login_required
def create_invoice(order_id):
    if current_user.role != 'business':
        return jsonify({'error': 'Only business accounts can request invoices'}), 403
    
    order = Order.query.get_or_404(order_id)
    
    try:
        # Create a Stripe Customer if not exists
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={
                    'user_id': current_user.id
                }
            )
            current_user.stripe_customer_id = customer.id
            db.session.commit()
        
        # Create an invoice item
        invoice_item = stripe.InvoiceItem.create(
            customer=current_user.stripe_customer_id,
            amount=int(order.total_amount * 100),
            currency='usd',
            description=f'Order #{order.id}'
        )
        
        # Create the invoice
        invoice = stripe.Invoice.create(
            customer=current_user.stripe_customer_id,
            collection_method='send_invoice',
            days_until_due=30
        )
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method='invoice',
            stripe_invoice_id=invoice.id
        )
        db.session.add(payment)
        db.session.commit()
        
        # Send the invoice
        stripe.Invoice.send_invoice(invoice.id)
        
        return jsonify({
            'success': True,
            'invoice_id': invoice.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET', 'your_webhook_secret')
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400
    
    # Handle specific events
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        order_id = payment_intent.metadata.get('order_id')
        
        if order_id:
            order = Order.query.get(order_id)
            if order:
                # Update payment status
                payment = Payment.query.filter_by(order_id=order_id).first()
                if not payment:
                    payment = Payment(
                        order_id=order_id,
                        amount=order.total_amount,
                        payment_method='card',
                        stripe_payment_id=payment_intent.id
                    )
                    db.session.add(payment)
                
                payment.status = 'completed'
                order.status = 'paid'
                db.session.commit()
    
    elif event.type == 'invoice.paid':
        invoice = event.data.object
        payment = Payment.query.filter_by(stripe_invoice_id=invoice.id).first()
        
        if payment:
            payment.status = 'completed'
            payment.order.status = 'paid'
            db.session.commit()
    
    return jsonify({'status': 'success'}) 