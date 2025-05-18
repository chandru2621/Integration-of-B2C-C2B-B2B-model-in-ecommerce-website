from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.product import Product
from forms.product import ProductSearchForm, ProductForm
from sqlalchemy import or_
from models.quote import Quote
from models.user import User
from utils.decorators import admin_required
from models.bulk_request import BulkRequest
from services.notification import NotificationService
from models.order import Order, OrderItem

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    query = Product.query.filter_by(is_active=True)
    
    # Apply filters
    category = request.args.get('category')
    search = request.args.get('search')
    
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    # Get paginated results
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Get unique categories for filter dropdown
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('products/list.html',
                         products=products,
                         categories=categories,
                         current_category=category,
                         search_term=search,
                         Product=Product)

@products_bp.route('/<int:product_id>')
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('products/view.html', product=product)

@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_product():
    if request.method == 'POST':
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=float(request.form.get('price')),
            stock=int(request.form.get('stock')),
            category=request.form.get('category'),
            subcategory=request.form.get('subcategory'),
            brand=request.form.get('brand'),
            sustainability_score=int(request.form.get('sustainability_score')),
            image_url=request.form.get('image_url'),
            materials=request.form.get('materials'),
            certifications=request.form.get('certifications'),
            minimum_quantity=int(request.form.get('minimum_quantity', 1)),
            bulk_price=float(request.form.get('bulk_price', 0)),
            admin_id=current_user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product created successfully!')
        return redirect(url_for('products.view_product', product_id=product.id))
    
    return render_template('products/create.html', Product=Product)

@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.category = request.form.get('category')
        product.subcategory = request.form.get('subcategory')
        product.brand = request.form.get('brand')
        product.sustainability_score = int(request.form.get('sustainability_score'))
        product.image_url = request.form.get('image_url')
        product.materials = request.form.get('materials')
        product.certifications = request.form.get('certifications')
        product.minimum_quantity = int(request.form.get('minimum_quantity', 1))
        product.bulk_price = float(request.form.get('bulk_price', 0))
        
        db.session.commit()
        
        flash('Product updated successfully!')
        return redirect(url_for('products.view_product', product_id=product.id))
    
    return render_template('products/edit.html', product=product, Product=Product)

@products_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting product. Please try again.', 'danger')
    
    return redirect(url_for('products.list_products'))

@products_bp.route('/products/add/<int:product_id>')
@login_required
def add_to_cart(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        quantity = request.args.get('quantity', 1, type=int)
        
        # Check if product is in stock
        if product.stock < quantity:
            return jsonify({'error': 'Not enough stock available'}), 400
        
        # Add to cart logic here
        # This is a placeholder - implement your cart logic
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error in add_to_cart: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@products_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    try:
        if current_user.role != 'seller':
            return redirect(url_for('main.index'))
        
        if request.method == 'POST':
            # Create new product
            product = Product(
                name=request.form['name'],
                description=request.form['description'],
                price=float(request.form['price']),
                stock=int(request.form['stock']),
                category=request.form['category'],
                seller_id=current_user.id,
                subcategory=request.form.get('subcategory'),
                brand=request.form.get('brand'),
                sustainability_score=int(request.form['sustainability_score']),
                materials=request.form.get('materials'),
                certifications=request.form.get('certifications'),
                image_url=request.form.get('image_url')
            )
            
            db.session.add(product)
            db.session.commit()
            
            return redirect(url_for('products.product_detail', product_id=product.id))
        
        return render_template('products/add.html', categories=Product.CATEGORIES)
    except Exception as e:
        print(f"Error in add_product: {str(e)}")
        return render_template('error.html', error="An error occurred while adding the product"), 500

@products_bp.route('/products/<int:product_id>/request_quote', methods=['GET', 'POST'])
@login_required
def request_quote(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        requested_quantity = int(request.form['requested_quantity'])
        requested_price = float(request.form['requested_price'])
        quote = Quote(product_id=product_id, buyer_id=current_user.id, requested_quantity=requested_quantity, requested_price=requested_price)
        db.session.add(quote)
        db.session.commit()
        flash('Quote request submitted.', 'success')
        return redirect(url_for('products.product_detail', product_id=product_id))
    return render_template('products/request_quote.html', product=product)

@products_bp.route('/my_quotes')
@login_required
def my_quotes():
    quotes = Quote.query.filter_by(buyer_id=current_user.id).all()
    return render_template('products/my_quotes.html', quotes=quotes)

@products_bp.route('/bulk-request')
def bulk_request():
    # Get all products with bulk discounts
    products = Product.query.filter(Product.bulk_discount.isnot(None)).all()
    # Get unique categories for the form
    categories = Product.CATEGORIES
    return render_template('products/bulk_request.html', products=products, categories=categories)

@products_bp.route('/submit-bulk-request', methods=['POST'])
def submit_bulk_request():
    try:
        bulk_request = BulkRequest(
            organization=request.form.get('organization'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            category=request.form.get('category'),
            quantity=int(request.form.get('quantity')),
            requirements=request.form.get('requirements'),
            condition=request.form.get('condition')  # Add condition field
        )
        
        db.session.add(bulk_request)
        db.session.commit()
        
        # Notify admin
        NotificationService.create_notification(
            user_id=1,  # Admin user ID
            title='New Bulk Request',
            message=f'New bulk request from {bulk_request.organization} for {bulk_request.quantity} units of {bulk_request.category} ({bulk_request.condition})',
            type='bulk_request',
            bulk_request_id=bulk_request.id
        )
        
        flash('Your bulk request has been submitted successfully! We will contact you shortly.', 'success')
        return redirect(url_for('products.bulk_request'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while submitting your request. Please try again.', 'error')
        return redirect(url_for('products.bulk_request'))

@products_bp.route('/place-bulk-order/<int:product_id>', methods=['GET', 'POST'])
def place_bulk_order(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        
        if request.method == 'POST':
            # Validate quantity
            quantity = int(request.form.get('quantity', 0))
            if quantity <= 0:
                flash('Please enter a valid quantity.', 'error')
                return redirect(url_for('products.place_bulk_order', product_id=product_id))
            
            if quantity > product.stock:
                flash(f'Only {product.stock} units available in stock.', 'error')
                return redirect(url_for('products.place_bulk_order', product_id=product_id))
            
            # Create bulk request
            bulk_request = BulkRequest(
                organization=request.form.get('organization'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                category=product.category,
                quantity=quantity,
                requirements=request.form.get('requirements'),
                condition=product.condition,
                status='pending'
            )
            
            db.session.add(bulk_request)
            db.session.commit()
            
            # Notify admin
            NotificationService.create_notification(
                user_id=1,  # Admin user ID
                title='New Bulk Order Request',
                message=f'New bulk order request from {bulk_request.organization} for {bulk_request.quantity} units of {product.name} ({product.condition})',
                type='bulk_request',
                bulk_request_id=bulk_request.id
            )
            
            flash('Your bulk order request has been submitted successfully! We will contact you shortly.', 'success')
            return redirect(url_for('products.bulk_request'))
        
        return render_template('products/place_bulk_order.html', product=product)
        
    except ValueError as e:
        flash('Invalid quantity entered. Please try again.', 'error')
        return redirect(url_for('products.place_bulk_order', product_id=product_id))
    except Exception as e:
        db.session.rollback()
        print(f"Error in place_bulk_order: {str(e)}")  # For debugging
        flash('An error occurred while placing your order. Please try again.', 'error')
        return redirect(url_for('products.place_bulk_order', product_id=product_id)) 