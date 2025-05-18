from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.user import User
from forms.auth import LoginForm, RegistrationForm
from flask import Blueprint, redirect, url_for, flash, session
from flask_login import logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account is inactive. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        session['user_id'] = user.id
        session['user_role'] = user.role
        
        flash('Login successful!', 'success')
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Automatically log in the user after registration
            login_user(user)
            flash('Registration successful! Welcome to our store.', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            print(f"Registration error: {str(e)}")
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    # Clear any custom session data
    session.clear()
    # Logout the user
    logout_user()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Update user information
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        
        # Handle password change if provided
        new_password = request.form.get('new_password')
        if new_password:
            if new_password != request.form.get('confirm_password'):
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('auth.profile'))
            current_user.set_password(new_password)
        
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'danger')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')