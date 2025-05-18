from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models.user import User
from models.order import Order, OrderItem
from models.requirement import Requirement
from models.proposal import Proposal
from models.requirement_message import RequirementMessage
from services.notifications import NotificationService
from datetime import datetime, timedelta
import json
from werkzeug.security import generate_password_hash
from models.return_request import Return
from models.bulk_request import BulkRequest

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    total_orders = Order.query.count()
    total_requirements = Requirement.query.count()
    total_returns = Return.query.count()
    total_bulk_requests = BulkRequest.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    recent_requirements = Requirement.query.order_by(Requirement.created_at.desc()).limit(5).all()
    recent_bulk_requests = BulkRequest.query.order_by(BulkRequest.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html',
                         total_orders=total_orders,
                         total_requirements=total_requirements,
                         total_returns=total_returns,
                         total_bulk_requests=total_bulk_requests,
                         recent_orders=recent_orders,
                         recent_requirements=recent_requirements,
                         recent_bulk_requests=recent_bulk_requests)

@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    if date_from:
        query = query.filter(Order.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(Order.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
    
    orders = query.order_by(Order.created_at.desc()).all()
    statuses = db.session.query(Order.status).distinct().all()
    statuses = [status[0] for status in statuses]
    
    return render_template('admin/orders.html',
                         orders=orders,
                         statuses=statuses,
                         current_status=status,
                         date_from=date_from,
                         date_to=date_to)

@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/view_order.html', order=order)

@admin_bp.route('/orders/<int:order_id>/update_status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin.orders'))
    
    order.status = new_status
    if new_status == 'delivered':
        order.delivered_at = datetime.utcnow()
    
    try:
        db.session.commit()
        flash(f'Order status updated to {new_status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating order status.', 'danger')
    
    return redirect(url_for('admin.orders'))

@admin_bp.route('/requirements')
@login_required
@admin_required
def manage_requirements():
    requirements = Requirement.query.order_by(Requirement.created_at.desc()).all()
    return render_template('admin/requirements.html', requirements=requirements)

@admin_bp.route('/requirements/<int:req_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_requirement_status(req_id):
    req = Requirement.query.get_or_404(req_id)
    req.status = 'closed' if req.status == 'open' else 'open'
    db.session.commit()
    flash(f'Requirement status updated successfully.', 'success')
    return redirect(url_for('admin.manage_requirements'))

@admin_bp.route('/reports')
@login_required
@admin_required
def manage_reports():
    reported_messages = RequirementMessage.query.filter_by(is_reported=True).all()
    return render_template('admin/reports.html', reported_messages=reported_messages)

@admin_bp.route('/reports/<int:message_id>/resolve', methods=['POST'])
@login_required
@admin_required
def resolve_report(message_id):
    message = RequirementMessage.query.get_or_404(message_id)
    message.is_reported = False
    db.session.commit()
    flash('Report resolved successfully.', 'success')
    return redirect(url_for('admin.manage_reports'))

@admin_bp.route('/returns')
@login_required
@admin_required
def returns():
    returns = Return.query.order_by(Return.created_at.desc()).all()
    return render_template('admin/returns.html', returns=returns)

@admin_bp.route('/returns/<int:return_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_return(return_id):
    return_request = Return.query.get_or_404(return_id)
    
    if return_request.status != 'pending':
        flash('This return request has already been processed.', 'error')
        return redirect(url_for('admin.returns'))
    
    return_request.status = 'approved'
    return_request.admin_notes = request.form.get('admin_notes')
    return_request.processed_at = datetime.utcnow()
    return_request.refund_status = 'completed'
    
    try:
        db.session.commit()
        flash('Return request approved and refund processed successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error processing refund. Please try again.', 'error')
    
    return redirect(url_for('admin.returns'))

@admin_bp.route('/returns/<int:return_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_return(return_id):
    return_request = Return.query.get_or_404(return_id)
    
    if return_request.status != 'pending':
        flash('This return request has already been processed.', 'error')
        return redirect(url_for('admin.returns'))
    
    rejection_reason = request.form.get('rejection_reason')
    if not rejection_reason:
        flash('Please provide a reason for rejection.', 'error')
        return redirect(url_for('admin.returns'))
    
    return_request.status = 'rejected'
    return_request.admin_notes = rejection_reason
    return_request.processed_at = datetime.utcnow()
    
    try:
        db.session.commit()
        flash('Return request rejected successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error rejecting return request. Please try again.', 'error')
    
    return redirect(url_for('admin.returns'))

@admin_bp.route('/bulk-requests')
@login_required
@admin_required
def bulk_requests():
    # Get all organization requests ordered by creation date
    bulk_requests = BulkRequest.query.order_by(BulkRequest.created_at.desc()).all()
    return render_template('admin/bulk_requests.html', bulk_requests=bulk_requests)

@admin_bp.route('/bulk-requests/<int:request_id>/update', methods=['POST'])
@login_required
@admin_required
def update_bulk_request(request_id):
    bulk_request = BulkRequest.query.get_or_404(request_id)
    action = request.form.get('action')
    
    if action == 'approve':
        bulk_request.status = 'approved'
        # Create notification for organization
        NotificationService.create_notification(
            email=bulk_request.email,
            title='Organization Request Approved',
            message=f'Your request for {bulk_request.quantity} units of {bulk_request.category} products ({bulk_request.condition}) has been approved. Our team will contact you shortly for payment and delivery details.',
            type='organization_request_update'
        )
    elif action == 'reject':
        bulk_request.status = 'rejected'
        # Create notification for organization
        NotificationService.create_notification(
            email=bulk_request.email,
            title='Organization Request Update',
            message=f'Your request for {bulk_request.quantity} units of {bulk_request.category} products ({bulk_request.condition}) could not be fulfilled at this time.',
            type='organization_request_update'
        )
    
    bulk_request.admin_notes = request.form.get('admin_notes')
    db.session.commit()
    
    flash(f'Organization request has been {action}d successfully.', 'success')
    return redirect(url_for('admin.bulk_requests')) 