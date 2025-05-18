from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.requirement import Requirement
from models.proposal import Proposal
from extensions import db
from services.notification import NotificationService
from utils.decorators import admin_required

requirement_bp = Blueprint('requirement', __name__)

@requirement_bp.route('/<int:req_id>/propose', methods=['POST'])
@login_required
@admin_required
def submit_proposal(req_id):
    requirement = Requirement.query.get_or_404(req_id)
    
    price = float(request.form.get('price'))
    details = request.form.get('details')
    
    proposal = Proposal(
        requirement_id=req_id,
        admin_id=current_user.id,
        price=price,
        description=details
    )
    
    db.session.add(proposal)
    db.session.commit()
    
    # Send proposal notification
    NotificationService.notify_proposal_reply(requirement, proposal)
    
    flash('Proposal submitted successfully!', 'success')
    return redirect(url_for('requirement.view', req_id=req_id)) 