from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.cart import Cart, CartItem
from models.product import Product

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
@login_required
def view_cart():
    if current_user.role != 'customer':
        flash('Only customers can view cart.', 'error')
        return redirect(url_for('main.index'))
    
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return render_template('cart/view.html', cart=cart)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    if current_user.role != 'customer':
        flash('Only customers can add items to cart.', 'error')
        return redirect(url_for('products.view_product', product_id=product_id))
    
    try:
        product = Product.query.get_or_404(product_id)
        quantity = int(request.form.get('quantity', 1))
        
        if quantity <= 0:
            flash('Quantity must be greater than 0.', 'error')
            return redirect(url_for('products.view_product', product_id=product_id))
        
        if quantity > product.stock:
            flash('Not enough stock available.', 'error')
            return redirect(url_for('products.view_product', product_id=product_id))
        
        # Get or create cart
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
        
        # Check if product already in cart
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if cart_item:
            # Update quantity if product already in cart
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                flash('Not enough stock available.', 'error')
                return redirect(url_for('products.view_product', product_id=product_id))
            cart_item.quantity = new_quantity
        else:
            # Add new item to cart
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
        flash('Product added to cart successfully!', 'success')
        
    except ValueError:
        flash('Invalid quantity value.', 'error')
        return redirect(url_for('products.view_product', product_id=product_id))
    except Exception as e:
        db.session.rollback()
        flash('Error adding product to cart. Please try again.', 'error')
        return redirect(url_for('products.view_product', product_id=product_id))
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    if current_user.role != 'customer':
        flash('Only customers can update cart.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    try:
        cart_item = CartItem.query.get_or_404(item_id)
        if cart_item.cart.user_id != current_user.id:
            flash('Unauthorized access.', 'error')
            return redirect(url_for('cart.view_cart'))
        
        quantity = int(request.form.get('quantity', 1))
        if quantity <= 0:
            flash('Quantity must be greater than 0.', 'error')
            return redirect(url_for('cart.view_cart'))
        
        if quantity > cart_item.product.stock:
            flash('Not enough stock available.', 'error')
            return redirect(url_for('cart.view_cart'))
        
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart updated successfully!', 'success')
        
    except ValueError:
        flash('Invalid quantity value.', 'error')
    except Exception as e:
        db.session.rollback()
        flash('Error updating cart. Please try again.', 'error')
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    if current_user.role != 'customer':
        flash('Only customers can remove items from cart.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    try:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error removing item from cart.', 'error')
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        flash('Cart cleared successfully!', 'success')
    return redirect(url_for('cart.view_cart')) 