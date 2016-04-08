# -*- coding: utf8 -*-

from .. import db
from . import main
from flask import render_template, redirect, url_for, abort, flash
from flask.ext.login import login_required, current_user
from ..models import User
from .forms import EditProfileForm

@main.route("/")
@login_required
def index():
    return render_template("index.html")

@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template("user.html", user=user)


@main.route("/edit-profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u"个人资料已更新")
        return redirect(url_for('.user', username=current_user.username))
    form.full_name.data = current_user.full_name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit-profile.html", form=form)

