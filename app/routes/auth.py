from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        location = request.form.get('location', '').strip()
        skills = request.form.get('skills', '').strip()
        user_type = request.form.get('user_type', 'seller')
        
        if not username or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 4:
            flash('Password must be at least 4 characters long.', 'danger')
            return redirect(url_for('auth.register'))
        
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists. Please try a different one.', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email, location=location, skills=skills, user_type=user_type)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Welcome to Mini Freelance. Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False
        
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with that email address. Please register first.', 'danger')
            return render_template('auth/login.html')
        
        if not user.check_password(password):
            flash('Incorrect password. Please try again.', 'danger')
            return render_template('auth/login.html')
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
