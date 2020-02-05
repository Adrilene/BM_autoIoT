from flask_login import login_required, login_user, logout_user
from flask import Blueprint, redirect, url_for, g, render_template, request, flash, session

from forms.FormLogin import FormLogin
from forms.FormCreateUser import FormCreateUser

from utils.decorators import admin_required

from models.User import User, Role

from main import db

users_template = Blueprint('users_template', __name__, template_folder='templates')

@users_template.route('/users')
@admin_required
def users():

    users = User.query.all()

    return render_template('users.html', users=users)

@users_template.route('/login', methods=['GET', 'POST'])
def login():

    form_login = FormLogin()

    if ('type_form_login' in request.form and request.form[
        'type_form_login'] == 'login' and form_login.validate_on_submit()):
        user = User.query.filter_by(username=form_login.username_login.data).first()
        if (user and user.verify_password(form_login.password_login.data)):
            login_user(user, remember=True)
            return redirect(url_for('base_template.home'))
        else:
            flash("Failed to login. Incorrect username or password")
            return redirect(request.args.get('next') or request.referrer)

    return render_template('landing_page.html', form_login=form_login)

@users_template.route('/logout')
def logout():
    logout_user()
    session.pop('oauth_token', None)
    return redirect(url_for('users_template.login'))

@users_template.route('/create_user', methods=['GET', 'POST'])
@admin_required
def create_user():
    form_create_user = FormCreateUser()

    form_create_user.validate_on_submit()
    if(request.method == 'POST' and len(form_create_user.errors) <= 1):
        role = Role.query.filter_by(id=form_create_user.role.data).first()

        if(role):
            user = User()
            user.username = form_create_user.username.data
            user.password = form_create_user.password.data
            user.role = role

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('users_template.users'))
        else:
            flash('Error finding the correct Role', 'danger')

    roles = Role.query.all()
    form_create_user.role.choices = [(role.id, role.name) for role in roles]

    return render_template('user_create.html', form_create_user=form_create_user)

@users_template.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):

    user = User.query.get(id)

    if(user is None):
        flash('User do not exists', 'danger')
        return redirect(url_for('users_template.users'))


    form_create_user = FormCreateUser()

    form_create_user.validate_on_submit()
    if (request.method == 'POST' and len(form_create_user.errors) <= 1):
        role = Role.query.filter_by(id=form_create_user.role.data).first()

        if (role):
            user.username = form_create_user.username.data
            user.password = form_create_user.password.data
            user.role = role

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('users_template.users'))
        else:
            flash('Error finding the correct Role', 'danger')

    if(request.method == 'GET'):
        form_create_user.role.default = user.role.id
        form_create_user.process()
        form_create_user.username.data = user.username

    roles = Role.query.all()
    form_create_user.role.choices = [(role.id, role.name) for role in roles]

    return render_template('user_create.html', form_create_user=form_create_user)

@users_template.route('/delete/user/<int:id>')
@admin_required
def delete(id):

    selected_object = User.query.filter_by(id=id).first()

    if(selected_object and selected_object != g.user):
        db.session.delete(selected_object)
        db.session.commit()

        flash('User deleted successfully.', 'success')
        return redirect(url_for('users_template.users'))

    flash('Error deleting the User.', 'danger')
    return redirect(url_for('users_template.users'))