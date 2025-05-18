from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.order import Order, OrderItem
from models.cart import Cart, CartItem
from models.product import Product
from models.payment import Payment
from services.notification import NotificationService
from datetime import datetime
import pdfkit
from io import BytesIO
from models.return_request import Return

order_bp = Blueprint('order', __name__, url_prefix='/order')

@order_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if current_user.role != 'customer':
        flash('Only customers can place orders.', 'error')
        return redirect(url_for('main.index'))
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    # Check if all items are still in stock
    for item in cart.items:
        if item.quantity > item.product.stock:
            flash(f'Not enough stock available for {item.product.name}.', 'error')
            return redirect(url_for('cart.view_cart'))
    
    if request.method == 'POST':
        try:
            # Get payment method
            payment_method = request.form.get('payment_method', 'cod')
            
            # Validate required shipping information
            shipping_name = request.form.get('shipping_name')
            shipping_address = request.form.get('shipping_address')
            shipping_city = request.form.get('shipping_city')
            shipping_state = request.form.get('shipping_state')
            shipping_zip = request.form.get('shipping_zip')
            shipping_country = request.form.get('shipping_country')
            
            if not all([shipping_name, shipping_address, shipping_city, shipping_state, shipping_zip, shipping_country]):
                flash('Please fill in all shipping information.', 'error')
                return redirect(url_for('order.checkout'))
            
            # Create new order
            order = Order(
                user_id=current_user.id,
                total_amount=cart.total_amount,
                status='pending',
                shipping_name=shipping_name,
                shipping_address=shipping_address,
                shipping_city=shipping_city,
                shipping_state=shipping_state,
                shipping_zip=shipping_zip,
                shipping_country=shipping_country,
                payment_method=payment_method,
                payment_status='pending'
            )
            db.session.add(order)
            db.session.flush()  # Get the order ID without committing
            
            # Create order items and update product stock
            for cart_item in cart.items:
                # Verify stock again before creating order item
                if cart_item.quantity > cart_item.product.stock:
                    raise ValueError(f'Not enough stock available for {cart_item.product.name}')
                
                order_item = OrderItem(
                    order_id=order.id,  # Use order_id instead of order object
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                db.session.add(order_item)
                
                # Update product stock
                cart_item.product.stock -= cart_item.quantity
            
            # Clear the cart
            for item in cart.items:
                db.session.delete(item)
            
            # Commit all changes
            db.session.commit()
            
            # Create notification for order creation
            try:
                NotificationService.create_notification(
                    user_id=current_user.id,
                    title="Order Created",
                    message=f"Your order #{order.id} has been created successfully.",
                    notification_type="order_created",
                    order_id=order.id
                )
            except Exception as notification_error:
                print(f"Error creating notification: {str(notification_error)}")
                # Don't fail the order if notification fails
            
            if payment_method == 'cod':
                flash('Order placed successfully! Please prepare cash for delivery.', 'success')
            else:
                flash('Order placed successfully! Please proceed with payment.', 'success')
            
            return redirect(url_for('order.view_order', order_id=order.id))
            
        except ValueError as ve:
            db.session.rollback()
            flash(str(ve), 'error')
            return redirect(url_for('cart.view_cart'))
        except Exception as e:
            db.session.rollback()
            print(f"Error placing order: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            flash('Error placing order. Please try again.', 'error')
            return redirect(url_for('cart.view_cart'))
    
    return render_template('order/checkout.html', cart=cart)

@order_bp.route('/payment/<int:order_id>', methods=['GET'])
@login_required
def payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('You are not authorized to view this order.')
        return redirect(url_for('main.index'))
    return render_template('order/payment.html', order=order)

@order_bp.route('/payment/<int:order_id>/confirm', methods=['POST'])
@login_required
def confirm_payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('You are not authorized to process this payment.')
        return redirect(url_for('main.index'))
    
    try:
        payment_method = request.form.get('payment_method', 'card')
        
        if payment_method == 'card':
            card_number = request.form.get('card_number')
            expiry = request.form.get('expiry')
            cvv = request.form.get('cvv')
            card_name = request.form.get('card_name')
            
            if not all([card_number, expiry, cvv, card_name]):
                flash('Please fill in all card details.')
                return redirect(url_for('order.payment', order_id=order.id))
            
            # Update order status
            order.payment_method = 'card'
            order.payment_status = 'completed'
            order.status = 'processing'
            
            # Create payment record
            payment = Payment(
                order_id=order.id,
                amount=order.total_amount,
                payment_method='card',
                status='completed'
            )
            db.session.add(payment)
            
        else:  # Cash on Delivery
            order.payment_method = 'cod'
            order.payment_status = 'pending'
            order.status = 'pending'
            
            # Create payment record
            payment = Payment(
                order_id=order.id,
                amount=order.total_amount,
                payment_method='cod',
                status='pending'
            )
            db.session.add(payment)
        
        db.session.commit()
        
        # Create notification for payment
        NotificationService.create_notification(
            user_id=current_user.id,
            title="Payment Status Updated",
            message=f"Payment for order #{order.id} has been {order.payment_status}.",
            notification_type="payment_update",
            order_id=order.id
        )
        
        if payment_method == 'card':
            flash('Payment successful! Your order is being processed.')
        else:
            flash('Order placed successfully! Please prepare cash for delivery.')
        
        return redirect(url_for('order.view_order', order_id=order.id))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error processing payment: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        flash(f'Error processing payment: {str(e)}')
        return redirect(url_for('order.payment', order_id=order.id))

@order_bp.route('/orders')
@login_required
def list_orders():
    if current_user.role == 'admin':
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    return render_template('order/list.html', orders=orders)

@order_bp.route('/orders/<int:order_id>')
@login_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Check if user has permission to view this order
    if current_user.role != 'admin' and order.user_id != current_user.id:
        flash('You do not have permission to view this order.', 'error')
        return redirect(url_for('order.list_orders'))
    
    return render_template('order/view.html', order=order)

@order_bp.route('/orders/<int:order_id>/update', methods=['POST'])
@login_required
def update_order_status(order_id):
    if current_user.role != 'admin':
        flash('Only administrators can update order status.', 'error')
        return redirect(url_for('order.view_order', order_id=order_id))
    
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        flash('Invalid order status.', 'error')
        return redirect(url_for('order.view_order', order_id=order_id))
    
    order.status = new_status
    order.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        flash('Order status updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating order status.', 'error')
    
    return redirect(url_for('order.view_order', order_id=order_id))

@order_bp.route('/history')
@login_required
def history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('order/history.html', orders=orders)

@order_bp.route('/orders/history')
@login_required
def order_history():
    if current_user.role == 'customer':
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        return render_template('orders/customer_history.html', orders=orders)
    elif current_user.role == 'seller':
        # Get orders for seller's products
        orders = Order.query.join(OrderItem).join(Product).filter(
            Product.seller_id == current_user.id
        ).order_by(Order.created_at.desc()).all()
        return render_template('orders/seller_history.html', orders=orders)
    return redirect(url_for('main.index'))

@order_bp.route('/orders/<int:order_id>/invoice')
@login_required
def download_invoice(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not any(item.product.seller_id == current_user.id for item in order.items):
        flash('You are not authorized to view this invoice.', 'danger')
        return redirect(url_for('order.order_history'))
    
    try:
        # Generate HTML for invoice
        html = render_template('orders/invoice.html', order=order)
        
        # Try to convert HTML to PDF
        try:
            # Convert HTML to PDF
            pdf = pdfkit.from_string(html, False)
            
            # Create a BytesIO object to store the PDF
            pdf_bytes = BytesIO(pdf)
            pdf_bytes.seek(0)
            
            # Send the PDF as a file
            return send_file(
                pdf_bytes,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'invoice_{order.id}.pdf'
            )
        except OSError:
            # If wkhtmltopdf is not available, show the invoice in HTML format
            flash('PDF generation is not available. Showing invoice in HTML format.', 'warning')
            return render_template('orders/invoice.html', order=order)
            
    except Exception as e:
        flash('Error generating invoice. Please try again later.', 'danger')
        return redirect(url_for('order.order_history'))

@order_bp.route('/return/<int:order_id>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def request_return(order_id, item_id):
    order = Order.query.get_or_404(order_id)
    order_item = OrderItem.query.get_or_404(item_id)
    
    # Verify the order belongs to the current user
    if order.user_id != current_user.id:
        flash('You do not have permission to return items from this order.', 'error')
        return redirect(url_for('main.index'))
    
    # Check if the order is eligible for return (e.g., within return window)
    if not order.is_eligible_for_return():
        flash('This order is no longer eligible for returns.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        reason = request.form.get('reason')
        condition = request.form.get('condition')
        notes = request.form.get('notes')
        quantity = int(request.form.get('quantity', 1))
        
        # Validate quantity
        if quantity <= 0 or quantity > order_item.quantity:
            flash('Invalid return quantity.', 'error')
            return redirect(url_for('order.request_return', order_id=order_id, item_id=item_id))
        
        # Calculate refund amount (50% of original price)
        refund_amount = (order_item.price * quantity) * 0.5
        
        try:
            return_request = Return(
                order_id=order_id,
                order_item_id=item_id,
                quantity=quantity,
                reason=reason,
                condition=condition,
                refund_amount=refund_amount,
                notes=notes
            )
            db.session.add(return_request)
            db.session.commit()
            
            flash('Return request submitted successfully. You will receive 50% of the original price as a refund once approved.', 'success')
            return redirect(url_for('order.view_order', order_id=order_id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error submitting return request. Please try again.', 'error')
    
    return render_template('order/request_return.html', order=order, order_item=order_item)

@order_bp.route('/orders/<int:order_id>/mark_delivered', methods=['POST'])
@login_required
def mark_order_delivered(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Check if the order belongs to the current user
    if order.user_id != current_user.id:
        flash('You are not authorized to update this order.', 'danger')
        return redirect(url_for('order.order_history'))
    
    # Check if the order is in shipped status
    if order.status != 'shipped':
        flash('Only shipped orders can be marked as delivered.', 'warning')
        return redirect(url_for('order.order_history'))
    
    # Mark the order as delivered
    if order.mark_as_delivered():
        db.session.commit()
        flash('Order marked as delivered successfully.', 'success')
    else:
        flash('Unable to mark order as delivered.', 'danger')
    
    return redirect(url_for('order.order_history'))

@order_bp.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get filter parameters
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Base query
    query = Order.query
    
    # Apply filters
    if status:
        query = query.filter(Order.status == status)
    if date_from:
        query = query.filter(Order.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(Order.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
    
    # Get all orders with their items and users
    orders = query.order_by(Order.created_at.desc()).all()
    
    # Get unique statuses for filter dropdown
    statuses = db.session.query(Order.status).distinct().all()
    statuses = [status[0] for status in statuses]
    
    return render_template('orders/admin_orders.html', 
                         orders=orders, 
                         statuses=statuses,
                         current_status=status,
                         date_from=date_from,
                         date_to=date_to)

@order_bp.route('/admin/orders/<int:order_id>/update_status', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    if not current_user.is_admin:
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('main.index'))
    
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('order.admin_orders'))
    
    # Update order status
    order.status = new_status
    
    # If marking as delivered, set the delivered_at timestamp
    if new_status == 'delivered':
        order.delivered_at = datetime.utcnow()
    
    try:
        db.session.commit()
        flash(f'Order status updated to {new_status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating order status.', 'danger')
    
    return redirect(url_for('order.admin_orders'))

@order_bp.route('/admin/returns')
@login_required
def admin_returns():
    if not current_user.is_admin:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get filter parameters
    status = request.args.get('status')
    
    # Base query
    query = Return.query
    
    # Apply filters
    if status:
        query = query.filter(Return.status == status)
    
    # Get all return requests with their related data
    returns = query.order_by(Return.created_at.desc()).all()
    
    return render_template('orders/admin_returns.html', 
                         returns=returns,
                         current_status=status)

@order_bp.route('/admin/returns/<int:return_id>/process', methods=['POST'])
@login_required
def process_return_request(return_id):
    if not current_user.is_admin:
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('main.index'))
    
    return_request = Return.query.get_or_404(return_id)
    action = request.form.get('action')
    admin_notes = request.form.get('admin_notes')
    
    if action not in ['approve', 'reject']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('order.admin_returns'))
    
    try:
        if action == 'approve':
            # Process the return
            return_request.approve(current_user.id, admin_notes)
            
            # Update product stock
            product = return_request.order_item.product
            product.stock += return_request.quantity
            
            # Here you would typically process the refund
            # For now, we'll just mark it as approved
            flash('Return request approved. Refund will be processed.', 'success')
        else:
            return_request.reject(current_user.id, admin_notes)
            flash('Return request rejected.', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Error processing return request.', 'danger')
    
    return redirect(url_for('order.admin_returns'))

@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Check if the order belongs to the current user
    if order.user_id != current_user.id:
        flash('You are not authorized to cancel this order.', 'danger')
        return redirect(url_for('order.history'))
    
    # Check if the order can be cancelled (only pending orders can be cancelled)
    if order.status != 'pending':
        flash('Only pending orders can be cancelled.', 'warning')
        return redirect(url_for('order.history'))
    
    try:
        # Update order status
        order.status = 'cancelled'
        
        # Restore product stock
        for item in order.items:
            product = item.product
            product.stock += item.quantity
        
        db.session.commit()
        flash('Order cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error cancelling order. Please try again.', 'danger')
    
    return redirect(url_for('order.history')) 