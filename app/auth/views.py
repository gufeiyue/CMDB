# coding: utf-8
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user
from . import auth
from ..models import Auth_user
from ..email import send_email
from .forms import LoginForm, RegistrationForm
from .. import db




@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        user = Auth_user.query.filter_by(email=form.email.data).first()
        password = user.password
        if user is not None and password == form.password.data:
            login_user(user, False)
            return redirect(request.args.get('next') or url_for('admin.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)



@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Auth_user(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                         is_superuser="0",
                         first_name="C",
                         last_name="mdb",
                         is_staff="0",
                         is_active="1",
                         date_joined="2017-04-06 14:24:23.098748")
        db.session.add(user)
        db.session.commit()
        #token = user.generate_confirmation_token()
        # send_email(user.email, 'Confirm Your Account',
        #            'auth/email/confirm', user=user, token=token)
        # flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('admin.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已退出登陆。', 'success')
    return redirect(url_for('auth.login'))
