from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.bulk_request import BulkRequest
from models.product import Product
from extensions import db

bulk_order_bp = Blueprint('bulk_order', __name__)

@bulk_order_bp.route('/bulk-order/<int:product_id>', methods=['GET', 'POST'])
@login_required
def create_bulk_order(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        organization_name = request.form.get('organization_name')
        
        bulk_request = BulkRequest(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity,
            organization_name=organization_name
        )
        
        db.session.add(bulk_request)
        db.session.commit()
        
        flash('Bulk order request submitted successfully!', 'success')
        return redirect(url_for('products.product_detail', product_id=product_id))
        
    return render_template('bulk_order/create.html', product=product)