from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.forms.auth_forms import LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        # Allow checking either username or email
        user = User.query.filter((User.username == form.username.data) | (User.email == form.username.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.username}! Logged in as {user.role}.", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash("Invalid username/email or password.", "danger")
            
    return render_template('auth/login.html', form=form, title="Login")

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('auth.login'))
