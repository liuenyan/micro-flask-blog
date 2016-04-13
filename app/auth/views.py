# -*- encoding: utf8 -*-

from flask import render_template, redirect, request, url_for, flash
from . import auth
from ..models import User
from flask.ext.login import login_user, login_required, logout_user, current_user
from .forms import LoginForm, ChangePasswordForm
from .. import moment
from .. import db

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名或密码无效')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'你已经登出')
    return redirect(url_for('main.index'))


@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash(u'密码已更新')
            return redirect(url_for('main.index'))
        else:
            flash(u'请输入正确的旧密码')
    return render_template('auth/change-password.html', form=form)
