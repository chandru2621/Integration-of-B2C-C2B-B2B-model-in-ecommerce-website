from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.requirement import Requirement
from models.proposal import Proposal
from models.requirement_message import RequirementMessage
from models.product import Product
from models.cart import Cart, CartItem
from forms.bulk_request_form import BulkRequestForm
from models.bulk_request import BulkRequest
from services.notification import NotificationService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'seller':
        return redirect(url_for('seller.dashboard'))
    else:
        return redirect(url_for('customer.dashboard'))

@main_bp.route('/requirements/new', methods=['GET', 'POST'])
@login_required
def new_requirement():
    if request.method == 'POST':
        req = Requirement(
            title=request.form['title'],
            description=request.form['description'],
            category=request.form['category'],
            quantity=int(request.form.get('quantity') or 0),
            budget=float(request.form.get('budget') or 0),
            requester_id=current_user.id
        )
        db.session.add(req)
        db.session.commit()
        flash('Requirement posted!', 'success')
        return redirect(url_for('main.my_requirements'))
    return render_template('requirements/new.html')

@main_bp.route('/requirements')
@login_required
def all_requirements():
    requirements = Requirement.query.filter_by(status='open').all()
    return render_template('requirements/list.html', requirements=requirements)

@main_bp.route('/my_requirements')
@login_required
def my_requirements():
    requirements = Requirement.query.filter_by(requester_id=current_user.id).all()
    return render_template('requirements/my_list.html', requirements=requirements)

@main_bp.route('/requirements/<int:req_id>', methods=['GET', 'POST'])
@login_required
def requirement_detail(req_id):
    req = Requirement.query.get_or_404(req_id)
    proposals = req.proposals
    messages = req.messages
    if request.method == 'POST' and current_user.id == req.requester_id:
        # requester can send a message
        msg = RequirementMessage(
            requirement_id=req.id,
            sender_id=current_user.id,
            content=request.form['content']
        )
        db.session.add(msg)
        db.session.commit()
        flash('Message sent.', 'success')
        return redirect(url_for('main.requirement_detail', req_id=req.id))
    return render_template('requirements/detail.html', req=req, proposals=proposals, messages=messages)

@main_bp.route('/requirements/<int:req_id>/propose', methods=['GET', 'POST'])
@login_required
def submit_proposal(req_id):
    req = Requirement.query.get_or_404(req_id)
    if request.method == 'POST':
        prop = Proposal(
            requirement_id=req.id,
            seller_id=current_user.id,
            price=float(request.form['price']),
            details=request.form['details']
        )
        db.session.add(prop)
        db.session.commit()
        flash('Proposal submitted!', 'success')
        return redirect(url_for('main.requirement_detail', req_id=req.id))
    return render_template('requirements/propose.html', req=req)

@main_bp.route('/proposals/<int:proposal_id>/message', methods=['POST'])
@login_required
def proposal_message(proposal_id):
    prop = Proposal.query.get_or_404(proposal_id)
    req = prop.requirement
    msg = RequirementMessage(
        requirement_id=req.id,
        proposal_id=prop.id,
        sender_id=current_user.id,
        content=request.form['content']
    )
    db.session.add(msg)
    db.session.commit()
    flash('Message sent.', 'success')
    return redirect(url_for('main.requirement_detail', req_id=req.id))

@main_bp.route('/bulk-request', methods=['GET', 'POST'])
def bulk_request():
    form = BulkRequestForm()
    if form.validate_on_submit():
        bulk_request = BulkRequest(
            organization_name=form.organization_name.data,
            organization_address=form.organization_address.data,
            contact_email=form.contact_email.data,
            contact_phone=form.contact_phone.data,
            product_category=form.product_category.data,
            quantity=form.quantity.data,
            requirements=form.requirements.data
        )
        db.session.add(bulk_request)
        db.session.commit()
        flash('Your bulk request has been submitted successfully! We will contact you shortly.', 'success')
        return redirect(url_for('main.bulk_request'))
    return render_template('bulk_request.html', form=form)

@main_bp.route('/submit-bulk-request', methods=['POST'])
def submit_bulk_request():
    form = BulkRequestForm()
    if form.validate_on_submit():
        bulk_request = BulkRequest(
            organization_name=form.organization_name.data,
            organization_address=form.organization_address.data,
            contact_email=form.contact_email.data,
            contact_phone=form.contact_phone.data,
            product_category=form.product_category.data,
            quantity=form.quantity.data,
            requirements=form.requirements.data
        )
        db.session.add(bulk_request)
        db.session.commit()
        flash('Your bulk request has been submitted successfully! We will contact you shortly.', 'success')
        return redirect(url_for('main.bulk_request'))
    return render_template('bulk_request.html', form=form)

@main_bp.route('/test-email')
@login_required
def test_email():
    try:
        # Send a test email to the current user
        NotificationService.send_email(
            current_user.email,
            "Test Email from EcoShop",
            """
            <html>
            <body>
                <h2>Test Email</h2>
                <p>This is a test email to verify that the email configuration is working correctly.</p>
                <p>If you're receiving this email, your email settings are properly configured!</p>
            </body>
            </html>
            """
        )
        flash('Test email sent successfully! Please check your inbox.', 'success')
    except Exception as e:
        flash(f'Error sending test email: {str(e)}', 'error')
    
    return redirect(url_for('main.index')) 