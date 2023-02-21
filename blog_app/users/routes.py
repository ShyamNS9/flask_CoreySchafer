from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from blog_app import db, bcrypt
from blog_app.users.utils import save_picture, send_reset_email
from blog_app.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from blog_app.models import User, Post

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def registration_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pwd
        )
        db.session.add(user)
        db.session.commit()
        flash(message=f'Account created for {form.username.data}! You can now login', category='success')
        return redirect(url_for('users.login_page'))
    return render_template('register.html', title='Registration', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user=user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                pass
            flash(message=f'Login was Successful! Welcome {user.username}!', category='success')
            return redirect(next_page) if next_page else redirect(url_for('main.home_page'))
        else:
            flash(message='Login was Unsuccessful. Please check email and password.', category='danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout_page():
    logout_user()
    flash(message=f'Logout was Successful!', category='success')
    return redirect(url_for('main.home_page'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account_page():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account_page'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', form=form, title='Account', image_file=image_file)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', title='User Posts', posts=posts, user=user)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user=user)
        flash('An email has been sent with instruction to reset your password.', category='info')
        return redirect(url_for('users.login_page'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_page(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', category='warning')
        return redirect(url_for('users.reset_request_page'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pwd
        db.session.commit()
        flash(message=f'Your password has been updated! You can now login', category='success')
        return redirect(url_for('users.login_page'))
    return render_template('reset_token.html', title='Reset Password', form=form)
